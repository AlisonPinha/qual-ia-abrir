#!/usr/bin/env python3
"""
Gera _private/mapa.html: a entrega paga do "Qual IA Usar?".

É o mesmo diagnóstico do site, sem o paywall. Onde o index mostra silhueta e
faixa de preço vaga, aqui vem o nome, o custo real, o primeiro passo e o prompt
pronto de cada ferramenta.

O cálculo é o mesmo arquivo (_build/motor.js) que o index injeta, para que a
versão paga nunca devolva uma stack diferente da que o teaser mostrou.

A URL não é divulgada e a página sai com noindex: quem chega aqui é quem comprou.
Quando houver volume, o gate vira login de verdade e esta página não muda.

Uso: python3 _build/gerar_mapa.py
"""

import json
import pathlib
import sys
from html import escape

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BUILD = RAIZ / "_build"
SAIDA = RAIZ / "_private" / "mapa.html"
SAIDA.parent.mkdir(parents=True, exist_ok=True)

d = json.loads((BUILD / "dados.json").read_text(encoding="utf-8"))
CSS = (BUILD / "estilo.css").read_text(encoding="utf-8")
MOTOR_JS = (BUILD / "motor.js").read_text(encoding="utf-8")
SESSAO_JS = (BUILD / "sessao.js").read_text(encoding="utf-8")
ESPELHO_JS = (BUILD / "espelho.js").read_text(encoding="utf-8")
CODIGO_JS = (BUILD / "codigo.js").read_text(encoding="utf-8")
sys.path.insert(0, str(BUILD))
from config import ANALITICO_URL, CHECKOUT_UPSELL  # noqa: E402
import questionario  # noqa: E402
F = d["ferramentas"]
DG = d["diagnostico"]
UP = d["upsell"]
PR = d["presente"]

# O que a pessoa paga aqui é o pacote menos o que ela já pagou pelo mapa. O número não
# se escreve à mão em lugar nenhum: sai sempre desta conta, senão um dia os dois divergem.
LIQUIDO = int(UP["preco"]) - int(UP["credito"])

# ---------- perguntas: mesmo HTML do index, incluindo os breaks e as trilhas ----------

perguntas_html, regras, n_perguntas = questionario.montar(DG["perguntas"], DG["aberta"])

# ---------- motor completo: aqui não se omite nada ----------

motor = {
    "pesos": {p[0]: [pesos for _t, pesos in p[2]] for p in DG["perguntas"]},
    "rotulos": {p[0]: [texto for texto, _p in p[2]] for p in DG["perguntas"]},
    "se": regras,
    "total": n_perguntas,
    "ordem": DG["ordem"],
    "gratis": DG["gratis"],
    "gratisPlano": DG["gratisPlano"],
    "curtoGratis": DG["curtoGratis"],
    "espelho": DG["espelho"],
    "mudaram": DG["mudaram"],
    "espelhoPronto": DG["espelhoPronto"],
    "cabem": DG["cabem"],
    "teto": DG["teto"],
    "foco": DG["foco"],
    "celular": DG["celular"],
    "semCelular": DG["semCelular"],
    "perfil": DG["perfil"],
    "analitico": ANALITICO_URL,
    "pids": [p[0] for p in DG["perguntas"] if not p[0].startswith("break")],
    "ferramentas": {
        n: {
            "curto": DG["acesso"][n]["curto"],
            "faixa": DG["acesso"][n]["faixa"],
            "free": DG["acesso"][n]["free"],
            "generalista": DG["acesso"][n].get("generalista", False),
            # o que o index esconde:
            "logo": F[n]["logo"],
            "url": F[n]["url"],
            "oq": F[n]["oq"],
            "custo": DG["acesso"][n]["custo"],
            "passo": DG["comeco"][n][0],
            "prompt": DG["comeco"][n][1],
            # o que existe dentro dela e quase ninguém usa; vazio quando não conferi
            "recursos": DG.get("recursos", {}).get(n, []),
        }
        for n in F
    },
}

# ---------- o mesmo motor, do lado do servidor ----------
# A function /api/mapa recalcula a stack em vez de acreditar no que o navegador
# mandar: o cliente só envia índices de resposta, e o texto que vai para o modelo
# sai daqui. Sem isso, qualquer um poderia mandar texto próprio para dentro do prompt.

# fora de api/ de propósito: todo arquivo dentro de api/ vira rota, e este é biblioteca
API_MOTOR = RAIZ / "_lib" / "motor.mjs"
motor_api = {k: v for k, v in motor.items() if k != "analitico"}
motor_api["titulos"] = {p[0]: p[1] for p in DG["perguntas"]}
motor_api["aviso_custo"] = DG["aviso_custo"]
motor_api["aberta"] = DG["aberta"]
# a /api/plano precisa do esqueleto da semana: o mesmo dado que a página usa
motor_api["dias"] = d["semana"]["dias"]
motor_api["recursos"] = DG["recursos"]

# ---------- a venda dentro da entrega ----------
#
# Duas peças com o mesmo preço e o mesmo link, em momentos diferentes:
#   oto  → aparece uma vez, na primeira vez que o mapa é revelado (tarefa 2.3)
#   asc  → fica no fim do mapa para sempre, porque quem paga no Pix não volta ao
#          checkout, e sem isto não existe caminho do produto de entrada para o
#          upsell fora da plataforma de pagamento (tarefa 2.4)
#
# Sem CHECKOUT_UPSELL as duas somem e a entrega segue inteira: botão que não leva a
# lugar nenhum é pior do que botão nenhum.

def _conta(rotulo, valor, classe=""):
    return (f'<span class="{classe}"><i>{escape(rotulo)}</i>'
            f'<b>{escape(valor)}</b></span>')


