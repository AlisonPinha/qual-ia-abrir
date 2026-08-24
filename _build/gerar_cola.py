#!/usr/bin/env python3
"""Gera a cola gratuita do Direct e a fonte visual do card a partir de dados.json."""

import json
import pathlib
import sys
from html import escape

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BUILD = RAIZ / "_build"
SAIDA = RAIZ / "public" / "cola" / "index.html"

sys.path.insert(0, str(BUILD))
from config import GA4_ID  # noqa: E402

d = json.loads((BUILD / "dados.json").read_text(encoding="utf-8"))
F = d["ferramentas"]

grupos = []
tarefas = []
for titulo, linhas in d["grupos"]:
    selecionadas = [linha for linha in linhas if linha[3] is True]
    if selecionadas:
        grupos.append((titulo, selecionadas))
        tarefas.extend(selecionadas)

if len(tarefas) != 11:
    raise SystemExit(f"a cola exige exatamente 11 tarefas no_reel; dados.json tem {len(tarefas)}")

ferramentas = list(dict.fromkeys(linha[1] for linha in tarefas))
cola_js = (BUILD / "cola.js").read_text(encoding="utf-8")


def logo(nome, lado=34):
    return (f'<img src="/logos/{escape(F[nome]["logo"], quote=True)}" alt="" '
            f'width="{lado}" height="{lado}" loading="lazy">')


numero = 0
secoes = []
for titulo, linhas in grupos:
    cards = []
    for tarefa, ferramenta, porque, _ in linhas:
        numero += 1
        cards.append(f"""
        <article class="tarefa" data-task="{numero}">
          <span class="numero">{numero:02d}</span>
          <div class="tarefa-corpo">
            <h3>{escape(tarefa)}</h3>
            <div class="ferramenta">{logo(ferramenta)}<strong>{escape(ferramenta)}</strong></div>
            <p>{escape(porque)}</p>
          </div>
        </article>""")
    secoes.append(f"""
    <section class="grupo" aria-labelledby="grupo-{len(secoes) + 1}">
      <div class="grupo-titulo">
        <span>{len(linhas)} {"tarefas" if len(linhas) != 1 else "tarefa"}</span>
        <h2 id="grupo-{len(secoes) + 1}">{escape(titulo)}</h2>
      </div>
      <div class="tarefas">{"".join(cards)}</div>
    </section>""")

logos_hero = "".join(logo(nome, 42) for nome in ferramentas)
ga4 = ""
if GA4_ID:
    ga4 = f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={escape(GA4_ID, quote=True)}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', {json.dumps(GA4_ID)});
  gtag('event', 'abriu_cola', {{quantidade_tarefas: 11}});
