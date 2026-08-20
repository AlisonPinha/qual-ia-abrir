// Memória do diagnóstico e envio anônimo. Compartilhado pelo site e pela entrega paga.
//
// Memória: as respostas ficam no navegador para o comprador não ter que refazer o
// diagnóstico dentro do /mapa. Só vale no mesmo aparelho; em outro, o mapa pergunta
// de novo, que é o comportamento normal.
//
// Anônimo: nem nome nem WhatsApp saem daqui. Só o que foi respondido e o que o motor
// recomendou, para saber qual perfil responde e onde as pessoas abandonam.

const SESSAO_CHAVE = "qia:resp";
const SESSAO_DIAS = 30;
const CLAIM_CHAVE = "qia:claim";

// Segredo aleatório deste aparelho. Viaja no `sck` junto do diagnóstico, mas só ganha valor
// depois que o webhook grava uma compra paga. A /acesso consome uma vez e apaga do aparelho.
function claimCheckout() {
  try {
    const salvo = JSON.parse(localStorage.getItem(CLAIM_CHAVE) || "null");
    if (salvo?.valor && salvo.ate > Date.now()) return salvo.valor;
    const bytes = crypto.getRandomValues(new Uint8Array(24));
    const valor = btoa(String.fromCharCode(...bytes))
      .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    localStorage.setItem(CLAIM_CHAVE, JSON.stringify({ valor, ate: Date.now() + SESSAO_DIAS * 864e5 }));
    return valor;
  } catch (_) { return ""; }
}

function claimSalvo() {
  try {
    const salvo = JSON.parse(localStorage.getItem(CLAIM_CHAVE) || "null");
    return salvo?.ate > Date.now() ? salvo.valor || "" : "";
  } catch (_) { return ""; }
}

function limparClaim() {
  try { localStorage.removeItem(CLAIM_CHAVE); } catch (_) {}
}

// Assinatura das opções de uma pergunta. Sem isto, uma resposta guardada com o
// questionário antigo continuaria "válida" depois de a gente inserir uma opção nova, e o
// índice 0 do orçamento, que era "Até R$ 150", passaria a significar "só o que é grátis".
function assinaturaPergunta(rotulos) {
  let h = 5381;
  for (const r of rotulos) for (let i = 0; i < r.length; i++) h = ((h * 33) ^ r.charCodeAt(i)) >>> 0;
  return h;
}

function salvarSessao(resp, pids, livre, MOTOR) {
  try {
    const sig = {};
    if (MOTOR) for (const pid of Object.keys(resp))
      if (MOTOR.rotulos[pid]) sig[pid] = assinaturaPergunta(MOTOR.rotulos[pid]);
    localStorage.setItem(SESSAO_CHAVE, JSON.stringify({
      v: 2, resp, pids, livre: livre || {}, sig, ts: Date.now()
    }));
  } catch (e) { /* modo privado ou storage cheio: seguir sem memória */ }
}