if CHECKOUT_UPSELL:
    _itens = "".join(f'<li><b>{escape(titulo)}</b><span>{escape(txt)}</span></li>'
                     for titulo, txt in UP["entregaveis"])
    _r1, _r2, _r3 = UP["conta"]
    oto_html = f"""
  <section class="oto" id="oto" hidden aria-labelledby="oto-titulo">
    <span class="selo-rosa">{escape(UP["rotulo"])}</span>
    <h2 id="oto-titulo" tabindex="-1">{escape(UP["nome"])}</h2>
    <p class="oto-promessa"><b class="crenca">{escape(DG["crencaCurta"])}</b>
       {escape(UP["promessa"])}</p>
    <ul class="oto-lista">{_itens}</ul>
    <div class="oto-conta">
      {_conta(_r1, f'R$ {UP["preco"]}')}
      {_conta(_r2, f'- R$ {UP["credito"]}')}
      {_conta(_r3, f'R$ {LIQUIDO}', "oto-total")}
    </div>
    <p class="oto-razao">{escape(UP["razao_preco"])}</p>
    <a class="btn-cta" id="oto-comprar" href="{CHECKOUT_UPSELL}" target="_blank"
       rel="noopener">{escape(UP["cta"])} por R$ {LIQUIDO}\u00a0→</a>
    <p class="oto-nota">{escape(UP["nota"])}</p>
    <button type="button" class="oto-pular" id="oto-pular">{escape(UP["pular"])}</button>
  </section>"""

    asc_html = f"""
    <section class="asc" id="ascensao">
      <span class="asc-rot">{escape(UP["rotulo_mapa"])}</span>
      <h3>{escape(UP["nome"])}</h3>
      <p>{escape(UP["promessa"])}</p>
      <p class="asc-preco"><b>R$ {LIQUIDO}</b><i>com os seus R$ {UP["credito"]} já abatidos</i></p>
      <a class="btn-cta" href="{CHECKOUT_UPSELL}" target="_blank" rel="noopener">{escape(UP["cta"])}\u00a0→</a>
      <p class="asc-nota">{escape(UP["nota"])}</p>
    </section>"""
else:
    oto_html = asc_html = ""

# ---------- o presente: qual produto vem depois ----------
# Só existe se houver para onde gravar. Uma pergunta, no fim da entrega, depois de a
# pessoa ter recebido o que comprou.

if ANALITICO_URL:
    _opcoes = "".join(
        f'<button type="button" class="opc" aria-pressed="false">{escape(o)}</button>'
        for o in PR["opcoes"] + [PR["outro"]])
    pres_html = f"""
    <section class="pres" id="presente">
      <h3>{escape(PR["titulo"])}</h3>
      <p class="pres-sub">{escape(PR["sub"])}</p>
      <div class="pres-opcoes" id="pres-opcoes" role="group"
           aria-label="{escape(PR["titulo"])}">{_opcoes}</div>
      <div class="campo-aberto" id="pres-campo" hidden>
        <label for="pres-outro">{escape(PR["campo"])}</label>
        <input id="pres-outro" type="text" maxlength="120" autocomplete="off">
      </div>
      <button type="button" class="btn btn-p" id="pres-enviar" disabled>{escape(PR["botao"])}</button>
      <p class="pres-pronto" id="pres-pronto" hidden>{escape(PR["pronto"])}</p>
    </section>"""
else:
    pres_html = ""

