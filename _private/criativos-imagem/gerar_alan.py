#!/usr/bin/env python3
"""
Modelagem dos anúncios do Alan Nicolas / Academia Lendária.

Diferença para o gerar_modelo.py (que modela o Bravy School): aquelas peças
VESTEM A MARCA, estas IMITAM CONTEÚDO. É a linha 236 do playbook ("formato
orgânico ganha sempre") somada à 276 ("layout que imita o tipo de conteúdo que o
público consome converte mais, fizeram página parecida com portal de notícias").

**Por isso estas peças NÃO usam a paleta da LP.** Um print de tweet roxo não
parece um tweet, parece banner, e aí o formato perde a única coisa que ele tem.
A continuidade com a LP aqui é feita pelo rosto e pelo nome, não pela cor.
Ver MODELAGEM-ALAN.md.

Régua do A1 herdada do ADR-0002 do carousel-generator (o formato tweet da casa):
fundo branco puro, conteúdo ancorado no topo, imagem ancorada na base sangrando
a borda inferior, nenhuma moldura.

Uso:  python3 gerar_alan.py A1 A2 A3 A4
"""
import base64, pathlib, sys
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).parent
FONTES = pathlib.Path.home() / "Projetos/carousel-generator/fonts"
FOTO = pathlib.Path.home() / "Projetos/carousel-generator/fotos/headshot-alison.jpg"
# a de palco tem plateia e tela ao fundo: é contexto, não retrato, e é o que o
# formato de portal pede. Se ainda não foi copiada para cá, cai na headshot.
PALCO = AQUI / "palco-alison-crop.jpg"      # A2: slot 992x470
PALCO_MED = AQUI / "palco-alison-med.jpg"   # A4: slot 992x520
FOTO_A2 = PALCO if PALCO.exists() else FOTO
FOTO_A4 = PALCO_MED if PALCO_MED.exists() else FOTO_A2

NOME = "Alison Araújo"
ARROBA = "@aalisonaraujo"  # dois "a": conferido no perfil real em 25/08/2026.
                          # Estava com um "a" só, e a peça imita print de post:
                          # o anúncio saía por um perfil e o print mostrava outro.


def b64(caminho):
    return base64.b64encode(pathlib.Path(caminho).read_bytes()).decode()


BASE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family:Archivo; src:url(data:font/ttf;base64,@@ARCHIVO@@); font-weight:100 900; }
@font-face { font-family:Anton; src:url(data:font/ttf;base64,@@ANTON@@); }
* { margin:0; padding:0; box-sizing:border-box; }
body { width:1080px; height:1350px; font-family:Archivo; background:#fff; color:#0f1419;
       overflow:hidden; display:flex; flex-direction:column; }
