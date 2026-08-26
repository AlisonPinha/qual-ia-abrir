// POST /api/cakto: o webhook da Cakto vira `Purchase` na API de Conversões do Meta.
//
// Por que existe. A venda de 19/08 entrou paga e o pixel ficou com zero `Purchase`: em 14
// dias chegaram 115 PageView, 83 ViewContent, 22 InitiateCheckout e nenhuma compra. Não é
// configuração torta, é estrutural. O Pix é pago FORA do navegador: a pessoa sai do
// checkout, paga no app do banco e nunca volta à página, então evento de navegador não tem
// como disparar. Em low ticket, onde quase tudo sai no Pix, isso deixa o Meta sem o único
// sinal que importa, e campanha otimizada para compra não tem o que aprender.
//
// O caminho é do servidor: a Cakto chama aqui quando a compra é aprovada, e daqui o evento
// vai para a Graph API já com os dados do comprador com hash.
//
// O mesmo evento também libera a entrega. O pedido é gravado para que o link fixo enviado
// pela própria Cakto consiga validar claim, e-mail e telefone. Reembolso ou chargeback revogam
// a sessão na próxima requisição. Falhar aqui não impede o CAPI nem provoca reenvio infinito.

import {
  normalizarPedido,
  registrarCompra,
  revogarPedido,
} from "./_access.mjs";

export const config = { maxDuration: 30 };

const PIXEL = "827402089420392";
const API = "v21.0";
const SITE = "https://diagnostico.noahai.com.br";
const LIMITE_CORPO = 20000;
const LIMITE_PLANILHA_MS = 8000;

// O que a Cakto manda quando a cobrança é criada e ainda não foi paga. Não vira Purchase:
// contar aqui é exatamente o ROAS mentiroso que os toggles do painel evitam. Fica listado
// porque é o gatilho da recuperação por WhatsApp, que entra quando existir número para ela.
const AGUARDANDO = ["pix_gerado", "boleto_gerado", "picpay_gerado", "checkout_abandonment"];
const REVOGAR = new Set(["refund", "chargeback"]);

// Status que contradizem uma compra aprovada. A lista é NEGATIVA de propósito: exigir
// `status === "paid"` faria a venda sumir no dia em que a Cakto passar a escrever
// "approved", e perder venda é pior do que deixar passar um status estranho.
const NAO_E_VENDA = ["refunded", "chargeback", "chargedback", "canceled", "cancelled",
                     "refused", "waiting_payment", "pending"];

// O payload de exemplo do painel da Cakto, que é o que o botão "Testar" dispara. Sem esta
// guarda, um clique ali vira uma venda de mentira no pixel, que entra no aprendizado da
// campanha e no relatório para sempre. Os dois valores saem do modelo mostrado no painel.
const EXEMPLO_DO_PAINEL = ["87956abe-940e-4e8b-8a27-82c482920f64"];
const EMAIL_DO_EXEMPLO = "john.doe@example.com";

// Comparação sem vazar em quanto tempo ela falha: string curta, custo irrelevante.
function iguais(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

async function sha256(texto) {
  const bytes = new TextEncoder().encode(texto);
  const hash = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(hash)].map(b => b.toString(16).padStart(2, "0")).join("");
}

// O Meta exige o dado normalizado ANTES do hash, senão o casamento não acontece:
// minúsculas, sem espaço nas pontas, telefone só com dígitos e com o país na frente.
const texto = v => (typeof v === "string" ? v.trim().toLowerCase() : "");

function telefone(v) {
  const d = String(v || "").replace(/\D/g, "");
  if (d.length < 10) return "";
  return d.startsWith("55") ? d : "55" + d;      // a Cakto manda o número sem o país
}

// O primeiro e o último pedaço do nome, que é como o Meta espera fn e ln.
function nome(v) {
  const partes = texto(v).split(/\s+/).filter(Boolean);
  if (!partes.length) return ["", ""];
  return [partes[0], partes.length > 1 ? partes[partes.length - 1] : ""];
}