JS = r"""
  const el = id => document.getElementById(id);
  const quiz = el("quiz");
  const passos = [...quiz.querySelectorAll(".passo")];
  const resp = {};
  // quem entra por código ou por memória não passa pelo quiz, e não é abandono de quiz
  let abriuQuiz = false;
  let terminouQuiz = false;
  const livre = {};          // o que a pessoa escreveu quando nenhuma opção era a dela
  let atual = 0;
  let stackAtual = [];       // a última stack calculada, para o voto do presente

  // trilha por área: o passo que não é da área respondida não aparece nem conta
  const vale = i => valePergunta(MOTOR, passos[i].dataset.q, resp);
  // completando: veio memória parcial, então pergunta só o que falta e corta os breaks,
  // que são conteúdo de convencimento para quem está respondendo a primeira vez
  let completando = false;
  let faltavam = 0;   // quantas faltavam quando ela chegou, para o contador não travar em 1
  const precisa = i => {
    const q = passos[i].dataset.q;
    if (!vale(i)) return false;
    if (MOTOR.pids.includes(q)) return !(q in resp);
    return !(completando && /^break\d/.test(q));
  };
  const ehPergunta = i => MOTOR.pids.includes(passos[i].dataset.q);

  // O teto é MOTOR.total, o caminho mais longo. Só desce quando a pessoa responde algo
  // que exclui uma pergunta de vez: assim o contador nunca cresce no meio do quiz, que
  // é o que assusta, e no máximo dá a boa notícia de que acabou antes.
  const totalPerguntas = () => {
    let n = MOTOR.total;
    for (const p of passos) {
      const q = p.dataset.q, se = MOTOR.se[q];
      if (!se || "area" in se || !MOTOR.pids.includes(q)) continue;
      const fora = Object.entries(se).some(([dep, vals]) => dep in resp && !vals.includes(resp[dep]));
      if (fora) n--;
    }
    return n;
  };

  let espelhoPronto = false;
  const prepararEspelho = () => {
    if (espelhoPronto) return;
    espelhoPronto = true;
    pintarEspelho(MOTOR, resp, el("espelho-lista"));
    const botao = passos[atual].querySelector(".opc");
    const status = el("espelho-status");
    // o botão nasce clicável no HTML: se o JS falhar, ninguém fica preso na tela
    botao.disabled = true;
    setTimeout(() => { status.textContent = MOTOR.espelhoPronto; botao.disabled = false; }, 1600);
  };

  const mostrar = () => {
    abriuQuiz = true;          // a partir daqui existe quiz na tela, e existe abandono
    passos.forEach((p, i) => { p.hidden = i !== atual; });
    // a tela de espelho carrega, repete as respostas e só então libera o resultado
    if (passos[atual].dataset.q === "break_espelho") prepararEspelho();
    const fila = passos.map((_p, i) => i).filter(precisa);
    // A fila é o que ainda FALTA responder, e por isso não serve para medir progresso: a
    // pergunta respondida sai dela na hora, então a posição dava "1 de 19" em toda tela e a
    // barra ficava presa no começo. O caminho é o quiz inteiro desta pessoa, já respondido
    // ou não, e é sobre ele que o contador e a barra andam.
    const caminho = passos.map((_p, i) => i).filter(i => ehPergunta(i) && vale(i));
    const feitas = caminho.filter(i => i <= atual).length;
    // o passo atual conta como iniciado: barra vazia na pergunta 1 derruba a conclusão
    el("barra-fill").style.width = ((feitas - 0.6) / caminho.length * 100) + "%";
    const num = passos[atual].querySelector(".num");
    if (num && ehPergunta(atual))
      // o total não é constante: com pergunta condicional, um número fixo mentiria para
      // quem pula duas, e contador que mente faz abandonar o quiz
      num.textContent = completando
        ? (faltavam - fila.filter(ehPergunta).length + 1) + " de " + faltavam
        : feitas + " de " + totalPerguntas();
  };

  const proximo = () => { do { atual++; } while (atual < passos.length && !precisa(atual)); };
  const esc = s => String(s).replace(/[&<>"]/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function render(daMemoria) {
    terminouQuiz = true;
    const { stack, corta } = calcularStack(MOTOR, resp);
    stackAtual = stack;
    if (!daMemoria) salvarSessao(resp, MOTOR.pids, livre, MOTOR);
    enviarAnalitico(MOTOR.analitico, "mapa", MOTOR, resp, stack, corta, livre);
    el("res-memoria").hidden = !daMemoria;
    // o campo de código é para quem ainda não entrou: em cima do mapa vira ruído
    const entrar = el("entrar-codigo");
    if (entrar) entrar.hidden = true;
    el("mapa-sub").textContent = daMemoria
      ? "Suas respostas do site já estão aqui. Abaixo vem tudo: o custo real de cada uma, "
        + "o primeiro passo e o prompt pronto para copiar."
      : "Pronto. Abaixo vem tudo: o custo real de cada uma, o primeiro passo e o prompt "
        + "pronto para copiar.";
    const [qArea, qOrc] = MOTOR.perfil;
    el("res-perfil").textContent =
      `${MOTOR.rotulos[qArea][resp[qArea]]} · ${MOTOR.rotulos[qOrc][resp[qOrc]]}.`;

    const codigo = gerarCodigo(MOTOR, resp);
    if (codigo) {
      el("res-codigo-valor").textContent = codigo;
      el("res-codigo").hidden = false;
      // O código salva as respostas, não a compra. Em outro aparelho a pessoa primeiro entra
      // pelo e-mail em /acesso e usa o código apenas se o pedido antigo não tiver sido ligado
      // automaticamente ao diagnóstico.
      const zap = el("res-codigo-zap");
      if (zap) {
        const texto = "O meu mapa de IA, do Qual IA Usar\n\n"
          + stack.map((s, i) => `${i + 1}. ${s.nome} (${s.custo})`).join("\n")
          + (corta.length ? "\n\nO que não assinar agora: " + corta.join(", ") : "")
          + "\n\nCódigo do meu diagnóstico: " + codigo
          + "\nPara abrir em outro aparelho, peço o link pessoal por aqui:\n"
          + location.origin + "/acesso";
        zap.href = "https://wa.me/?text=" + encodeURIComponent(texto);
        zap.textContent = "Mandar no meu WhatsApp";
      }
    }

    el("res-stack").innerHTML = stack.map((s, i) => `
      <li class="m-card">
        <div class="m-cab">
          <img class="m-logo" src="/logos/${esc(s.logo)}" alt="" width="34" height="34">
          <div class="m-id">
            <a class="m-nome" href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.nome)}</a>
            <span class="m-oq">${esc(s.oq)}</span>
          </div>
          <span class="res-n">${i + 1}</span>
        </div>
        <div class="m-meta">
          <span class="m-quando">${esc(s.quando)}</span>
          <span class="m-custo">${esc(s.custo)}</span>
        </div>
        <div class="m-bloco" id="porque${i}" hidden>
          <span class="m-rot">Por que esta pra você</span>
          <p></p>
        </div>
        ${s.recursos.length ? `<div class="m-bloco">
          <span class="m-rot">Dentro dela, o que quase ninguém usa</span>
          <ul class="m-recursos">${s.recursos.map(([nome, oq]) =>
            `<li><b>${esc(nome)}</b> ${esc(oq)}</li>`).join("")}</ul>
        </div>` : ""}
        <div class="m-bloco">
          <span class="m-rot">Primeiro passo</span>
          <p>${esc(s.passo)}</p>
        </div>
        <div class="m-bloco">
          <span class="m-rot">Prompt pronto</span>
          <pre class="m-prompt" id="p${i}">${esc(s.prompt)}</pre>
          <button type="button" class="m-copiar" data-alvo="p${i}">Copiar prompt</button>
        </div>
      </li>`).join("");

    el("res-corta").innerHTML = "<b>O que não assinar agora:</b> " +
      corta.map(n => `${esc(n)} <i>(${esc(MOTOR.ferramentas[n].custo)})</i>`).join(", ") + ".";

    for (const b of el("res-stack").querySelectorAll(".m-copiar")) {
      b.addEventListener("click", async () => {
        await navigator.clipboard.writeText(el(b.dataset.alvo).textContent);
        b.textContent = "Copiado";
        setTimeout(() => { b.textContent = "Copiar prompt"; }, 1600);
      });
    }

    quiz.hidden = true;
    el("barra-fill").style.width = "100%";
    // a origem viaja junto para a Cakto: sem ela a venda do upsell aparece como direta
    const origem = origemTrafego();
    const claim = claimCheckout();
    for (const a of document.querySelectorAll('a[href*="pay.cakto.com.br"]')) {
      const url = new URL(a.href);
      if (origem && !a.dataset.org) {
        for (const [chave, valor] of new URLSearchParams(origem)) url.searchParams.set(chave, valor);
      }
      if (codigo && claim) url.searchParams.set("sck", "qia2_" + codigo + "." + claim);
      a.href = url.toString();
      a.dataset.org = "1";
    }
    if (oto && !otoVisto()) { oto.hidden = false; el("oto-titulo").focus(); }
    else abrirMapa();
    redigir(resp, livre);
  }

  // ---------- a camada de IA (ADR-0001: as regras decidem, a IA redige) ----------
  //
  // Tudo acima já está na tela e completo. O que vem daqui é a versão escrita para
  // esta pessoa, colocada por cima. Se a chamada falhar, demorar ou vier pela metade,
  // cada bloco volta ao que era: o mapa não depende disso para ser entregue.

  const IA_CHAVE = "qia:ia";
  const TEM_PRECO = /R\$|US\$|\d+\s*(d[óo]lares|reais)/i;
  // "eu mesmo" e "eu mesma" marcam o gênero de quem copia o prompt como se tivesse escrito.
  // A regra 7 do SISTEMA já proíbe e mesmo assim escapou em produção, dentro de um PROMPT:
  // instrução não é garantia, então o corte aqui é determinístico, igual ao do preço.
  // Fica só o que é inequívoco: "sozinho" costuma ser a ferramenta, não a pessoa.
  const MARCA_GENERO = /\beu mesm[oa]\b/i;
  // A conexão pode cair e mesmo assim o navegador dar a leitura por encerrada. Por isso
  // "terminou" não é o stream fechar, é o último bloco ter chegado: sem isso, um prompt
  // cortado no meio ficaria na tela com cara de pronto, e é ele que a pessoa copia.
  const BLOCOS = ["ABERTURA", "PORQUE1", "PROMPT1", "PORQUE2", "PROMPT2",
                  "PORQUE3", "PROMPT3", "CORTE"];
  const inteiro = t => BLOCOS.every(n => t.includes("[[" + n + "]]"));
  let emEscrita = null;

  function alvosDaVez() {
    const alvos = {
      ABERTURA: { no: el("res-abertura") },
      CORTE: { no: el("res-corta-ia") },
    };
    for (let i = 0; i < 3; i++) {
      const porque = el("porque" + i);
      if (porque) alvos["PORQUE" + (i + 1)] = { no: porque.querySelector("p"), caixa: porque };
      const pre = el("p" + i);
      if (pre) alvos["PROMPT" + (i + 1)] = {
        no: pre, fixo: pre.textContent,
        botao: el("res-stack").querySelector(`.m-copiar[data-alvo="p${i}"]`),
      };
    }
    return alvos;
  }

  function escrever(alvos, nome, texto, fechado) {
    const a = alvos[nome];
    if (!a || a.travado) return;
    // preço só existe onde o produto escreveu: se o modelo inventar valor, o bloco
    // inteiro é descartado e fica o texto de fábrica
    if (a.fixo === undefined && TEM_PRECO.test(texto)) { a.travado = true; return; }
    // marca de gênero trava até o prompt, que é onde ela mais dói: volta o de fábrica
    if (MARCA_GENERO.test(texto)) {
      a.travado = true;
      if (a.fixo !== undefined) { a.no.textContent = a.fixo; if (a.botao) a.botao.disabled = false; }
      else { a.no.textContent = ""; (a.caixa || a.no).hidden = true; }
      return;
    }
    a.no.textContent = texto;
    (a.caixa || a.no).hidden = !texto;
    if (a.botao) a.botao.disabled = !fechado;
    a.fechado = fechado;
  }

  function aplicar(alvos, buffer, fim) {
    const partes = buffer.split(/\[\[([A-Z]+\d?)\]\]/);
    for (let i = 1; i < partes.length; i += 2)
      escrever(alvos, partes[i], (partes[i + 1] || "").trim(), fim || i + 2 < partes.length);
  }

  function devolver(alvos) {
    for (const a of Object.values(alvos)) {
      if (a.fechado) continue;
      if (a.fixo !== undefined) { a.no.textContent = a.fixo; if (a.botao) a.botao.disabled = false; }
      else { a.no.textContent = ""; (a.caixa || a.no).hidden = true; }
    }
  }

  async function redigir(resp, livre) {
    if (emEscrita) emEscrita.abort();          // refez o quiz no meio: a anterior morre
    const alvos = alvosDaVez();
    const chave = JSON.stringify([resp, livre]);
    try {
      const guardado = JSON.parse(localStorage.getItem(IA_CHAVE) || "null");
      if (guardado && guardado.k === chave) return aplicar(alvos, guardado.t, true);
    } catch (e) { /* sem memória: escreve de novo */ }

    const aviso = el("res-escrevendo");
    // Duas tentativas: resposta sem os oito blocos deixaria a pessoa com o texto de
    // fábrica em cima do que ela pagou. Escrever de novo custa menos que entregar
    // genérico, e o teto de duas impede que um modelo teimoso rode em laço.
    for (let tentativa = 0; tentativa < 2; tentativa++) {
      const ctrl = new AbortController();
      emEscrita = ctrl;
      // 75s: a function tem maxDuration de 60s e as respostas medidas levam de 34 a 44s.
      // Em 45s o relógio cortava o stream no último bloco, e a pessoa perdia o corte.
      const relogio = setTimeout(() => ctrl.abort(), 75000);
      let buffer = "";
      try {
        const r = await fetch("/api/mapa", {
          method: "POST", signal: ctrl.signal,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ resp, livre }),
        });
        // 429 é o teto de chamadas e 503 é falta de chave: insistir dá o mesmo,
        // e a segunda tentativa só existe para resposta incompleta ou queda no meio.
        if (r.status === 429 || r.status === 503) break;
        if (!r.ok || !r.body) throw new Error(r.status);
        aviso.hidden = false;
        const leitor = r.body.getReader();
        const dec = new TextDecoder();
        for (;;) {
          const { done, value } = await leitor.read();
          if (done) break;
          buffer += dec.decode(value, { stream: true });
          aplicar(alvos, buffer, false);
        }
        if (inteiro(buffer)) {
          aplicar(alvos, buffer, true);
          try { localStorage.setItem(IA_CHAVE, JSON.stringify({ k: chave, t: buffer })); } catch (e) {}
          return;
        }
      } catch (e) {
        if (ctrl.signal.aborted && emEscrita !== ctrl) return;   // o quiz foi refeito: some
      } finally {
        clearTimeout(relogio);
        aviso.hidden = true;
        if (emEscrita === ctrl) emEscrita = null;
      }
    }
    devolver(alvos);                            // as duas falharam: texto de fábrica, entrega intacta
  }

  // "nenhuma dessas": em vez de avançar, abre o campo. Ninguém é obrigado a escolher
  // uma tarefa que não é a dele só para o quiz deixar passar.
  const abrirCampo = (b) => {
    const passo = b.closest(".passo");
    const campo = passo.querySelector(".campo-aberto");
    if (!campo || b !== b.parentNode.lastElementChild) {
      if (campo) { campo.hidden = true; delete livre[passo.dataset.q]; }
      return false;
    }
    campo.hidden = false;
    campo.querySelector("input").focus();
    campo.scrollIntoView({ block: "nearest", behavior: "smooth" });   // no celular nasce abaixo da dobra
    return true;
  };

  for (const b of quiz.querySelectorAll(".opc")) {
    b.addEventListener("click", () => {
      resp[b.dataset.q] = +b.dataset.i;
      // trocar a área depois de voltar derruba a trilha antiga
      limparOrfas(MOTOR, resp);
      for (const irmao of b.parentNode.children)
        irmao.setAttribute("aria-pressed", String(irmao === b));
      if (abrirCampo(b)) return;
      proximo();
      if (atual < passos.length) mostrar(); else render();
    });
  }

  for (const b of quiz.querySelectorAll(".btn-livre")) {
    const campo = b.parentNode.querySelector("input");
    const seguir = () => {
      const texto = campo.value.trim();
      if (texto) livre[campo.closest(".passo").dataset.q] = texto;
      proximo();
      if (atual < passos.length) mostrar(); else render();
    };
    b.addEventListener("click", seguir);
    // sem isto o Enter submete o formulário e recarrega a página no meio do quiz
    campo.addEventListener("keydown", e => {
      if (e.key === "Enter") { e.preventDefault(); seguir(); }
    });
  }

  el("refazer").addEventListener("click", () => {
    limparSessao();
    for (const k of Object.keys(resp)) delete resp[k];
    for (const b of quiz.querySelectorAll(".opc")) b.setAttribute("aria-pressed", "false");
    atual = 0;
    el("resultado").hidden = true;
    quiz.hidden = false;
    mostrar();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  // ---------- a tela pós-compra (2.3) ----------
  //
  // Aparece uma vez, entre a identificação e o mapa. Nunca segura a entrega: o botão de
  // abrir o mapa está na mesma tela, e comprar também libera, porque o checkout abre em
  // outra aba e a pessoa volta para esta. Quem já dispensou não vê de novo, e o lembrete
  // permanente do fim do mapa passa a ser o único caminho.
  const OTO_CHAVE = "qia:oto";
  const oto = el("oto");
  const otoVisto = () => {
    try { return localStorage.getItem(OTO_CHAVE) === "1"; } catch (e) { return false; }
  };
  function abrirMapa() {
    try { localStorage.setItem(OTO_CHAVE, "1"); } catch (e) { /* modo privado: só desta vez */ }
    if (oto) oto.hidden = true;
    el("resultado").hidden = false;
    el("res-titulo").focus();
  }
  if (oto) {
    el("oto-pular").addEventListener("click", abrirMapa);
    el("oto-comprar").addEventListener("click", abrirMapa);
  }

  // ---------- o presente: qual produto vem depois (2.8) ----------
  const pres = el("presente");
  if (pres) {
    const opcoes = [...pres.querySelectorAll(".opc")];
    const campo = el("pres-campo");
    const enviar = el("pres-enviar");
    let escolha = "";
    for (const b of opcoes) {
      b.addEventListener("click", () => {
        escolha = b.textContent.trim();
        for (const irmao of opcoes) irmao.setAttribute("aria-pressed", String(irmao === b));
        const aberto = b === opcoes[opcoes.length - 1];   // "outra coisa" abre o campo
        campo.hidden = !aberto;
        if (aberto) el("pres-outro").focus();
        enviar.disabled = false;
      });
    }
    enviar.addEventListener("click", () => {
      const qArea = MOTOR.perfil[0];
      try {
        fetch(MOTOR.analitico, {
          method: "POST", mode: "no-cors",
          headers: { "Content-Type": "text/plain;charset=utf-8" },
          body: JSON.stringify({
            tipo: "presente",
            escolha,
            outro: el("pres-outro").value.trim().slice(0, 120),
            area: MOTOR.rotulos[qArea][resp[qArea]] || "",
            stack: stackAtual.map(s => s.nome),
            origem: "mapa",
            utm: origemTrafego(),
            ts: new Date().toISOString(),
          }),
        }).catch(() => {});
      } catch (e) { /* voto não pode quebrar a entrega */ }
      el("pres-opcoes").hidden = true;
      campo.hidden = true;
      enviar.hidden = true;
      el("pres-pronto").hidden = false;
    });
  }

  // funil: em que pergunta a pessoa parou. Aqui é quem já pagou: comprador que trava no
  // meio do quiz não recebe a entrega, e isso é reembolso, não só métrica.
  rastrearFunil(MOTOR.analitico, "mapa", () => {
    if (!abriuQuiz) return null;
    const passo = passos[Math.min(atual, passos.length - 1)];
    const legenda = passo.querySelector("legend");
    const caminho = passos.map((_p, i) => i).filter(i => vale(i) && ehPergunta(i));
    const [qArea] = MOTOR.perfil;
    return {
      pid: terminouQuiz ? "(concluiu)" : passo.dataset.q,
      // o enunciado sai do DOM porque o contador "n de m" é o primeiro filho do legend
      pergunta: terminouQuiz || !legenda || !legenda.lastChild
              ? "" : legenda.lastChild.textContent.trim(),
      posicao: terminouQuiz ? ""
             : caminho.filter(i => i <= atual).length + " de " + totalPerguntas(),
      respondidas: Object.keys(resp).filter(q => MOTOR.pids.includes(q)).length,
      total: totalPerguntas(),
      area: qArea in resp ? MOTOR.rotulos[qArea][resp[qArea]] : "",
      concluiu: terminouQuiz ? "sim" : ""
    };
  });

  // veio do site no mesmo aparelho: não faz a pessoa responder tudo de novo
  // ordem de entrada: código na URL, código digitado, memória do navegador, quiz.
  // A primeira venda de teste mostrou por que: quem compra no celular abre o e-mail no
  // computador, e sem isto refaz as 23 etapas depois de ter pago.
  function entrarCom(respostas) {
    for (const k of Object.keys(resp)) delete resp[k];
    Object.assign(resp, respostas);
    const bloco = el("entrar-codigo");
    if (bloco) bloco.hidden = true;
    render(true);
  }

  el("codigo-usar").addEventListener("click", () => {
    const lido = lerCodigo(MOTOR, el("codigo-campo").value);
    if (!lido) { el("codigo-erro").hidden = false; return; }
    salvarSessao(lido, MOTOR.pids, {}, MOTOR);
    entrarCom(lido);
  });

  const daUrl = new URLSearchParams(location.search).get("c")
             || new URLSearchParams(location.hash.replace(/^#/, "?")).get("c");
  const doLink = daUrl ? lerCodigo(MOTOR, daUrl) : null;
  const salvas = lerSessao(r => pidsExigidos(MOTOR, r), MOTOR);

  if (doLink) {
    salvarSessao(doLink, MOTOR.pids, {}, MOTOR);
    entrarCom(doLink);
  } else if (salvas && salvas.completa) {
    Object.assign(resp, salvas.resp);
    Object.assign(livre, salvas.livre);
    const bloco = el("entrar-codigo");
    if (bloco) bloco.hidden = true;
    render(true);
  } else if (salvas) {
    // memória parcial: aproveita o que já foi respondido e pergunta só o que falta
    Object.assign(resp, salvas.resp);
    Object.assign(livre, salvas.livre);
    completando = true;
    faltavam = passos.filter((_p, i) => precisa(i) && MOTOR.pids.includes(passos[i].dataset.q)).length;
    const aviso = el("completando-aviso");
    if (aviso) aviso.hidden = false;
    atual = -1;
    proximo();
    if (atual < passos.length) mostrar(); else render(false);
  } else {
    mostrar();
  }
"""

