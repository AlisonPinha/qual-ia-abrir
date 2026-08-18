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
sys.path.insert(0, str(BUILD))
from config import ANALITICO_URL  # noqa: E402
F = d["ferramentas"]
DG = d["diagnostico"]

# ---------- perguntas: mesmo HTML do index, incluindo os breaks ----------

perguntas_html = []
n_perguntas = sum(1 for pid, _t, _o in DG["perguntas"] if not pid.startswith("break"))
n_pergunta = 0
for i, (pid, titulo, opcoes) in enumerate(DG["perguntas"], start=1):
    botoes = "".join(
        f'<button type="button" class="opc" data-q="{escape(pid, quote=True)}" data-i="{j}">'
        f'{escape(texto)}</button>'
        for j, (texto, _pesos) in enumerate(opcoes)
    )
    if pid.startswith("break"):
        manchete, _, corpo = titulo.partition(" | ")
        perguntas_html.append(
            f'<fieldset class="passo passo-break" data-passo="{i}" data-q="{escape(pid, quote=True)}">'
            f'<legend>{escape(manchete)}</legend>'
            f'<p class="break-corpo">{escape(corpo)}</p>'
            f'<div class="opcoes">{botoes}</div></fieldset>'
        )
        continue
    n_pergunta += 1
    perguntas_html.append(
        f'<fieldset class="passo" data-passo="{i}" data-q="{escape(pid, quote=True)}">'
        f'<legend><span class="num">{n_pergunta} de {n_perguntas}</span>{escape(titulo)}</legend>'
        f'<div class="opcoes">{botoes}</div></fieldset>'
    )

# ---------- motor completo: aqui não se omite nada ----------

motor = {
    "pesos": {pid: [pesos for _t, pesos in opcoes] for pid, _tit, opcoes in DG["perguntas"]},
    "rotulos": {pid: [texto for texto, _p in opcoes] for pid, _tit, opcoes in DG["perguntas"]},
    "ordem": DG["ordem"],
    "cabem": DG["cabem"],
    "celular": DG["celular"],
    "perfil": DG["perfil"],
    "analitico": ANALITICO_URL,
    "pids": [pid for pid, _t, _o in DG["perguntas"] if not pid.startswith("break")],
    "ferramentas": {
        n: {
            "curto": DG["acesso"][n]["curto"],
            "faixa": DG["acesso"][n]["faixa"],
            # o que o index esconde:
            "logo": F[n]["logo"],
            "url": F[n]["url"],
            "oq": F[n]["oq"],
            "custo": DG["acesso"][n]["custo"],
            "passo": DG["comeco"][n][0],
            "prompt": DG["comeco"][n][1],
        }
        for n in F
    },
}

JS = r"""
  const el = id => document.getElementById(id);
  const quiz = el("quiz");
  const passos = [...quiz.querySelectorAll(".passo")];
  const resp = {};
  let atual = 0;

  const mostrar = () => {
    passos.forEach((p, i) => { p.hidden = i !== atual; });
    el("barra-fill").style.width = ((atual + 0.4) / passos.length * 100) + "%";
  };

  const esc = s => String(s).replace(/[&<>"]/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function render(daMemoria) {
    const { stack, corta } = calcularStack(MOTOR, resp);
    if (!daMemoria) salvarSessao(resp, MOTOR.pids);
    enviarAnalitico(MOTOR.analitico, "mapa", MOTOR, resp, stack, corta);
    el("res-memoria").hidden = !daMemoria;
    if (daMemoria) el("mapa-sub").textContent =
      "Suas respostas do site já estão aqui. Abaixo vem tudo: o custo real de cada uma, "
      + "o primeiro passo e o prompt pronto para copiar.";
    const [qArea, qOrc] = MOTOR.perfil;
    el("res-perfil").textContent =
      `${MOTOR.rotulos[qArea][resp[qArea]]} · ${MOTOR.rotulos[qOrc][resp[qOrc]]}.`;

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
  }

  for (const b of quiz.querySelectorAll(".opc")) {
    b.addEventListener("click", () => {
      resp[b.dataset.q] = +b.dataset.i;
      for (const irmao of b.parentNode.children)
        irmao.setAttribute("aria-pressed", String(irmao === b));
      atual++;
      if (atual < passos.length) mostrar(); else render();
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
  const salvas = lerSessao(MOTOR.pids);
  if (salvas) {
    Object.assign(resp, salvas);
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

  <form id="quiz">{"".join(perguntas_html)}</form>

  <div id="resultado" role="region" aria-live="polite" aria-label="O seu mapa" hidden>
    <div class="res-topo">
      <span class="selo-rosa">Sua stack</span>
      <h3 id="res-titulo" tabindex="-1">Estas são as suas 3</h3>
      <p id="res-perfil"></p>
    </div>
    <p class="res-memoria" id="res-memoria" hidden>Montado com as respostas que você deu no
       site. Mudou alguma coisa? Refaz ali embaixo.</p>
    <ol class="res-stack" id="res-stack"></ol>
    <div class="res-corta" id="res-corta"></div>
    <button type="button" class="refazer" id="refazer">Refazer com outras respostas</button>
  </div>
</main>
<script>const MOTOR = {json.dumps(motor, ensure_ascii=False, separators=(",", ":"))};{MOTOR_JS}{SESSAO_JS}{JS}</script>
</body>
</html>
"""

SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(html, encoding="utf-8")
print(f"gerado: public/mapa/index.html  ({len(html):,} bytes)")
print(f"  {n_perguntas} perguntas, {len(F)} ferramentas com passo, prompt e custo real")
print("  noindex ligado. A URL não é divulgada: quem chega aqui é quem comprou.")