// Devolve as respostas salvas apenas se cobrirem TODAS as perguntas desta página.
// Se o questionário mudou desde a última visita, ignora e deixa refazer: melhor
// perguntar de novo do que montar a stack com pergunta que não existe mais.
// `exigidos` é função porque, com trilha por área, quais perguntas são obrigatórias
// depende das próprias respostas salvas.
// Devolve o que dá para aproveitar, não tudo ou nada. Quando o questionário muda, quem já
// respondeu completa só o que falta em vez de recomeçar: na primeira venda, a compradora
// refez as 23 etapas por causa disso, e depois refaria de novo a cada mudança nossa.
// `completa` diz se as respostas cobrem tudo o que o motor exige agora.
function lerSessao(exigidos, MOTOR) {
  try {
    const bruto = localStorage.getItem(SESSAO_CHAVE);
    if (!bruto) return null;
    const d = JSON.parse(bruto);
    if (d.v !== 1 && d.v !== 2) return null;
    if (Date.now() - d.ts > SESSAO_DIAS * 864e5) return null;

    const resp = {};
    for (const [pid, i] of Object.entries(d.resp || {})) {
      const rotulos = MOTOR && MOTOR.rotulos[pid];
      if (!rotulos) continue;                       // pergunta que não existe mais
      if (!Number.isInteger(i) || i >= rotulos.length) continue;
      // sem assinatura (memória da versão 1) as opções podem ter mudado por baixo:
      // só aproveita o que ainda bate exatamente
      if (d.v === 2 && d.sig && d.sig[pid] !== assinaturaPergunta(rotulos)) continue;
      // memória sem assinatura: aproveita tudo, menos as perguntas que a gente sabe que
      // tiveram as opções mexidas desde então
      if (d.v === 1 && (MOTOR.mudaram || []).includes(pid)) continue;
      resp[pid] = i;
    }
    if (!Object.keys(resp).length) return null;
    return { resp, livre: d.livre || {}, completa: exigidos(resp).every(p => p in resp) };
  } catch (e) { return null; }
}

function limparSessao() {
  try { localStorage.removeItem(SESSAO_CHAVE); } catch (e) {}
}

// Origem do tráfego: o que veio na URL, guardado para a compra que acontece dias
// depois não aparecer como direta. Last touch: parâmetro novo passa a valer.
const ORIGEM_CHAVE = "qia:org";
const PARAMETROS_ORIGEM = [
  "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "fbclid", "gclid"
];

// Só atribuição reconhecida viaja para a Cakto. O código do diagnóstico e qualquer outro
// parâmetro da página ficam de fora, para um link compartilhado não virar campanha por engano.
function filtrarOrigem(busca = "") {
  const entrada = new URLSearchParams(busca);
  const saida = new URLSearchParams();
  for (const k of PARAMETROS_ORIGEM) {
    for (const valor of entrada.getAll(k)) saida.append(k, valor);
  }
  return saida.toString();
}

function origemTrafego() {
  const agora = filtrarOrigem(location.search);
  try {
    if (agora) localStorage.setItem(ORIGEM_CHAVE, agora);
    const salvo = filtrarOrigem(localStorage.getItem(ORIGEM_CHAVE) || "");
    if (!agora && salvo) localStorage.setItem(ORIGEM_CHAVE, salvo);
    return agora || salvo;
  } catch (e) { return agora; }        // modo privado: vale só a visita atual
}

// Envio anônimo. no-cors porque o Apps Script não devolve cabeçalho de CORS:
// o que importa é gravar, não ler a resposta. Falha em silêncio de propósito,
// porque analytics não pode quebrar a entrega.
function enviarAnalitico(url, origem, MOTOR, resp, stack, corta, livre) {
  if (!url) return;
  try {
    const respostas = {};
    for (const [q, i] of Object.entries(resp)) {
      if (q.startsWith("break")) continue;          // o break não é resposta
      respostas[q] = MOTOR.rotulos[q][i];
    }
    fetch(url, {
      method: "POST",
      mode: "no-cors",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify({
        tipo: "diagnostico",
        origem,                                      // "site" ou "mapa"
        utm: origemTrafego(),                        // de onde a pessoa veio
        respostas,
        // o que a pessoa escreveu quando nenhuma opção era a dela: é o que diz
        // qual tarefa está faltando no quiz
        descreveu: Object.values(livre || {}).join(" | "),
        stack: stack.map(s => s.nome),
        cortar: corta,
        ts: new Date().toISOString()
      })
    }).catch(() => {});
  } catch (e) { /* nunca atrapalhar o resultado */ }
}