CSS_MAPA = """
/* ---------- entrega paga ---------- */
.mapa-wrap { max-width: 720px; margin: 0 auto; padding: 34px 20px 90px; }
.mapa-topo { margin-bottom: 26px; }
.mapa-topo h1 { font-size: clamp(26px, 4vw, 38px); letter-spacing: -.02em; margin: 10px 0 8px; }
.mapa-topo p { color: #a29fae; font-size: 15.5px; line-height: 1.6; margin: 0; }
.mapa-barra { height: 3px; border-radius: 3px; background: rgba(255,255,255,.09); overflow: hidden; margin: 22px 0 4px; }
.mapa-barra i { display: block; height: 100%; width: 0; background: var(--roxo); transition: width .3s; }
.m-card { list-style: none; margin-top: 18px; padding: 20px; border-radius: 18px;
          border: 1px solid var(--linha); background: rgba(255,255,255,.035); }
.m-cab { display: flex; align-items: center; gap: 13px; }
.m-logo { border-radius: 9px; flex: none; }
.m-id { flex: 1; min-width: 0; }
.m-nome { display: block; font-size: 18px; font-weight: 600; color: #fff; text-decoration: none; }
.m-nome:hover { color: var(--roxo); }
.m-oq { display: block; margin-top: 3px; font-size: 13.5px; color: #a29fae; line-height: 1.45; }
.m-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 15px; }
.m-quando, .m-custo { padding: 6px 12px; border-radius: 999px; font-size: 12.5px; font-weight: 600; }
.m-quando { background: rgba(193,131,251,.16); color: #d9b9ff; }
.m-custo { background: rgba(255,255,255,.06); color: #c9c6d4; }
.m-bloco { margin-top: 17px; }
.m-rot { display: block; margin-bottom: 7px; font-size: 11px; font-weight: 600;
         letter-spacing: .12em; text-transform: uppercase; color: var(--roxo); }
.m-bloco p { margin: 0; font-size: 15px; line-height: 1.62; color: #ded9ea; }
.m-prompt { margin: 0; padding: 15px 17px; border-radius: 13px; white-space: pre-wrap;
            border: 1px solid var(--linha); background: rgba(0,0,0,.28); color: #ded9ea;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13.5px; line-height: 1.6; }
.m-copiar { margin-top: 10px; padding: 9px 16px; border-radius: 11px; cursor: pointer;
            border: 1px solid var(--linha); background: rgba(255,255,255,.05); color: #e9e7f0;
            font-family: inherit; font-size: 13.5px; font-weight: 600; }
.m-copiar:hover { background: rgba(255,255,255,.1); }
.mapa-wrap .res-corta { margin-top: 24px; }
.res-memoria { margin: 0 0 4px; padding: 11px 15px; border-radius: 12px; font-size: 13.5px;
               line-height: 1.55; color: #a29fae; background: rgba(255,255,255,.04);
               border: 1px solid var(--linha); }
.mapa-wrap .passo:first-of-type { padding-top: 8px; }
.m-recursos { margin: 0; padding: 0; list-style: none; display: grid; gap: 9px; }
.m-recursos li { font-size: 14.5px; line-height: 1.55; color: #ded9ea;
                 padding-left: 13px; border-left: 2px solid rgba(193,131,251,.4); }
.m-recursos b { color: #fff; font-weight: 600; }
/* o que a IA escreve por cima do mapa: só aparece quando o texto chega */
.res-escrevendo { margin: 14px 0 0; font-size: 13.5px; color: var(--roxo); }
.res-escrevendo::after { content: "…"; animation: pisca 1.2s steps(1) infinite; }
@keyframes pisca { 50% { opacity: .25; } }
.res-abertura { margin: 14px 0 0; font-size: 15.5px; line-height: 1.65; color: #ded9ea; }
.res-corta-ia { margin: 10px 0 0; font-size: 14.5px; line-height: 1.6; color: #a29fae; }
@media (prefers-reduced-motion: reduce) { .res-escrevendo::after { animation: none; } }

/* ---------- a venda dentro da entrega ---------- */
.oto[hidden], .asc[hidden], .pres[hidden] { display: none; }
.oto { margin: 10px 0 0; padding: 24px 22px 22px; border-radius: 20px;
       border: 1px solid rgba(193,131,251,.34); background: rgba(193,131,251,.06); }
.oto h2 { margin: 13px 0 8px; font-size: clamp(22px,3.4vw,29px); line-height: 1.18; letter-spacing: -.02em; }
.oto-promessa { margin: 0 0 18px; font-size: 15.5px; line-height: 1.62; color: #ded9ea; }
.oto-lista { margin: 0; padding: 0; list-style: none; display: grid; gap: 13px; }
.oto-lista li { padding-left: 14px; border-left: 2px solid rgba(193,131,251,.45); }
.oto-lista b { display: block; font-size: 15px; font-weight: 600; color: #fff; }
.oto-lista span { display: block; margin-top: 3px; font-size: 14px; line-height: 1.55; color: var(--cinza-claro); }
.oto-conta { margin: 21px 0 0; padding: 15px 16px; border-radius: 14px; background: rgba(0,0,0,.3);
             display: grid; gap: 9px; }
.oto-conta span { display: flex; justify-content: space-between; align-items: baseline; gap: 14px; }
.oto-conta i { font-style: normal; font-size: 14px; color: var(--cinza-claro); }
.oto-conta b { font-size: 15px; font-weight: 600; }
.oto-total { padding-top: 10px; border-top: 1px solid var(--linha); }
.oto-total i { color: #fff; font-weight: 600; }
.oto-total b { font-size: 25px; }
.oto-razao { margin: 14px 0 0; font-size: 13.5px; line-height: 1.55; color: var(--cinza-min); }
.oto .btn-cta, .asc .btn-cta { display: flex; width: 100%; margin-top: 17px; text-align: center;
                               text-decoration: none; }
.oto-nota, .asc-nota { margin: 11px 0 0; text-align: center; font-size: 12.5px; color: var(--cinza-min); }
.oto-pular { display: block; width: 100%; margin-top: 15px; padding: 14px; cursor: pointer;
             border-radius: 14px; border: 1px solid var(--linha); background: rgba(255,255,255,.05);
             color: #e9e7f0; font-family: inherit; font-size: 15px; font-weight: 600; }
.oto-pular:hover { background: rgba(255,255,255,.1); }

.asc { margin: 32px 0 0; padding: 20px; border-radius: 18px;
       border: 1px solid rgba(193,131,251,.3); background: rgba(193,131,251,.05); }
.asc-rot { display: block; font-size: 11px; font-weight: 600; letter-spacing: .12em;
           text-transform: uppercase; color: var(--roxo); }
.asc h3 { margin: 10px 0 7px; font-size: 19px; }
.asc p { margin: 0; font-size: 14.5px; line-height: 1.6; color: #ded9ea; }
.asc p.asc-preco { display: flex; align-items: baseline; flex-wrap: wrap; gap: 4px 10px; margin: 15px 0 0; }
.asc-preco b { font-size: 26px; }
.asc-preco i { font-style: normal; font-size: 13px; color: var(--cinza-min); }

.pres { margin: 32px 0 0; padding: 20px; border-radius: 18px;
        border: 1px solid var(--linha); background: rgba(255,255,255,.03); }
.pres h3 { margin: 0 0 7px; font-size: 19px; }
.pres-sub { margin: 0 0 15px; font-size: 14px; line-height: 1.6; color: var(--cinza-claro); }
.pres-opcoes { display: grid; gap: 9px; }
.pres-opcoes[hidden] { display: none; }
.pres .opc { font-size: 14.5px; padding: 14px 17px; }
.pres .campo-aberto { margin-top: 12px; }
.pres #pres-enviar { margin-top: 14px; }
.pres .btn[hidden] { display: none; }
/* nasce desabilitado: sem isto ele parece clicável antes de a pessoa escolher */
.pres .btn:disabled { opacity: .5; cursor: default; }
.pres-pronto { margin: 14px 0 0; font-size: 14.5px; line-height: 1.6; color: var(--roxo); }
"""

