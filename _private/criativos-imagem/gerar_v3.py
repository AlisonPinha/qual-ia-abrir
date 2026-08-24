#!/usr/bin/env python3
"""
Execução do briefing "caos x ordem", com três correções obrigatórias.

O briefing pedia os três blocos como "escrever / pesquisar / automatizar". O
motor NÃO devolve papéis fixos: devolve três ferramentas em ORDEM DE ASSINAR, e
na tela do produto elas aparecem como Assina agora / Nos próximos 30 dias / Só
quando escalar (CRIATIVOS.md L258). Desenhar papel fixo é anunciar entrega que o
produto não faz, então os blocos usam o texto real.

O CTA do briefing era "QUERO MINHA STACK". O playbook exige que o CTA do criativo
case palavra por palavra com o botão da primeira tela, que é "descobrir a minha
stack". Trocado.

Nenhum logo é desenhado: as abas do caos são formas cegas. Logo de ferramenta no
anúncio fura o paywall das que a pessoa compra.
"""
import base64, pathlib, sys
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).parent
FONTES = pathlib.Path.home() / "Projetos/carousel-generator/fonts"
LIMAO, TINTA = "#CCF912", "#101114"

HEADLINES = {
    "briefing": "Qual IA você<br>usa hoje?",
    "I1": "R$ 1.244 por ano<br>na IA errada",
    "I6": "Dominar o ChatGPT<br>é o conselho mais caro",
}

def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

# abas cegas do lado do caos: largura e cor variadas, sem nome e sem logo
ABAS = "".join(
    f'<div class="aba" style="width:{w}px;opacity:{o}"></div>'
    for w, o in [(196,.92),(150,.72),(178,.85),(126,.6),(164,.78),(140,.66),(186,.88),(118,.55),
                 (172,.82),(134,.64),(190,.9),(146,.7),(160,.76),(122,.58),(182,.86),(138,.66),
                 (168,.8),(128,.6),(176,.84),(152,.72),(190,.88),(120,.56)]
)
POSTITS = "".join(
    f'<div class="postit" style="left:{x}px;top:{y}px;transform:rotate({r}deg)"></div>'
    for x, y, r in [(196,182,-7),(268,326,6),(214,470,-4),(276,604,8),(200,742,-6)]
)

HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family:Archivo; src:url(data:font/ttf;base64,{archivo}); font-weight:100 900; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1080px; height:1350px; font-family:Archivo; background:{tinta};
       color:#fff; overflow:hidden; display:flex; flex-direction:column; }}
h1 {{ font-size:76px; font-weight:800; line-height:1.04; letter-spacing:-.03em;
     text-align:center; padding:74px 60px 0; }}
h1 b {{ color:{limao}; }}
.selos {{ display:flex; gap:14px; justify-content:center; margin-top:26px; }}
.selo {{ border:2px solid #3a3d44; color:#c3c7cf; font-size:23px; font-weight:600;
        padding:10px 22px; border-radius:999px; letter-spacing:.02em; }}