// Lead da saída: nome e WhatsApp de quem já viu o resultado e está indo embora. Vai pelo
// mesmo Web App do envio anônimo, que separa por `tipo`, então não depende da CAPTURA_URL:
// o passo de contato no meio do quiz continua desligado, que é o que o playbook manda.
// keepalive porque a pessoa clica e sai na sequência.
function enviarLead(url, MOTOR, resp, stack, corta, livre, nome, whatsapp) {
  if (!url) return;
  try {
    const respostas = {};
    for (const [q, i] of Object.entries(resp)) {
      if (q.startsWith("break")) continue;
      respostas[q] = MOTOR.rotulos[q][i];
    }
    fetch(url, {
      method: "POST", mode: "no-cors", keepalive: true,
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify({
        tipo: "lead", nome, whatsapp,
        utm: origemTrafego(),
        respostas,
        descreveu: Object.values(livre || {}).join(" | "),
        stack: stack.map(s => s.nome),
        cortar: corta,
        ts: new Date().toISOString()
      })
    }).catch(() => {});
  } catch (e) { /* o lead nunca pode travar a saída */ }
}

// Funil do quiz: onde a pessoa parou. O envio anônimo acima só acontece quando o quiz
// TERMINA, então quem sai no meio não deixava rastro nenhum e a taxa de saída por
// pergunta era invisível. Aqui sai uma linha por pessoa, atualizada a cada saída, e quem
// conclui fica marcado na mesma linha: assim a aba tem numerador e denominador juntos.
//
// Não é do playbook. É medição nossa, e serve para diagnóstico do quiz, não para decidir
// teste A/B, que o playbook manda julgar pela conversão final.
const FUNIL_CHAVE = "qia:sid";

// Identidade anônima da visita, só para a mesma pessoa não virar dez linhas. Não é
// login, não sai daqui e não se cruza com nada: é um número de sorteio no navegador.
//
// O sorteio de reserva é feito UMA vez por carregamento, e não um valor fixo: com o
// storage bloqueado, um valor fixo faria todo mundo cair na mesma linha da planilha, e o
// upsert do Apps Script ficaria sobrescrevendo uma pessoa com a outra.
const SID_DESTA_VISITA = "v" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);

function idVisita() {
  try {
    let id = localStorage.getItem(FUNIL_CHAVE);
    if (!id) {
      id = Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
      localStorage.setItem(FUNIL_CHAVE, id);
    }
    return id;
  } catch (e) { return SID_DESTA_VISITA; }   // modo privado: uma linha por visita
}

// `estado()` devolve onde a pessoa está, ou null quando ela nem abriu o quiz: quem só
// leu a página não é abandono de quiz e não pode entrar na conta.
function rastrearFunil(url, origem, estado) {
  if (!url) return;
  let ultimo = "";
  const enviar = () => {
    const e = estado();
    if (!e) return;
    // trocar de app e voltar dispara isto várias vezes no mesmo ponto; sem esta guarda,
    // uma pessoa parada na pergunta 3 gera um POST a cada troca
    const chave = e.pid + "|" + e.respondidas + "|" + e.concluiu;
    if (chave === ultimo) return;
    ultimo = chave;
    const corpo = JSON.stringify(Object.assign(
      { tipo: "funil", sid: idVisita(), origem, utm: origemTrafego(),
        ts: new Date().toISOString() }, e));
    // sendBeacon é o único envio que o navegador promete entregar com a aba fechando;
    // fetch keepalive fica de reserva para quem não tem
    try {
      if (navigator.sendBeacon
          && navigator.sendBeacon(url, new Blob([corpo], { type: "text/plain;charset=utf-8" })))
        return;
    } catch (err) { /* cai no fetch abaixo */ }
    try {
      fetch(url, {
        method: "POST", mode: "no-cors", keepalive: true,
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: corpo
      }).catch(() => {});
    } catch (err) { /* medição nunca quebra a página */ }
  };
  // visibilitychange é o que dispara de verdade no celular: trocar de app, bloquear a
  // tela ou fechar a aba pelo gerenciador não passa por beforeunload nem por unload
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") enviar();
  });
  addEventListener("pagehide", enviar);
}
