#!/usr/bin/env python3
"""
Gera public/mapa/index.html: a entrega paga do "Qual IA Usar?".

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
SAIDA = RAIZ / "public" / "mapa" / "index.html"

d = json.loads((BUILD / "dados.json").read_text(encoding="utf-8"))
CSS = (BUILD / "estilo.css").read_text(encoding="utf-8")
MOTOR_JS = (BUILD / "motor.js").read_text(encoding="utf-8")
SESSAO_JS = (BUILD / "sessao.js").read_text(encoding="utf-8")
ESPELHO_JS = (BUILD / "espelho.js").read_text(encoding="utf-8")
CODIGO_JS = (BUILD / "codigo.js").read_text(encoding="utf-8")
sys.path.insert(0, str(BUILD))
from config import ANALITICO_URL  # noqa: E402
import questionario  # noqa: E402
F = d["ferramentas"]
DG = d["diagnostico"]

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

JS = r"""
  const el = id => document.getElementById(id);
  const quiz = el("quiz");
  const passos = [...quiz.querySelectorAll(".passo")];
  const resp = {};
  const livre = {};          // o que a pessoa escreveu quando nenhuma opção era a dela
  let atual = 0;

  // trilha por área: o passo que não é da área respondida não aparece nem conta
  const vale = i => valePergunta(MOTOR, passos[i].dataset.q, resp);
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
    passos.forEach((p, i) => { p.hidden = i !== atual; });
    // a tela de espelho carrega, repete as respostas e só então libera o resultado
    if (passos[atual].dataset.q === "break_espelho") prepararEspelho();
    const fila = passos.map((_p, i) => i).filter(vale);
    const pos = fila.indexOf(atual);
    el("barra-fill").style.width = ((pos + 0.4) / fila.length * 100) + "%";
    const num = passos[atual].querySelector(".num");
    if (num && ehPergunta(atual))
      // o total sai da fila, não de uma constante: com pergunta condicional, um número
      // fixo mentiria para quem pula duas, e contador que mente faz abandonar o quiz
      num.textContent = fila.filter(i => i <= atual && ehPergunta(i)).length
                      + " de " + totalPerguntas();
  };

  const proximo = () => { do { atual++; } while (atual < passos.length && !vale(atual)); };

  const esc = s => String(s).replace(/[&<>"]/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function render(daMemoria) {
    const { stack, corta } = calcularStack(MOTOR, resp);
    if (!daMemoria) salvarSessao(resp, MOTOR.pids, livre);
    enviarAnalitico(MOTOR.analitico, "mapa", MOTOR, resp, stack, corta, livre);
    el("res-memoria").hidden = !daMemoria;
    if (daMemoria) el("mapa-sub").textContent =
      "Suas respostas do site já estão aqui. Abaixo vem tudo: o custo real de cada uma, "
      + "o primeiro passo e o prompt pronto para copiar.";
    const [qArea, qOrc] = MOTOR.perfil;
    el("res-perfil").textContent =
      `${MOTOR.rotulos[qArea][resp[qArea]]} · ${MOTOR.rotulos[qOrc][resp[qOrc]]}.`;

    const codigo = gerarCodigo(MOTOR, resp);
    if (codigo) {
      el("res-codigo-valor").textContent = codigo;
      el("res-codigo").hidden = false;
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
    el("resultado").hidden = false;
    el("barra-fill").style.width = "100%";
    el("res-titulo").focus();
    redigir(resp, livre);
  }

  // ---------- a camada de IA (ADR-0001: as regras decidem, a IA redige) ----------
  //
  // Tudo acima já está na tela e completo. O que vem daqui é a versão escrita para
  // esta pessoa, colocada por cima. Se a chamada falhar, demorar ou vier pela metade,
  // cada bloco volta ao que era: o mapa não depende disso para ser entregue.

  const IA_CHAVE = "qia:ia";
  const TEM_PRECO = /R\$|US\$|\d+\s*(d[óo]lares|reais)/i;
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
    salvarSessao(lido, MOTOR.pids, {});
    entrarCom(lido);
  });

  const daUrl = new URLSearchParams(location.search).get("c")
             || new URLSearchParams(location.hash.replace(/^#/, "?")).get("c");
  const doLink = daUrl ? lerCodigo(MOTOR, daUrl) : null;
  const salvas = lerSessao(r => pidsExigidos(MOTOR, r));

  if (doLink) {
    salvarSessao(doLink, MOTOR.pids, {});
    entrarCom(doLink);
  } else if (salvas) {
    Object.assign(resp, salvas.resp);
    Object.assign(livre, salvas.livre);
    const bloco = el("entrar-codigo");
    if (bloco) bloco.hidden = true;
    render(true);
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
  <form id="quiz">{perguntas_html}</form>

  <div id="resultado" role="region" aria-live="polite" aria-label="O seu mapa" hidden>
    <div class="res-topo">
      <span class="selo-rosa">Sua stack</span>
      <h3 id="res-titulo" tabindex="-1">Estas são as suas 3</h3>
      <p id="res-perfil"></p>
      <div class="res-codigo" id="res-codigo" hidden>
        <span class="res-codigo-rot">O seu código de acesso</span>
        <code id="res-codigo-valor"></code>
        <button type="button" class="m-copiar" data-alvo="res-codigo-valor">Copiar</button>
        <p class="res-codigo-ajuda">Com ele você abre este mapa em qualquer aparelho, sem responder de novo.</p>
      </div>
    </div>
    <p class="res-memoria" id="res-memoria" hidden>Montado com as respostas que você deu no
       site. Mudou alguma coisa? Refaz ali embaixo.</p>
    <p class="res-escrevendo" id="res-escrevendo" role="status" hidden>Escrevendo a sua
       versão, com o prompt de cada uma para o seu caso.</p>
    <p class="res-abertura" id="res-abertura" hidden></p>
    <ol class="res-stack" id="res-stack"></ol>
    <div class="res-corta" id="res-corta"></div>
    <p class="res-corta-ia" id="res-corta-ia" hidden></p>
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
    "export { calcularStack, valePergunta, pidsExigidos };\n",
    encoding="utf-8")

print(f"gerado: public/mapa/index.html  ({len(html):,} bytes)")
print(f"  {n_perguntas} perguntas, {len(F)} ferramentas com passo, prompt e custo real")
print("  noindex ligado. A URL não é divulgada: quem chega aqui é quem comprou.")
print(f"gerado: _lib/motor.mjs  ({API_MOTOR.stat().st_size:,} bytes) para a /api/mapa")