.palco {{ flex:1; display:flex; margin:34px 56px 0; border-radius:20px; overflow:hidden; }}
/* esquerda: o caos. cinza e azul frio, denso, sem nada legível */
.caos {{ flex:1; background:linear-gradient(160deg,#1d2733,#141a22); padding:30px 26px;
        position:relative; }}
.rotulo {{ font-size:20px; font-weight:700; letter-spacing:.18em; margin-bottom:22px; }}
.caos .rotulo {{ color:#6f7c8d; }}
.aba {{ height:24px; background:#33404f; border-radius:6px; margin-bottom:10px; }}
.postit {{ position:absolute; width:112px; height:104px; background:#4a5568;
          border-radius:4px; box-shadow:0 8px 22px rgba(0,0,0,.42); }}
.sino {{ position:absolute; right:26px; top:150px; width:78px; height:78px;
        border-radius:50%; background:#2b3746; display:flex; align-items:center;
        justify-content:center; font-size:34px; }}
.contador {{ position:absolute; right:22px; top:144px; background:#d64545; color:#fff;
            font-size:21px; font-weight:700; border-radius:999px; padding:4px 11px; }}
/* direita: a ordem. clara, três blocos, nada além dos três */
.ordem {{ flex:1; background:#F6F7F4; padding:30px 26px; position:relative;
         display:flex; flex-direction:column; }}
.ordem .rotulo {{ color:#8b9199; }}
.bloco {{ background:#fff; border:2px solid #e4e7e2; border-left:9px solid {limao};
         border-radius:11px; padding:19px 20px; margin-bottom:15px;
         box-shadow:0 4px 14px rgba(16,17,20,.06); }}
.miolo {{ flex:1; display:flex; flex-direction:column; justify-content:center; }}
.quando {{ color:#101114; font-size:27px; font-weight:800; letter-spacing:-.01em; }}
.oquе {{ color:#7c828b; font-size:21px; margin-top:5px; }}
.barra {{ height:11px; background:#eef0ec; border-radius:999px; margin-top:11px; }}
.barra i {{ display:block; height:100%; background:{limao}; border-radius:999px; }}
/* elemento humano discreto, do briefing: só o cursor sobre o lado organizado */
.cursor {{ position:absolute; right:78px; top:352px; width:0; height:0;
          border-left:19px solid #101114; border-bottom:13px solid transparent;
          transform:rotate(-14deg); filter:drop-shadow(0 3px 5px rgba(0,0,0,.3)); }}
.pe {{ display:flex; align-items:center; justify-content:space-between;
      padding:30px 56px 40px; }}
.cta {{ background:{limao}; color:{tinta}; font-size:35px; font-weight:800;
       padding:24px 40px; border-radius:999px; letter-spacing:-.01em; }}
.marca {{ color:#767b85; font-size:24px; text-align:right; line-height:1.4; }}
</style></head><body>
<h1>{headline}</h1>
<div class="selos"><div class="selo">por profissão</div><div class="selo">2 minutos</div>
<div class="selo">R$ 67</div></div>
<div class="palco">
  <div class="caos"><div class="rotulo">HOJE</div>{abas}{postits}
    <div class="sino">&#128276;</div><div class="contador">12</div></div>
  <div class="ordem"><div class="rotulo">DEPOIS DO DIAGNÓSTICO</div>
    <div class="miolo">
    <div class="bloco"><div class="quando">Assina agora</div>
      <div class="oquе">a que resolve o que você mais faz</div><div class="barra"><i style="width:100%"></i></div></div>
    <div class="bloco"><div class="quando">Nos próximos 30 dias</div>
      <div class="oquе">a segunda, quando a primeira travar</div><div class="barra"><i style="width:62%"></i></div></div>
    <div class="bloco"><div class="quando">Só quando escalar</div>
      <div class="oquе">a terceira, e nem todo mundo chega nela</div><div class="barra"><i style="width:28%"></i></div></div>
    </div>
    <div class="cursor"></div>
  </div>
</div>
<div class="pe"><div class="cta">descobrir a minha stack</div>
  <div class="marca">diagnostico<br>.noahai.com.br</div></div>
</body></html>"""

def main():
    qual = sys.argv[1] if len(sys.argv) > 1 else "briefing"
    with sync_playwright() as pw:
        pagina = pw.chromium.launch().new_page(viewport={"width":1080,"height":1350})
        html = AQUI/f"_v3_{qual}.html"
        html.write_text(HTML.format(archivo=b64(FONTES/"Archivo.ttf"), tinta=TINTA, limao=LIMAO,
                                    headline=HEADLINES[qual], abas=ABAS, postits=POSTITS))
        pagina.goto(html.as_uri())
        pagina.screenshot(path=AQUI/f"v3-{qual}.png")
        html.unlink()
        print("ok ->", f"v3-{qual}.png")

main()