html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>O seu mapa · Qual IA Usar?</title>
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#0c0a10">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<style>{CSS}{CSS_MAPA}</style>
</head>
<body>
<main class="mapa-wrap">
  <header class="mapa-topo">
    <span class="selo-rosa">Acesso liberado</span>
    <h1>O seu mapa</h1>
    <p class="crenca crenca-solta">{escape(DG["crencaCurta"])}</p>
    <p id="mapa-sub">Responde de novo, com calma. Desta vez vem tudo: o custo real de cada uma,
       o primeiro passo e o prompt pronto para copiar.</p>
    <div class="mapa-barra"><i id="barra-fill"></i></div>
  </header>

  <div class="entrar-codigo" id="entrar-codigo">
    <p><b>Já respondeu no celular?</b> Cola aqui o código que apareceu no fim do diagnóstico
       e o seu mapa abre sem refazer nada.</p>
    <input id="codigo-campo" type="text" inputmode="latin" autocomplete="off"
           placeholder="2 6 A K - 4 6 A K - 4 6 A K" maxlength="26">
    <button type="button" class="btn btn-p" id="codigo-usar">Abrir com o meu código</button>
    <p class="erro" id="codigo-erro" hidden>Esse código não abriu. Confere se copiou inteiro, ou responde abaixo que leva 2 minutos.</p>
  </div>
  <p class="completando-aviso" id="completando-aviso" hidden>O diagnóstico ganhou perguntas novas desde
     que você respondeu. As suas respostas continuam aqui: falta só o que é novo.</p>
  <form id="quiz">{perguntas_html}</form>

