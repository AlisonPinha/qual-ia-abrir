"""
Gera public/plano/index.html: a entrega do upsell de R$ 197.

O /mapa diz quais são as três e por quê. Aqui elas entram na semana da pessoa e
rodam em cima de um trabalho real dela. É a fronteira decidida em 19/08: o front
escreve para o seu perfil, o upsell roda no seu material.

Reusa o mesmo questionário, o mesmo motor e a mesma memória do /mapa, pelo mesmo
motivo de sempre: as três páginas não podem divergir sobre o que perguntam nem
sobre o que calculam.

Uso: python3 _build/gerar_plano.py
"""

import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BUILD = RAIZ / "_build"
SAIDA = RAIZ / "public" / "plano" / "index.html"

CSS = (BUILD / "estilo.css").read_text(encoding="utf-8")
MOTOR_JS = (BUILD / "motor.js").read_text(encoding="utf-8")
ESPELHO_JS = (BUILD / "espelho.js").read_text(encoding="utf-8")
CODIGO_JS = (BUILD / "codigo.js").read_text(encoding="utf-8")
SESSAO_JS = (BUILD / "sessao.js").read_text(encoding="utf-8")

sys.path.insert(0, str(BUILD))
from config import ANALITICO_URL  # noqa: E402
import questionario  # noqa: E402

d = json.loads((BUILD / "dados.json").read_text(encoding="utf-8"))
F = d["ferramentas"]
DG = d["diagnostico"]
SEM = d["semana"]
UP = d["upsell"]

perguntas_html, regras, n_perguntas = questionario.montar(DG["perguntas"], DG["aberta"])

# ---------- motor completo: a semana precisa saber custo, recurso e ordem ----------
motor = {
    "pesos": {p[0]: [pesos for _t, pesos in p[2]] for p in DG["perguntas"]},
    "rotulos": {p[0]: [texto for texto, _p in p[2]] for p in DG["perguntas"]},
    "titulos": {p[0]: p[1] for p in DG["perguntas"]},
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
    "dias": SEM["dias"],
    "ferramentas": {
        n: {
            "curto": DG["acesso"][n]["curto"],
            "faixa": DG["acesso"][n]["faixa"],
            "free": DG["acesso"][n]["free"],
            "generalista": DG["acesso"][n].get("generalista", False),
            "logo": F[n]["logo"],
            "url": F[n]["url"],
            "oq": F[n]["oq"],
            "custo": DG["acesso"][n]["custo"],
            "recursos": DG["recursos"].get(n, []),
        }
        for n in F
    },
}