@@CSS@@
</style></head><body>@@CORPO@@</body></html>"""


# ── A1: print de post. Modela o tweet dele com o "Segundo Cérebro" ───────────
# A ordem dele: identidade → pergunta hipotética que descreve o mecanismo →
# parágrafo que NOMEIA o mecanismo e diz o que ele destrava → foto ancorada.
A1_CSS = """
.topo { padding:52px 52px 0; display:flex; align-items:center; gap:20px; }
.av { width:86px; height:86px; border-radius:50%; object-fit:cover; flex:none; }
.quem b { display:block; font-size:36px; font-weight:700; letter-spacing:-.01em; }
.quem span { display:block; font-size:30px; color:#536471; margin-top:2px; }
.selo { width:30px; height:30px; margin-left:8px; vertical-align:-4px; }
.corpo { padding:34px 52px 0; font-size:41px; line-height:1.36; letter-spacing:-.01em; }
.corpo p + p { margin-top:30px; }
.corpo b { font-weight:700; }
.cartao { margin-top:auto; height:640px; background:#0c0a10; color:#fff;
          padding:40px 44px 44px; display:flex; flex-direction:column; }
.cartao .tit { font-size:35px; font-weight:800; letter-spacing:-.01em; }
.cartao .tit i { font-style:normal; background:linear-gradient(96deg,#c183fb,#e27bb7);
                 -webkit-background-clip:text; background-clip:text; color:transparent; }
.linhas { margin-top:24px; flex:1; display:flex; flex-direction:column; gap:12px; }
.par { background:#191622; border-radius:14px; padding:0 20px; flex:1; display:flex;
       align-items:center; gap:18px; }
.par .tarefa { flex:1; font-size:27px; letter-spacing:-.01em; }
.par .seta { color:#5b5470; font-size:26px; }
.marca { width:56px; height:56px; border-radius:14px; background:#fff; flex:none;
         display:flex; align-items:center; justify-content:center; }
.marca img { width:34px; height:34px; }
.oculto { width:56px; height:56px; border-radius:14px; background:#241f30; flex:none;
          display:flex; align-items:center; justify-content:center; }
.oculto svg { width:26px; height:26px; fill:#6b6382; }

.pes { margin-top:22px; font-size:24px; color:#9ca3af; text-align:center; }
.pes b { color:#fff; font-weight:800; }
"""

SELO = ("<svg class='selo' viewBox='0 0 24 24' fill='#1d9bf0'><path d='M22.5 12.5c0-1.58-.875-2.95-2.148-3.6."
        "148-.435.238-.9.238-1.4 0-2.21-1.71-3.998-3.818-3.998-.47 0-.92.084-1.336.25C14.818 2.415 13.51 1.5 12 "
        "1.5s-2.816.917-3.437 2.25c-.415-.165-.866-.25-1.336-.25-2.11 0-3.818 1.79-3.818 4 0 .5.09.965.24 1.4C2.375 "
        "9.55 1.5 10.92 1.5 12.5c0 1.58.875 2.95 2.148 3.6-.148.435-.238.9-.238 1.4 0 2.21 1.708 4 3.818 4 .47 0 "
        ".92-.086 1.336-.25.62 1.334 1.926 2.25 3.436 2.25s2.816-.916 3.437-2.25c.415.163.865.248 1.336.248 2.11 0 "
        "3.818-1.79 3.818-4 0-.5-.09-.964-.238-1.4 1.273-.65 2.147-2.018 2.147-3.598zm-11.4 4.6L6.4 12.4l1.4-1.4 "
        "3.3 3.3 5.9-5.9 1.4 1.4-7.3 7.3z'/></svg>")

A1_CORPO = """
<div class="topo"><img class="av" src="data:image/jpeg;base64,@@FOTO@@">
  <div class="quem"><b>@@NOME@@@@SELO@@</b><span>@@ARROBA@@</span></div></div>
<div class="corpo">
  <p>Imagine listar as tarefas que comem a sua semana e receber, para cada uma,
     a IA certa de usar e o prompt pronto para colar nela.</p>
  <p>O problema quase nunca é a IA. É <b>usar a errada para aquela tarefa</b>,
     e concluir que a ferramenta é fraca quando o pedido é que estava vago.</p>
  <p>Não é "usa ChatGPT". É qual usar em cada momento do seu dia.</p>
</div>
@@CARTAO@@
"""


# ── A2: portal. Modela o "#ATENÇÃO / BREAKING NEWS" dele ─────────────────────
# Mantive a forma (barra de topo, kicker grande, foto, manchete, linha fina,
# linha do produto em bold) e tirei o "BREAKING NEWS": simular jornalismo para
# vender é o que separa modelar formato de forjar notícia.
A2_CSS = """
body { background:#fff; }
.barra { background:#d5252b; color:#fff; height:126px; display:flex; align-items:center;
         justify-content:space-between; padding:0 44px; }
.barra .t { font-size:44px; font-weight:800; letter-spacing:.02em; }
.barra .i { width:44px; height:34px; display:flex; flex-direction:column;
            justify-content:space-between; }
.barra .i i { display:block; height:5px; background:#fff; border-radius:3px; }
.lupa { width:44px; height:44px; border:5px solid #fff; border-radius:50%; position:relative; }
.lupa::after { content:''; position:absolute; right:-12px; bottom:-8px; width:20px; height:5px;
               background:#fff; transform:rotate(45deg); border-radius:3px; }
.kicker { font-family:Anton; font-size:88px; line-height:1.18; letter-spacing:-.015em;
          padding:44px 44px 0; }
.foto { width:calc(100% - 88px); height:470px; object-fit:cover; object-position:center center;
        margin:30px 44px 0; }
.manchete { padding:34px 44px 0; font-size:44px; font-weight:800; line-height:1.28;
            letter-spacing:-.01em; }
.linha { padding:22px 44px 0; font-size:36px; line-height:1.38; color:#3d444b; }
.evento { margin-top:auto; padding:0 44px 52px; font-size:36px; font-weight:800; }
.evento span { color:#d5252b; }
"""

A2_CORPO = """
<div class="barra"><div class="i"><i></i><i></i><i></i></div>
  <div class="t">PARA QUEM USA IA</div>
  <div class="lupa"></div></div>
<div class="kicker">TER VÁRIAS IAs<br>NÃO É SABER QUAL USAR.</div>
<img class="foto" src="data:image/jpeg;base64,@@FOTO@@">
<div class="manchete">O reflexo é usar sempre a mesma, inclusive para o que ela faz pior.</div>
<div class="linha">O diagnóstico mapeia as tarefas da sua semana e devolve, para cada uma,
  a ferramenta certa de usar e o prompt pronto para colar.</div>
<div class="evento">Qual IA Usar? · <span>diagnóstico de 2 minutos</span></div>"""


# ── A3: texto sobre branco com botão desenhado. Modela o "VOCÊ MELHOROU O PROMPT" ──
# A peça mais crua dele e a que mais se parece com post de grupo. O botão azul é
# desenhado dentro da imagem, inclinado, com setas apontando para o CTA real.
A3_CSS = """
body { justify-content:center; padding:0 76px; }
.h { font-size:76px; font-weight:800; line-height:1.16; letter-spacing:-.02em;
     text-align:center; color:#d5252b; }
.s { margin-top:38px; font-size:40px; font-weight:500; line-height:1.4;
     letter-spacing:-.01em; text-align:center; color:#15181b; }
.s b { font-weight:800; }
.e { margin-top:30px; font-size:35px; color:#4b5157; text-align:center; }
.btn { margin:58px auto 0; background:#1877f2; color:#fff; font-size:44px; font-weight:700;
       padding:22px 42px; border-radius:14px; transform:rotate(-4deg); width:fit-content;
       box-shadow:0 10px 28px rgba(24,119,242,.34); }
.setas { margin-top:26px; font-size:56px; text-align:center; letter-spacing:.06em; }
"""

A3_CORPO = """
<div class="h">PARE DE ASSINAR IA<br>QUE VOCÊ NÃO USA.</div>
<div class="s">Quase nunca é a IA que é fraca: é a tarefa na ferramenta errada, pedida
  do jeito errado. A <b>Regra das 3 IAs</b> resolve as duas.</div>

<div class="btn">Clique em Saiba Mais</div>
<div class="setas">👇👇👇</div>"""


LOGOS = pathlib.Path.home() / "Projetos/qual-ia-abrir/public/logos"
CAD = "<svg viewBox='0 0 24 24'><path d='M17 9V7a5 5 0 0 0-10 0v2H5v13h14V9h-2zm-8-2a3 3 0 0 1 6 0v2H9V7z'/></svg>"

# tarefa → o que abre. As quatro nomeadas vêm do `oq` de cada uma no dados.json;
# as outras vêm de escopo.sem_nome, que é como a LP fala delas desde 19/08: pela
# tarefa que resolvem, sem nome e sem logo, porque elas são o que a pessoa compra.
PARES = [("Escrever sem estragar o seu texto", "claude.svg"),
         ("Ler o processo inteiro e responder sobre ele", None),
         ("Pesquisar com a fonte do lado", "perplexity.svg"),
         ("Montar a apresentação pronta pra mostrar", None),
         ("Narrar com a sua voz", None)]


def cartao_html():
    linhas = []
    for tarefa, svg in PARES:
        marca = (f"<div class='marca'><img src='data:image/svg+xml;base64,{b64(LOGOS / svg)}'></div>"
                 if svg else f"<div class='oculto'>{CAD}</div>")
        linhas.append(f"<div class='par'><div class='tarefa'>{tarefa}</div>"
                      f"<div class='seta'>&rarr;</div>{marca}</div>")
    return ("<div class='cartao'><div class='tit'>Cada tarefa tem uma "
            "<i>IA certa</i> de usar.</div>"
            f"<div class='linhas'>{''.join(linhas)}</div>"
            "<div class='pes'>São 12 no mapa. As suas saem do que você responde, "
            "não de uma lista pronta.</div></div>")


# ── A4: matéria de portal. A outra peça de portal dele, a do "Especialista revela" ──
# Diferença para o A2: lá o kicker é uma tese em caixa alta gigante; aqui a peça
# imita o corpo de uma matéria (tag de editoria, manchete média, lead, foto,
# chamada para o botão). É a variante que mais parece notícia das duas, e por isso
# é também a que mais pesa na revisão da Meta. A barra de topo é a mesma do A2,
# de propósito: as duas são a mesma família.
A4_CSS = """
body { background:#fff; }
.barra { background:#d5252b; color:#fff; height:126px; display:flex; align-items:center;
         justify-content:space-between; padding:0 44px; }
.barra .t { font-size:44px; font-weight:800; letter-spacing:.02em; }
.barra .i { width:44px; height:34px; display:flex; flex-direction:column;
            justify-content:space-between; }
.barra .i i { display:block; height:5px; background:#fff; border-radius:3px; }
.lupa { width:44px; height:44px; border:5px solid #fff; border-radius:50%; position:relative; }
.lupa::after { content:''; position:absolute; right:-12px; bottom:-8px; width:20px; height:5px;
               background:#fff; transform:rotate(45deg); border-radius:3px; }
.tag { display:inline-block; margin:44px 0 0 44px; background:#d5252b; color:#fff;
       font-size:28px; font-weight:700; letter-spacing:.14em; padding:10px 20px;
       font-family:ui-monospace,"SF Mono",Menlo,monospace; }
.manchete { padding:28px 44px 0; font-size:50px; font-weight:800; line-height:1.26;
            letter-spacing:-.015em; }
.lead { padding:26px 44px 0; font-size:37px; line-height:1.42; color:#2f3439; }
.foto { width:calc(100% - 88px); height:520px; object-fit:cover; object-position:center center;
        margin:32px 44px 0; }
.chamada { margin-top:auto; padding:30px 44px 52px; font-size:37px; color:#2f3439; }
.chamada b { color:#101114; font-weight:800; }
"""

A4_CORPO = """
<div class="barra"><div class="i"><i></i><i></i><i></i></div>
  <div class="t">PARA QUEM USA IA</div>
  <div class="lupa"></div></div>
<div class="tag">QUAL IA USAR?</div>
<div class="manchete">Especialista revela o diagnóstico que ele usa para saber
  qual IA usar em cada tarefa do dia.</div>
<div class="lead">O problema quase nunca é a IA: é a tarefa na ferramenta errada,
  pedida do jeito errado. Em 2 minutos, o mapa diz qual ferramenta resolve cada coisa
  da sua semana e como pedir cada uma.</div>
<img class="foto" src="data:image/jpeg;base64,@@FOTO@@">
<div class="chamada">&#11015;&#65039; <b>Toque no botão</b> para saber mais.</div>"""


PECAS = {"A1": (A1_CSS, A1_CORPO), "A2": (A2_CSS, A2_CORPO), "A3": (A3_CSS, A3_CORPO),
         "A4": (A4_CSS, A4_CORPO)}


def main():
    pecas = sys.argv[1:] or ["A1", "A2", "A3", "A4"]
    foto = b64(FOTO)
    foto_a2 = b64(FOTO_A2)
    foto_a4 = b64(FOTO_A4)
    with sync_playwright() as pw:
        pagina = pw.chromium.launch().new_page(viewport={"width": 1080, "height": 1350})
        for peca in pecas:
            css, corpo = PECAS[peca]
            html = AQUI / f"_a_{peca}.html"
            html.write_text(BASE.replace("@@ARCHIVO@@", b64(FONTES / "Archivo.ttf"))
                            .replace("@@ANTON@@", b64(FONTES / "Anton.ttf"))
                            .replace("@@CSS@@", css).replace("@@CORPO@@", corpo)
                            .replace("@@FOTO@@", foto_a4 if peca == "A4" else foto_a2 if peca == "A2" else foto)
                            .replace("@@CARTAO@@", cartao_html()).replace("@@NOME@@", NOME)
                            .replace("@@ARROBA@@", ARROBA)
                            .replace("@@SELO@@", SELO))
            pagina.goto(html.as_uri())
            pagina.screenshot(path=AQUI / f"{peca}.png")
            html.unlink()
            print("ok ->", f"{peca}.png")


main()
