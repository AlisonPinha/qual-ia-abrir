#!/usr/bin/env python3
"""
Gera public/index.html com todo o conteúdo já escrito no HTML.

O motivo de existir: antes a lista era montada por JavaScript no navegador, então
o robô do Google, o gerador de preview do WhatsApp e leitores de tela recebiam uma
página vazia. Agora o JS só liga a busca e o filtro sobre o que já está no HTML.

Fonte dos dados: _build/dados.json
Estilo:          _build/estilo.css
Uso:             python3 _build/gerar.py && vercel deploy --prod --yes
"""

import json
import pathlib
import unicodedata
from html import escape

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BUILD = RAIZ / "_build"
SAIDA = RAIZ / "public" / "index.html"
SITE = "https://qual-ia-abrir.vercel.app"

d = json.loads((BUILD / "dados.json").read_text(encoding="utf-8"))
CSS = (BUILD / "estilo.css").read_text(encoding="utf-8")
F = d["ferramentas"]


def sem_acento(s: str) -> str:
    """Índice de busca: minúsculo e sem diacrítico, para 'video' achar 'vídeo'."""
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")


def ico(nome: str, classe: str = "", lado: int = 26) -> str:
    cls = f"ico {classe}".strip()
    return (f'<img class="{cls}" src="/logos/{F[nome]["logo"]}" alt="" '
            f'width="{lado}" height="{lado}" loading="lazy">')


def link_ferramenta(nome: str) -> str:
    return (f'<a class="ferramenta" href="{F[nome]["url"]}" target="_blank" rel="noopener">'
            f'{ico(nome)}{escape(nome)}</a>')


# ---------- lista de tarefas ----------

total = 0
grupos_html = []

for titulo, linhas in d["grupos"]:
    itens = []
    for tarefa, ferr, porque, no_reel in linhas:
        total += 1
        busca = sem_acento(f"{tarefa} {ferr} {porque} {titulo}")
        selo = '<span class="selo">no reel</span>' if no_reel else ""
        itens.append(
            f'<li class="linha" data-busca="{escape(busca, quote=True)}" data-ferr="{escape(ferr, quote=True)}">'
            f'<span class="tarefa">{escape(tarefa)}{selo}</span>'
            f'{link_ferramenta(ferr)}'
            f'<span class="porque">{escape(porque)}</span>'
            f'</li>'
        )
    grupos_html.append(
        f'<section class="grupo"><h2>{escape(titulo)}</h2>'
        f'<ul class="linhas">{"".join(itens)}</ul></section>'
    )

# ---------- demais blocos ----------

fileira = "".join(
    f'<img src="/logos/{F[n]["logo"]}" alt="" width="30" height="30">'
    for n in F if n != "Claude Code"
)

chips = "".join(
    f'<button type="button" class="chip" aria-pressed="false" data-ferr="{escape(n, quote=True)}">'
    f'<img src="/logos/{F[n]["logo"]}" alt="" width="18" height="18">{escape(n)}</button>'
    for n in F if n != "Claude Code"
)

desempates = "".join(
    f'<div class="desempate"><h3>{escape(t)}</h3><div class="versus">' +
    "".join(f'<div class="lado"><span class="nome">{ico(n)}{escape(n)}</span>'
            f'<span class="quando">{txt}</span></div>' for n, txt in lados) +
    "</div></div>"
    for t, lados in d["desempates"]
)

cards = "".join(
    f'<a class="card" href="{F[n]["url"]}" target="_blank" rel="noopener">'
    f'{ico(n, "g", 44)}'
    f'<span class="nome">{escape(n)} <span class="seta">↗</span></span>'
    f'<span class="oq">{escape(F[n]["oq"])}</span></a>'
    for n in F
)

cinco = "".join(
    f'<li>{ico(n)}<span class="nome">{escape(n)}</span>'
    f'<span class="papel">{escape(papel)}</span></li>'
    for n, papel in d["cinco"]
)

# Dados estruturados: ajuda o Google a entender que é uma lista de recomendações.
schema = json.dumps({
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "Qual IA abrir pra cada tarefa",
    "description": f"{total} tarefas do dia a dia e a ferramenta de IA certa para cada uma.",
    "numberOfItems": total,
    "itemListElement": [
        {"@type": "ListItem", "position": i, "name": f"{tarefa}: {ferr}",
         "url": F[ferr]["url"]}
        for i, (tarefa, ferr, *_) in enumerate(
            (l for _, linhas in d["grupos"] for l in linhas), start=1)
    ],
}, ensure_ascii=False, separators=(",", ":"))

JS = """
  const el = id => document.getElementById(id);
  const listaEl = el("lista"), chipsEl = el("chips"), countEl = el("count"), qEl = el("q");
  const itens = [...document.querySelectorAll(".linha")]
    .map(n => ({ el: n, busca: n.dataset.busca, ferr: n.dataset.ferr }));
  const total = itens.length;
  const norm = s => s.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase();
  let ativo = null;

  function aplicar() {
    const termo = norm(qEl.value.trim());
    let vis = 0;

    for (const it of itens) {
      const ok = (!termo || it.busca.includes(termo)) &&
                 (!ativo || it.ferr === ativo || (ativo === "Claude" && it.ferr === "Claude Code"));
      it.el.hidden = !ok;
      if (ok) vis++;
    }

    for (const sec of listaEl.children)
      sec.hidden = ![...sec.querySelectorAll(".linha")].some(l => !l.hidden);

    const filtrando = !!termo || !!ativo;
    document.body.classList.toggle("filtering", filtrando);
    document.body.classList.toggle("vazio-on", vis === 0);
    countEl.textContent = filtrando
      ? `${vis} ${vis === 1 ? "tarefa encontrada" : "tarefas encontradas"}`
      : `${total} tarefas mapeadas`;
  }

  qEl.addEventListener("input", aplicar);

  for (const b of chipsEl.children) {
    b.addEventListener("click", () => {
      ativo = ativo === b.dataset.ferr ? null : b.dataset.ferr;
      for (const c of chipsEl.children)
        c.setAttribute("aria-pressed", String(c.dataset.ferr === ativo));
      aplicar();
    });
  }

  el("clear").addEventListener("click", () => {
    qEl.value = "";
    ativo = null;
    for (const c of chipsEl.children) c.setAttribute("aria-pressed", "false");
    aplicar();
    qEl.focus();
  });

  const consoleEl = el("console");
  const sentinela = document.createElement("div");
  sentinela.style.height = "1px";
  consoleEl.parentNode.insertBefore(sentinela, consoleEl);
  new IntersectionObserver(([e]) => consoleEl.classList.toggle("stuck", !e.isIntersecting))
    .observe(sentinela);
"""