JS = r"""
  const el = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

  const quiz = el("quiz");
  const passos = [...quiz.querySelectorAll(".passo")];
  const resp = {};
  const livre = {};
  let atual = 0;

  const vale = i => valePergunta(MOTOR, passos[i].dataset.q, resp);
  const ehPergunta = i => MOTOR.pids.includes(passos[i].dataset.q);

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
    botao.disabled = true;
    setTimeout(() => { status.textContent = MOTOR.espelhoPronto; botao.disabled = false; }, 1600);
  };

  const mostrar = () => {
    passos.forEach((p, i) => { p.hidden = i !== atual; });
    if (passos[atual].dataset.q === "break_espelho") prepararEspelho();
    const fila = passos.map((_p, i) => i).filter(vale);
    const pos = fila.indexOf(atual);
    el("barra-fill").style.width = ((pos + 0.4) / fila.length * 100) + "%";
    const num = passos[atual].querySelector(".num");
    if (num && ehPergunta(atual))
      num.textContent = fila.filter(i => i <= atual && ehPergunta(i)).length + " de " + totalPerguntas();
  };

  const proximo = () => { do { atual++; } while (atual < passos.length && !vale(atual)); };

  // ---------- a semana ----------
  let stackAtual = null;

  function preencher(texto, stack) {
    const alvo = Object.keys(resp).find(q => /(^|_)tarefa$/.test(q));
    const tarefa = alvo ? MOTOR.rotulos[alvo][resp[alvo]].toLowerCase() : "a tarefa que mais te toma tempo";
    return texto
      .replace(/\{F1\}/g, stack[0] ? stack[0].nome : "")
      .replace(/\{F2\}/g, stack[1] ? stack[1].nome : "")
      .replace(/\{F3\}/g, stack[2] ? stack[2].nome : "")
      .replace(/\{tarefa\}/g, tarefa);
  }

  function render(daMemoria) {
    const { stack, corta } = calcularStack(MOTOR, resp);
    stackAtual = stack;
    if (!daMemoria) salvarSessao(resp, MOTOR.pids, livre);
    enviarAnalitico(MOTOR.analitico, "plano", MOTOR, resp, stack, corta, livre);

    const [qArea] = MOTOR.perfil;
    el("plano-perfil").textContent =
      `${MOTOR.rotulos[qArea][resp[qArea]]} · ${stack.map(s => s.nome).join(", ")}`;

    el("dias").innerHTML = MOTOR.dias.map(dia => `
      <li class="dia" id="dia${dia.n}">
        <div class="dia-cab">
          <span class="dia-n">Dia ${dia.n}</span>
          <h3>${esc(preencher(dia.titulo, stack))}</h3>
        </div>
        <p class="dia-obj">${esc(preencher(dia.objetivo, stack))}</p>
        <p class="dia-tarefa"><b>O que fazer hoje:</b> ${esc(preencher(dia.tarefa, stack))}</p>
        <p class="dia-entrega"><b>No fim do dia você tem:</b> ${esc(preencher(dia.entrega, stack))}</p>
        <div class="dia-ia" id="dia-ia-${dia.n}" hidden></div>
      </li>`).join("");

    el("config").innerHTML = stack.map((s, i) => `
      <li class="cfg">
        <div class="cfg-cab">
          <img class="m-logo" src="/logos/${esc(s.logo)}" alt="" width="30" height="30">
          <b>${esc(s.nome)}</b>
          <span class="cfg-quando">${esc(s.quando)}</span>
        </div>
        <pre class="cfg-texto" id="cfg${i}">O texto de configuração desta é escrito para o seu caso quando a página carrega.</pre>
        <button type="button" class="m-copiar" data-alvo="cfg${i}">Copiar</button>
      </li>`).join("");

    el("material-alvo").textContent = stack[0] ? stack[0].nome : "";
    el("quiz").hidden = true;
    el("plano").hidden = false;
    redigir();
  }

  // ---------- a IA escreve por cima do esqueleto, conforme o ADR-0001 ----------
  // Duas chamadas em vez de uma: juntas, os sete dias e as três configurações não cabem
  // nos 60s da function, e o stream morria no meio do quarto dia.
  async function redigir() {
    const aviso = el("plano-escrevendo");
    aviso.hidden = false;
    aviso.textContent = "Escrevendo a sua semana...";
    await pedir("semana");
    aviso.textContent = "Escrevendo a configuração das suas 3...";
    await pedir("config");
    aviso.hidden = true;
  }

  async function pedir(modo) {
    const ctrl = new AbortController();
    const relogio = setTimeout(() => ctrl.abort(), 75000);
    try {
      const r = await fetch("/api/plano", {
        method: "POST", signal: ctrl.signal,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ modo, resp, livre }),
      });
      if (r.status === 429 || r.status === 503 || !r.ok || !r.body) return;
      const leitor = r.body.getReader();
      const dec = new TextDecoder();
      let buffer = "";
      for (;;) {
        const { done, value } = await leitor.read();
        if (done) break;
        buffer += dec.decode(value, { stream: true });
        aplicarSemana(buffer);
      }
      aplicarSemana(buffer);
    } catch (e) {
      /* o esqueleto já está na tela: a semana não depende da IA para existir */
    } finally {
      clearTimeout(relogio);
    }
  }

  function aplicarSemana(buffer) {
    const partes = buffer.split(/\[\[([A-Z]+\d?)\]\]/);
    for (let i = 1; i < partes.length; i += 2) {
      const nome = partes[i], texto = (partes[i + 1] || "").trim();
      if (!texto) continue;
      const dia = nome.match(/^DIA(\d)$/);
      if (dia) {
        const no = el("dia-ia-" + dia[1]);
        if (no) { no.textContent = texto; no.hidden = false; }
      }
      const cfg = nome.match(/^CFG(\d)$/);
      if (cfg) {
        const no = el("cfg" + (Number(cfg[1]) - 1));
        if (no) no.textContent = texto;
      }
    }
  }

  // ---------- o trabalho da pessoa, rodado dentro da ferramenta certa ----------
  el("material-rodar").addEventListener("click", async () => {
    const campo = el("material");
    const texto = campo.value.trim();
    const saida = el("material-saida");
    const botao = el("material-rodar");
    if (texto.length < 80) {
      saida.textContent = "Cola um trabalho seu de verdade, com pelo menos umas linhas: é em cima dele que a ferramenta vai rodar.";
      saida.hidden = false;
      return;
    }
    botao.disabled = true;
    botao.textContent = "Rodando...";
    saida.textContent = "";
    saida.hidden = false;
    const ctrl = new AbortController();
    const relogio = setTimeout(() => ctrl.abort(), 90000);
    try {
      const r = await fetch("/api/plano", {
        method: "POST", signal: ctrl.signal,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ modo: "rodar", resp, livre, material: texto.slice(0, 18000) }),
      });
      if (!r.ok || !r.body) throw new Error(r.status);
      const leitor = r.body.getReader();
      const dec = new TextDecoder();
      for (;;) {
        const { done, value } = await leitor.read();
        if (done) break;
        saida.textContent += dec.decode(value, { stream: true });
      }
      el("material-copiar").hidden = false;
    } catch (e) {
      saida.textContent = "Não deu para rodar agora. Tenta de novo em alguns minutos: o seu material continua aqui.";
    } finally {
      clearTimeout(relogio);
      botao.disabled = false;
      botao.textContent = "Rodar na ferramenta certa";
    }
  });

  // ---------- copiar ----------
  document.addEventListener("click", e => {
    const b = e.target.closest(".m-copiar, #material-copiar");
    if (!b) return;
    const alvo = b.id === "material-copiar" ? el("material-saida") : el(b.dataset.alvo);
    navigator.clipboard.writeText(alvo.textContent).then(() => {
      const antes = b.textContent;
      b.textContent = "Copiado";
      setTimeout(() => { b.textContent = antes; }, 1400);
    });
  });

  // ---------- quiz, para quem chega sem memória ----------
  const abrirCampo = (b) => {
    const passo = b.closest(".passo");
    const campo = passo.querySelector(".campo-aberto");
    if (!campo || b !== b.parentNode.lastElementChild) {
      if (campo) { campo.hidden = true; delete livre[passo.dataset.q]; }
      return false;
    }
    campo.hidden = false;
    campo.querySelector("input").focus();
    return true;
  };

  for (const b of quiz.querySelectorAll(".opc")) {
    b.addEventListener("click", () => {
      resp[b.dataset.q] = +b.dataset.i;
      for (const irmao of b.parentNode.children)
        irmao.setAttribute("aria-pressed", String(irmao === b));
      if (abrirCampo(b)) return;
      proximo();
      if (atual < passos.length) mostrar(); else render(false);
    });
  }
  for (const b of quiz.querySelectorAll(".btn-livre")) {
    b.addEventListener("click", () => {
      const passo = b.closest(".passo");
      const texto = passo.querySelector("input").value.trim();
      if (texto) livre[passo.dataset.q] = texto.slice(0, 120);
      proximo();
      if (atual < passos.length) mostrar(); else render(false);
    });
  }

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

CSS_PLANO = """
.plano-wrap { max-width: 760px; margin: 0 auto; padding: 26px 18px 80px; }
.plano-topo h1 { font-size: 30px; line-height: 1.15; margin: 10px 0 6px; }
#plano-perfil { color: var(--cinza-claro); font-size: 14px; margin: 0 0 18px; }
.plano-barra { height: 4px; border-radius: 3px; background: rgba(255,255,255,.08); overflow: hidden; margin-top: 14px; }
.plano-barra i { display: block; height: 100%; width: 0; background: var(--roxo); transition: width .25s ease; }