// O valor vem como número ou como "67.00"; o que não der número não vira Purchase sem valor,
// porque venda sem valor estraga o ROAS tanto quanto venda a mais.
//
// `baseAmount` vem PRIMEIRO porque é o nome que a documentação oficial da Cakto usa no payload
// do `purchase_approved` (docs.cakto.com.br/conceitos/webhooks). Os outros quatro continuam
// como rede: a lista foi escrita antes de a documentação ser lida, e nenhuma venda real passou
// por aqui ainda para dizer qual chega de verdade.
function valor(d) {
  const bruto = d.baseAmount ?? d.amount ?? d.total ?? d.value ?? d.price;
  const n = typeof bruto === "string" ? Number(bruto.replace(",", ".")) : Number(bruto);
  return Number.isFinite(n) && n > 0 ? n : null;
}

async function usuario(c) {
  const [pn, sn] = nome(c.name);
  const em = texto(c.email);
  const ph = telefone(c.phone ?? c.cellphone ?? c.phone_number);
  const campos = {};
  if (em) campos.em = [await sha256(em)];
  if (ph) campos.ph = [await sha256(ph)];
  if (pn) campos.fn = [await sha256(pn)];
  if (sn) campos.ln = [await sha256(sn)];
  return campos;
}

// Decisão pura para manter a entrega testável sem chamar banco nem Meta. Uma compra pode
// liberar acesso mesmo quando o preço não serve para montar o evento de publicidade.
export function prepararCompraAprovada(d = {}) {
  const pedido = String(d.id || d.order_id || "");
  if (!pedido) return null;
  if (EXEMPLO_DO_PAINEL.includes(pedido)
      || texto((d.customer || {}).email) === EMAIL_DO_EXEMPLO) return null;
  if (NAO_E_VENDA.includes(texto(d.status))) return null;
  return { pedido, acesso: normalizarPedido(d), preco: valor(d) };
}

function rastreamentoDoCheckout(d = {}) {
  const checkout = String(d.checkoutUrl || d.checkout_url || "").trim();
  try {
    const url = new URL(checkout);
    const parametro = nome => String(url.searchParams.get(nome) || "").slice(0, 500);
    return {
      checkout: `${url.origin}${url.pathname}`.slice(0, 500),
      utm_source: parametro("utm_source"),
      utm_medium: parametro("utm_medium"),
      utm_campaign: parametro("utm_campaign"),
      utm_content: parametro("utm_content"),
      utm_term: parametro("utm_term"),
    };
  } catch {
    return { checkout: "", utm_source: "", utm_medium: "", utm_campaign: "",
             utm_content: "", utm_term: "" };
  }
}

// Espelho operacional sem PII. A Cakto continua sendo a fonte financeira e o Neon a fonte
// do acesso; a planilha existe para cruzar pedido, variante, UTM e estado numa tela só.
// O URL perde query string de propósito: o `sck` contém o claim do aparelho e nunca deve ser
// duplicado numa planilha.
export function prepararVendaParaPlanilha(d = {}, evento = "") {
  const pedido = String(d.id || d.order_id || "").trim();
  const email = texto((d.customer || {}).email);
  if (!pedido || EXEMPLO_DO_PAINEL.includes(pedido) || email === EMAIL_DO_EXEMPLO) return null;
  if (!["purchase_approved", "refund", "chargeback"].includes(evento)) return null;
  const acesso = normalizarPedido(d);
  const preco = valor(d);
  const produto = d.product || {};
  return {
    pedido,
    referencia: String(d.refId || d.ref_id || "").trim().slice(0, 200),
    evento,
    status: evento === "purchase_approved" ? "paid" : evento,
    produto: String(produto.name || "").trim().slice(0, 255),
    direito: acesso?.entitlement || "",
    valor: preco ?? "",
    moeda: "BRL",
    codigo_diagnostico: acesso?.diagnosticCode || "",
    meta_event_id: pedido,
    pago_em: acesso?.paidAt || "",
    origem: "cakto_webhook",
    ...rastreamentoDoCheckout(d),
  };
}

async function registrarVendaNaPlanilha(venda) {
  const url = process.env.SHEETS_SALES_URL;
  const segredo = process.env.SHEETS_SALES_SECRET;
  if (!url || !segredo) throw new Error("SHEETS_SALES_URL ou SHEETS_SALES_SECRET ausente");
  const resposta = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ tipo: "venda", segredo, ...venda }),
    signal: AbortSignal.timeout(LIMITE_PLANILHA_MS),
  });
  const corpo = await resposta.text();
  if (!resposta.ok || corpo.trim() !== "ok")
    throw new Error(`resposta inesperada (${resposta.status}): ${corpo.slice(0, 80)}`);
  return true;
}