</script>"""

html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>Sua cola das 11 tarefas · Qual IA Usar?</title>
  <meta name="description" content="As 11 tarefas do Reel e a IA que Alison abriria primeiro em cada uma.">
  <meta property="og:title" content="Sua cola das 11 tarefas">
  <meta property="og:description" content="Qual IA abrir primeiro em cada situação.">
  <meta property="og:image" content="https://diagnostico.noahai.com.br/card-dm.png">
  <meta property="og:url" content="https://diagnostico.noahai.com.br/cola">
  <meta property="og:type" content="website">
  <meta name="theme-color" content="#0c0a10">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap">
  <style>
    :root {{ --roxo:#c183fb; --rosa:#e27bb7;
            --grad:linear-gradient(96deg,#c183fb 0%,#e27bb7 100%);
            --fundo:#0c0a10; --card:#14111c; --linha:rgba(255,255,255,.08);
            --texto:#fff; --muted:#b9b6c4; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; background:var(--fundo); color:var(--texto); font-family:"Poppins",-apple-system,
      BlinkMacSystemFont,"Segoe UI",sans-serif; line-height:1.5; -webkit-font-smoothing:antialiased; }}
    a {{ color:inherit; }}
    .env {{ width:min(760px,calc(100% - 32px)); margin:auto; }}
    header {{ padding:20px 0; border-bottom:1px solid var(--linha); }}
    .marca {{ display:flex; align-items:center; gap:9px; font-weight:750; letter-spacing:-.02em; }}
    .bolha {{ display:grid; place-items:center; width:27px; height:27px; border-radius:8px;
      color:#14111c; background:var(--grad); font-weight:900; }}
    .hero {{ padding:54px 0 46px; position:relative; overflow:hidden; }}
    .hero::before {{ content:""; position:absolute; width:800px; height:500px; top:-310px; left:50%;
      transform:translateX(-50%); pointer-events:none;
      background:radial-gradient(circle,rgba(193,131,251,.18),rgba(226,123,183,.07) 42%,transparent 68%); }}
    .hero .env {{ position:relative; }}
    .eyebrow {{ display:inline-flex; border:1px solid var(--linha); background:rgba(255,255,255,.04); color:#e8e6ef;
      border-radius:999px; padding:7px 12px; text-transform:uppercase; letter-spacing:.09em;
      font-size:12px; font-weight:800; }}
    h1,h2,h3,p {{ margin-top:0; }}
    h1 {{ max-width:680px; margin:20px 0 18px; font-size:clamp(44px,8vw,72px); font-weight:700;
      line-height:.98; letter-spacing:-.045em; }}
    h1 mark {{ padding:0; background:var(--grad); -webkit-background-clip:text; background-clip:text;
      color:transparent; }}
    .intro {{ max-width:610px; color:var(--muted); font-size:clamp(18px,4vw,22px); }}
    .intro strong {{ color:var(--texto); }}
    .hero-acao {{ width:min(520px,100%); margin-top:24px; }}
    .logos {{ display:flex; gap:10px; margin-top:28px; flex-wrap:wrap; }}
    .logos img {{ width:42px; height:42px; border-radius:12px; background:#fff; padding:3px; object-fit:contain; }}
    .nota {{ margin-top:24px; padding:16px 18px; border-left:3px solid var(--rosa); color:#d7d8dc;
      background:#14111c; border-radius:0 10px 10px 0; }}
    main {{ padding-bottom:30px; }}
    .grupo {{ margin:0 0 50px; }}
    .grupo-titulo {{ display:flex; justify-content:space-between; align-items:end; gap:20px;
      margin-bottom:15px; }}
    .grupo-titulo h2 {{ margin:0; font-size:clamp(26px,6vw,36px); letter-spacing:-.035em; }}
    .grupo-titulo span {{ order:2; color:var(--muted); font:12px ui-monospace,SFMono-Regular,Menlo,monospace;
      text-transform:uppercase; letter-spacing:.08em; white-space:nowrap; }}
    .tarefas {{ display:grid; gap:12px; }}
    .tarefa {{ display:grid; grid-template-columns:48px 1fr; gap:14px; padding:20px;
      background:var(--card); border:1px solid var(--linha); border-radius:16px; }}
    .numero {{ color:#737780; font:13px ui-monospace,SFMono-Regular,Menlo,monospace; padding-top:4px; }}
    .tarefa h3 {{ margin:0 0 12px; font-size:20px; line-height:1.2; letter-spacing:-.02em; }}
    .ferramenta {{ display:flex; align-items:center; gap:10px; margin-bottom:12px; color:var(--roxo); }}
    .ferramenta img {{ width:34px; height:34px; border-radius:9px; background:#fff; padding:2px; object-fit:contain; }}
    .tarefa p {{ margin:0; color:var(--muted); }}
    .ponte {{ margin:70px 0 40px; padding:clamp(28px,7vw,48px); border:1px solid rgba(193,131,251,.22);
      background:linear-gradient(145deg,rgba(193,131,251,.10),#14111c 65%); border-radius:24px; }}
    .ponte h2 {{ margin:14px 0 16px; font-size:clamp(34px,8vw,56px); line-height:1;
      letter-spacing:-.045em; }}
    .ponte p {{ color:var(--muted); font-size:18px; }}
    .ponte p strong {{ color:var(--texto); }}
    .btn {{ display:flex; justify-content:center; align-items:center; width:100%; min-height:58px;
      margin-top:26px; padding:15px 20px; border-radius:14px; background:var(--grad); color:#14111c;
      text-decoration:none; text-align:center; font-weight:850; letter-spacing:-.01em; }}
    .btn:hover {{ filter:brightness(.94); }}
    .micro {{ margin:11px 0 0!important; text-align:center; font-size:13px!important; color:#888c94!important; }}
    footer {{ padding:30px 0 42px; border-top:1px solid var(--linha); color:#83868e; font-size:13px; }}
    footer .env {{ display:flex; justify-content:space-between; gap:20px; flex-wrap:wrap; }}
    @media (max-width:520px) {{
      .hero {{ padding:30px 0 38px; }}
      h1 {{ margin:16px 0 14px; }}
      .intro {{ font-size:17px; }}
      .hero-acao {{ margin-top:18px; }}
      .hero-acao .btn {{ margin-top:0; }}
      .logos {{ margin-top:24px; }}
      .grupo-titulo {{ display:block; }}
      .grupo-titulo span {{ display:block; margin-bottom:7px; }}
      .tarefa {{ grid-template-columns:35px 1fr; padding:18px 15px; gap:7px; }}
    }}
  </style>
  {ga4}
</head>
<body>
  <header><div class="env"><div class="marca"><span class="bolha">?</span> qual ia usar</div></div></header>
  <section class="hero">
    <div class="env">
      <span class="eyebrow">Seu presente de boas-vindas</span>
      <h1>A cola das <mark>11 tarefas</mark></h1>
      <p class="intro">As mesmas tarefas do Reel que te trouxe até aqui, agora em formato de consulta:
        <strong>qual IA eu abriria primeiro e por quê.</strong></p>
      <div class="hero-acao">
        <a class="btn" data-diagnostico href="/">Receber meu diagnóstico personalizado</a>
        <p class="micro">Leva cerca de 2 minutos.</p>
      </div>
      <div class="logos" aria-label="As seis ferramentas desta cola">{logos_hero}</div>
      <p class="nota">Não é um ranking das melhores IAs. É um ponto de partida para você parar de
        escolher ferramenta no escuro.</p>
    </div>
  </section>
  <main class="env">
    {"".join(secoes)}
    <section class="ponte">
      <span class="eyebrow">A lista é geral. A sua rotina não.</span>
      <h2>Qual combinação faz sentido para você?</h2>
      <p>A cola responde qual IA abrir primeiro em tarefas comuns. O diagnóstico cruza
        <strong>o que você faz, sua experiência, orçamento e ferramentas atuais</strong> para mostrar
        como a sua stack deveria ser organizada.</p>
      <a class="btn" data-diagnostico href="/">Receber meu diagnóstico personalizado</a>
      <p class="micro">Leva cerca de 2 minutos.</p>
    </section>
  </main>
  <footer><div class="env"><span>© 2026 Alison Araújo · @aalisonaraujo</span>
    <a href="/privacidade">Privacidade e exclusão de dados</a></div></footer>
  <script>{cola_js}</script>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


def gerar_card_fonte():
    imagens = "".join(
        f'<img src="../public/logos/{escape(F[nome]["logo"], quote=True)}" alt="{escape(nome, quote=True)}">'
        for nome in ferramentas
    )
    card = f"""<!doctype html><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap">