DESC = (f"{total} tarefas do dia a dia e a ferramenta de IA certa para cada uma, "
        "com o porquê da escolha e o link de cada ferramenta.")

html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Qual IA abrir pra cada tarefa</title>
<meta name="description" content="{escape(DESC, quote=True)}">
<meta name="author" content="Alison Araújo">
<link rel="canonical" href="{SITE}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="@aalisonaraujo">
<meta property="og:locale" content="pt_BR">
<meta property="og:url" content="{SITE}/">
<meta property="og:title" content="Qual IA abrir pra cada tarefa">
<meta property="og:description" content="{total} tarefas, a ferramenta certa pra cada uma e o porquê. Com o link de todas.">
<meta property="og:image" content="{SITE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Qual IA abrir pra cada tarefa">
<meta name="twitter:description" content="{total} tarefas, a ferramenta certa pra cada uma e o porquê. Com o link de todas.">
<meta name="twitter:image" content="{SITE}/og.png">
<meta name="theme-color" content="#131417" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#F1F2F5" media="(prefers-color-scheme: light)">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<script type="application/ld+json">{schema}</script>
<style>
{CSS}
</style>
</head>
<body>

<div class="wrap">

  <header class="top">
    <div class="fileira" aria-hidden="true">{fileira}</div>
    <div class="eyebrow">A lista completa · <b>@aalisonaraujo</b></div>
    <h1>Qual IA abrir</h1>
    <p class="tese">
      Não existe a melhor IA. <mark>Existe a certa pra tarefa.</mark>
      Ter todas instaladas não muda nada se você abre sempre a mesma.
    </p>
  </header>

  <div class="console" id="console">
    <div class="field">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.6"/>
        <path d="M11 11l3.5 3.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
      </svg>
      <input id="q" type="search" autocomplete="off" spellcheck="false"
             placeholder="o que você precisa fazer?" aria-label="Buscar uma tarefa">
      <button id="clear" type="button" aria-label="Limpar busca">×</button>
    </div>
    <div class="chips" id="chips" role="group" aria-label="Filtrar por ferramenta">{chips}</div>
  </div>

  <p class="count" id="count">{total} tarefas mapeadas</p>

  <main id="lista">{"".join(grupos_html)}</main>

  <div id="vazio">
    <p>Essa eu não mapeei ainda.</p>
    <span>Me manda no direct qual é a tarefa. Eu respondo e ela entra na próxima versão desta lista.</span>
  </div>

  <section class="bloco">
    <h2>Onde a resposta muda</h2>
    <p class="sub">
      Três casos em que eu troco de ferramenta no meio do caminho. É aqui que a maioria erra,
      e é o que separa quem tem as ferramentas de quem sabe usar.
    </p>
    <div class="desempates">{desempates}</div>
  </section>

  <section class="bloco">
    <h2>As nove ferramentas</h2>
    <p class="sub">Toca em qualquer uma pra abrir. Essas são as que eu tenho aberto num dia normal de trabalho.</p>
    <div class="cards">{cards}</div>
  </section>

  <section class="bloco">
    <h2>Se você só lembrar de cinco</h2>
    <p class="sub">Fecha esta página sabendo isto e você já está à frente de quase todo mundo.</p>
    <ul class="cinco">{cinco}</ul>
  </section>

  <section class="fecho">
    <h2>O que fazer com isso hoje</h2>
    <p>
      Escolhe <strong>uma tarefa que você faz toda semana</strong> e que está aqui com uma
      ferramenta que você nunca abriu. Faz essa uma vez pelo caminho novo. É assim que entra no
      automático, não lendo a lista inteira.
    </p>
    <p>
      Esta é a lista que eu uso de verdade, não um ranking das 50 melhores que ninguém abre.
      Ferramenta de IA muda rápido: quando eu trocar alguma, esta página troca junto.
    </p>
    <div class="assina">
      <span>Alison Araújo · <a href="https://instagram.com/aalisonaraujo" target="_blank" rel="noopener">@aalisonaraujo</a></span>
      <span>{total} tarefas · 9 ferramentas</span>
    </div>
  </section>

</div>

<script>{JS}</script>
<!-- Medição: ative "Web Analytics" no painel da Vercel e descomente a linha abaixo.
     Sem o toggle o script responde 404 e suja o console. -->
<!-- <script defer src="/_vercel/insights/script.js"></script> -->
</body>
</html>
"""

SAIDA.write_text(html, encoding="utf-8")
print(f"gerado: {SAIDA.relative_to(RAIZ)}  ({len(html):,} bytes)")
print(f"  {total} tarefas em {len(d['grupos'])} grupos, {len(F)} ferramentas")
print(f"  conteúdo no HTML, sem depender de JavaScript")