export default {
  async fetch(request) {
    if (request.method !== "POST") return new Response("", { status: 405 });

    const segredo = process.env.CAKTO_WEBHOOK_SECRET;
    const token = process.env.META_CAPI_TOKEN;
    if (!segredo) return new Response("", { status: 503 });

    const cru = await request.text();
    if (cru.length > LIMITE_CORPO) return new Response("", { status: 413 });

    let corpo;
    try { corpo = JSON.parse(cru); } catch { return new Response("", { status: 400 }); }

    // sem o segredo certo ninguém entra: este endereço é público e um Purchase falso
    // envenena o aprendizado da campanha
    if (!iguais(String(corpo.secret || ""), segredo)) return new Response("", { status: 401 });

    const evento = String(corpo.event || "");
    // no disparo "Agrupado" o `data` é uma LISTA de pedidos, conferido no modelo do painel
    // em 19/08. Com order bump, cada linha da venda vem como um pedido, e cada uma vira um
    // Purchase com o valor dela: somar aqui inventaria uma transação que não existe.
    const pedidos = Array.isArray(corpo.data) ? corpo.data : [corpo.data || {}];

    // Reembolso e chargeback cortam o acesso. O webhook precisa ter esses dois eventos
    // marcados no painel da Cakto; até lá, este bloco fica pronto mas não é chamado.
    if (REVOGAR.has(evento)) {
      const revogacoes = pedidos.map(d =>
        revogarPedido(String(d.id || d.order_id || ""), evento));
      const vendas = pedidos.map(d => prepararVendaParaPlanilha(d, evento)).filter(Boolean)
        .map(venda => registrarVendaNaPlanilha(venda));
      const resultados = await Promise.allSettled(revogacoes);
      const resultadosVendas = await Promise.allSettled(vendas);
      for (const resultado of resultados) {
        if (resultado.status === "rejected")
          console.error("[acesso] falha ao revogar", evento, resultado.reason?.message);
      }
      for (const resultado of resultadosVendas) {
        if (resultado.status === "rejected")
          console.error("[planilha] falha ao atualizar venda", evento, resultado.reason?.message);
      }
      return new Response("ok", { status: 200 });
    }

    // 200 em tudo o que não é compra aprovada: a Cakto reenvia o que não recebe 200, e
    // evento que a gente ignora de propósito não é falha dela
    if (evento !== "purchase_approved") {
      return new Response(AGUARDANDO.includes(evento) ? "ignorado" : "ok", { status: 200 });
    }

    const agora = Math.floor(Date.now() / 1000);
    const eventos = [];
    const entregas = [];
    const vendas = [];
    for (const d of pedidos) {
      const compra = prepararCompraAprovada(d);
      if (!compra) continue;
      const { pedido, acesso, preco } = compra;
      const venda = prepararVendaParaPlanilha(d, evento);
      if (venda) vendas.push(registrarVendaNaPlanilha(venda).catch(erro =>
        console.error("[planilha] falha ao gravar venda", pedido, erro?.message)));

      // A entrega não depende do contrato de dados do Meta. Se a Cakto renomear o campo de
      // preço, o Purchase pode deixar de ser montado, mas uma compra aprovada conhecida ainda
      // precisa liberar o produto. É a função `normalizarPedido` que valida esse contrato.
      if (acesso) entregas.push((async () => {
        await registrarCompra(acesso);
      })().catch(erro => console.error("[acesso] falha na entrega", pedido, erro?.message)));
      else console.error("[acesso] pedido sem contrato de entrega", pedido,
                         JSON.stringify({ produto: (d.product || {}).name || "", temEmail: !!(d.customer || {}).email }));

      // Daqui para baixo é só Meta. Preço inválido impede um Purchase com ROAS falso, mas
      // nunca volta no tempo para impedir a entrega que já foi enfileirada acima.
      if (!preco) continue;
      const produto = d.product || {};
      eventos.push({
        event_name: "Purchase",
        // a hora do pagamento, não a de agora: o Meta recusa evento com mais de 7 dias e
        // atribui pela hora certa. Em segundos, e nunca no futuro.
        event_time: Math.min(
          Math.floor(Date.parse(d.paidAt || d.paid_at || d.createdAt || d.created_at || "") / 1000)
            || agora,
          agora),
        // o id do pedido é o que impede a mesma venda de contar duas vezes, seja num
        // reenvio da Cakto, seja se um dia o navegador também disparar
        event_id: pedido,
        action_source: "website",
        event_source_url: SITE + "/",
        user_data: await usuario(d.customer || {}),
        custom_data: {
          currency: "BRL",
          value: preco,
          // é o nome do produto na Cakto, e é ele que separa as quatro variantes do
          // teste de nome dentro do mesmo pixel
          content_name: (d.product || {}).name || "",
          content_ids: [produto.short_id || produto.id || pedido].filter(Boolean),
          content_type: "product",
          order_id: pedido,
        },
      });
    }
    // compra aprovada que não virou evento é o defeito mais caro possível aqui, e o mais
    // silencioso: foi assim que 14 dias passaram sem nenhum Purchase. Se um dia a Cakto
    // renomear `amount` ou `id`, o log é o que avisa, porque a venda entra igual no painel
    if (!eventos.length) {
      await Promise.all([...entregas, ...vendas]);
      console.error("[capi] purchase_approved sem evento montado",
                    JSON.stringify(pedidos.map(d => ({
                      id: d.id ?? d.order_id ?? null,
                      status: d.status ?? null,
                      temValor: valor(d) !== null,
                    }))).slice(0, 400));
      return new Response("nada a enviar", { status: 200 });
    }

    const payload = { data: eventos };
    // só em teste: o Events Manager mostra o evento na aba "Eventos de teste" sem sujar
    // o histórico. A Cakto não manda este campo, ele só existe no nosso curl de conferência
    if (corpo.test_event_code) payload.test_event_code = String(corpo.test_event_code);

    // Fora de produção o evento NUNCA entra no histórico do pixel. Sem isto, qualquer
    // conferência apontada para um deploy de preview vira venda de verdade no Events
    // Manager, e evento do pixel não se apaga: em 19/08 quatro cliques no botão "Testar"
    // da Cakto deixaram 4 Purchase permanentes para 2 vendas reais. O código de teste é
    // fixo porque o valor não precisa ser secreto: ele só desvia o evento de aba.
    if (!payload.test_event_code && process.env.VERCEL_ENV
        && process.env.VERCEL_ENV !== "production") {
      payload.test_event_code = "TEST_FORA_DE_PRODUCAO";
      console.error("[capi] ambiente", process.env.VERCEL_ENV,
                    "- Purchase desviado para Eventos de teste");
    }

    if (!token) {
      await Promise.all([...entregas, ...vendas]);
      console.error("[capi] META_CAPI_TOKEN ausente; acesso entregue sem evento Meta");
      return new Response("acesso ok, meta indisponível", { status: 200 });
    }

    const meta = fetch(`https://graph.facebook.com/${API}/${PIXEL}/events?access_token=${token}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    });
    const [resultadoMeta] = await Promise.allSettled([meta, ...entregas, ...vendas]);
    if (resultadoMeta.status === "rejected") {
      console.error("[capi] falha de rede", resultadoMeta.reason?.message);
      return new Response("erro no meta", { status: 200 });
    }
    const r = resultadoMeta.value;

    // o corpo da resposta do Meta não tem dado do comprador, só contagem e erro: pode logar
    const resposta = await r.text();
    if (!r.ok) console.error("[capi] o Meta recusou", r.status, resposta.slice(0, 400));

    // 200 mesmo quando o Meta recusa: se devolvermos erro, a Cakto reenvia e o problema
    // volta igual. O que precisa gritar é o log, não a plataforma de pagamento.
    //
    // No envio de teste devolve o que o Meta respondeu (`events_received` e o id do rastro,
    // sem nada do comprador): é o que prova a ponta a ponta sem esperar uma venda real.
    return new Response(payload.test_event_code ? resposta : (r.ok ? "ok" : "erro no meta"),
                        { status: 200 });
  },
};