{oto_html}
  <div id="resultado" role="region" aria-live="polite" aria-label="O seu mapa" hidden>
    <div class="res-topo">
      <span class="selo-rosa">Sua stack</span>
      <h3 id="res-titulo" tabindex="-1">Estas são as suas 3</h3>
      <p id="res-perfil"></p>
      <div class="res-codigo" id="res-codigo" hidden>
        <span class="res-codigo-rot">O código do seu diagnóstico</span>
        <code id="res-codigo-valor"></code>
        <button type="button" class="m-copiar" data-alvo="res-codigo-valor">Copiar</button>
        <a class="m-copiar" id="res-codigo-zap" target="_blank" rel="noopener">Guardar no WhatsApp</a>
        <p class="res-codigo-ajuda">Ele guarda as suas respostas. O acesso à compra continua sendo feito pelo seu e-mail.</p>
      </div>
    </div>
    <p class="res-memoria" id="res-memoria" hidden>Montado com as respostas que você deu no
       site. Mudou alguma coisa? Refaz ali embaixo.</p>
    <p class="res-escrevendo" id="res-escrevendo" role="status" hidden>Escrevendo a sua
       versão, com o prompt de cada uma para o seu caso.</p>
    <p class="res-abertura" id="res-abertura" hidden></p>
    <ol class="res-stack" id="res-stack"></ol>
    <div class="res-corta" id="res-corta"></div>
    <p class="res-corta-ia" id="res-corta-ia" hidden></p>{asc_html}{pres_html}
    <button type="button" class="refazer" id="refazer">Refazer com outras respostas</button>
  </div>