.bloco { margin: 34px 0 0; }
.bloco > h2 { font-size: 20px; margin: 0 0 4px; }
.bloco > p.sub { color: var(--cinza-min); font-size: 14px; margin: 0 0 16px; }

#dias { list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }
.dia { border: 1px solid rgba(255,255,255,.09); border-radius: 15px; padding: 16px 17px; background: rgba(255,255,255,.02); }
.dia-cab { display: flex; align-items: baseline; gap: 10px; }
.dia-n { font-size: 12px; font-weight: 700; color: var(--roxo); letter-spacing: .04em; text-transform: uppercase; }
.dia h3 { font-size: 17px; margin: 0; }
.dia-obj { color: var(--cinza-claro); font-size: 14px; margin: 7px 0 10px; }
.dia-tarefa, .dia-entrega { font-size: 14.5px; line-height: 1.6; margin: 6px 0; }
.dia-tarefa b, .dia-entrega b { color: #fff; }
.dia-ia { margin-top: 10px; padding-top: 10px; border-top: 1px dashed rgba(255,255,255,.12);
  font-size: 14.5px; line-height: 1.65; color: #d7d3e0; white-space: pre-wrap; }

#config { list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }
.cfg { border: 1px solid rgba(255,255,255,.09); border-radius: 15px; padding: 15px 16px; }
.cfg-cab { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.cfg-quando { margin-left: auto; font-size: 12px; color: var(--cinza-min); }
.cfg-texto { white-space: pre-wrap; font-size: 13.5px; line-height: 1.6; margin: 0 0 10px;
  background: rgba(0,0,0,.28); border-radius: 11px; padding: 13px 14px; font-family: ui-monospace, monospace; }

#material { width: 100%; min-height: 170px; border-radius: 13px; padding: 14px;
  background: rgba(0,0,0,.3); color: #fff; border: 1px solid rgba(255,255,255,.14);
  font-size: 14.5px; line-height: 1.6; resize: vertical; }
#material-rodar { margin-top: 12px; }
#material-saida { white-space: pre-wrap; margin-top: 16px; padding: 16px;
  border-radius: 13px; background: rgba(193,131,251,.07);
  border: 1px solid rgba(193,131,251,.22); font-size: 14.5px; line-height: 1.7; }
.plano-escrevendo { font-size: 13px; color: var(--roxo); margin: 10px 0 0; }
"""

html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>A sua primeira semana · Qual IA Usar?</title>
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#0c0a10">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<style>{CSS}{CSS_PLANO}</style>
</head>
<body>
<main class="plano-wrap">
  <header class="plano-topo">
    <span class="selo-rosa">Acesso liberado</span>
    <h1>{SEM["promessa"]}</h1>
    <p id="plano-perfil"></p>
    <div class="plano-barra"><i id="barra-fill"></i></div>
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

  <div id="plano" hidden>
    <p class="plano-escrevendo" id="plano-escrevendo" hidden>Escrevendo a sua semana...</p>

    <section class="bloco">
      <h2>Os seus 7 dias</h2>
      <p class="sub">Vinte minutos por dia, na ordem. Cada dia entrega uma coisa que fica.</p>
      <ol id="dias"></ol>
    </section>

    <section class="bloco">
      <h2>Um trabalho seu, rodado aqui</h2>
      <p class="sub">Cola um material real: um texto, um processo, um caso, um orçamento.
        Ele volta rodado dentro da <b id="material-alvo"></b>, que é a primeira da sua stack.
        Não é modelo para preencher.</p>
      <textarea id="material" placeholder="Cola aqui o seu material" maxlength="18000"></textarea>
      <button type="button" class="btn btn-p" id="material-rodar">Rodar na ferramenta certa</button>
      <div id="material-saida" hidden></div>
      <button type="button" class="m-copiar" id="material-copiar" hidden>Copiar o resultado</button>
    </section>

    <section class="bloco">
      <h2>As suas 3 configuradas</h2>
      <p class="sub">O texto exato para colar nas instruções de cada uma, escrito para o seu caso.</p>
      <ol id="config"></ol>
    </section>

    <section class="bloco">
      <h2>Revisão quando mudar</h2>
      <p class="sub">{UP["entregaveis"][3][1]}</p>
    </section>
  </div>
</main>
<script>const MOTOR = {json.dumps(motor, ensure_ascii=False, separators=(",", ":"))};{MOTOR_JS}{ESPELHO_JS}{CODIGO_JS}{SESSAO_JS}{JS}</script>
</body>
</html>
"""

SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(html, encoding="utf-8")
print(f"{SAIDA.relative_to(RAIZ)}: {len(html) // 1024} KB, {len(SEM['dias'])} dias")