<!-- Gerado por gerar_cola.py a partir das tarefas no_reel de dados.json. -->
<style>
  * {{ box-sizing:border-box; margin:0; }}
  body {{ width:1080px; height:1080px; background:#0c0a10; color:#fff;
    font-family:"Poppins",-apple-system,BlinkMacSystemFont,sans-serif; padding:88px 84px;
    display:flex; flex-direction:column; justify-content:space-between; position:relative; overflow:hidden; }}
  body::after {{ content:""; position:absolute; right:-220px; top:-220px; width:640px; height:640px;
    background:radial-gradient(circle,rgba(193,131,251,.20),rgba(226,123,183,.08) 44%,transparent 68%); }}
  .logos {{ display:flex; gap:24px; position:relative; z-index:1; }}
  .logos img {{ width:126px; height:126px; border-radius:25%; object-fit:contain; background:#fff; padding:5px; }}
  .tag {{ display:inline-block; color:#e8e6ef; text-transform:uppercase; font-weight:800;
    letter-spacing:.12em; font-size:25px; margin-bottom:28px; }}
  h1 {{ font-size:118px; line-height:.94; letter-spacing:-.045em; font-weight:700; max-width:900px; }}
  h1 mark {{ padding:0; background:linear-gradient(96deg,#c183fb,#e27bb7);
    -webkit-background-clip:text; background-clip:text; color:transparent; }}
  .sub {{ font-size:38px; color:#a4a7af; margin-top:30px; line-height:1.35; max-width:820px; }}
  .rodape {{ display:flex; justify-content:space-between; align-items:flex-end;
    font:27px ui-monospace,Menlo,monospace; color:#777b84; }}
  .rodape b {{ color:#ecedf1; font-weight:500; }}
  .pill {{ background:#14111c; border:1px solid rgba(193,131,251,.30); border-radius:999px;
    padding:13px 25px; color:#c183fb; font-size:24px; white-space:nowrap; }}
</style>
<div class="logos">{imagens}</div>
<div>
  <span class="tag">Seu presente de boas-vindas</span>
  <h1>A cola das <mark>{len(tarefas)} tarefas</mark></h1>
  <p class="sub">Qual IA abrir primeiro em cada situação.</p>
</div>
<div class="rodape"><span>Alison Araújo · <b>@aalisonaraujo</b></span>
  <span class="pill">6 IAs · consulta rápida</span></div>
"""
    (BUILD / "card-fonte.html").write_text(card, encoding="utf-8")


SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(html, encoding="utf-8")
gerar_card_fonte()
print(f"gerado: {SAIDA.relative_to(RAIZ)} ({len(tarefas)} tarefas, {len(ferramentas)} ferramentas)")
print("gerado: _build/card-fonte.html")