</main>
<script>const MOTOR = {json.dumps(motor, ensure_ascii=False, separators=(",", ":"))};{MOTOR_JS}{ESPELHO_JS}{CODIGO_JS}{SESSAO_JS}{JS}</script>
</body>
</html>
"""

SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(html, encoding="utf-8")

API_MOTOR.parent.mkdir(parents=True, exist_ok=True)
API_MOTOR.write_text(
    "// GERADO por _build/gerar_mapa.py. Editar aqui é perder o trabalho no próximo build.\n"
    f"export const MOTOR = {json.dumps(motor_api, ensure_ascii=False, separators=(',', ':'))};\n"
    f"{MOTOR_JS}\n"
    "export { calcularStack, valePergunta, pidsExigidos, limparOrfas };\n",
    encoding="utf-8")

print(f"gerado: _private/mapa.html  ({len(html):,} bytes)")
print(f"  {n_perguntas} perguntas, {len(F)} ferramentas com passo, prompt e custo real")
print("  noindex ligado. A URL não é divulgada: quem chega aqui é quem comprou.")
if CHECKOUT_UPSELL:
    print(f"  upsell no ar: tela pós-compra e CTA de ascensão por R$ {LIQUIDO}")
else:
    print("  AVISO: CHECKOUT_UPSELL vazia. A tela pós-compra e o CTA de ascensão não saem,\n"
          "         e o mapa abre direto. Preencha em _build/config.py para ligar.")
print(f"gerado: _lib/motor.mjs  ({API_MOTOR.stat().st_size:,} bytes) para a /api/mapa")
