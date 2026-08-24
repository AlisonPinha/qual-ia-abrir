#!/usr/bin/env python3
"""
Versão editorial das imagens de triagem, na direção do @jp.asv / @bravyschool.

O que veio da referência: fundo creme, tipografia pura sem foto, o termo do dia
em serifa itálica dentro da manchete, cor única de destaque, crop marks nos
cantos, kicker em caixa alta espaçada e contador em mono.

O que NÃO veio, e é de propósito: a paleta tijolo deles é identidade de marca de
outra operação. VARIANTE decide se o destaque é o tijolo (fiel à referência) ou
o verde-limão da casa. A tipografia é a da casa (Archivo), não a deles.

O que a referência não tem e um anúncio precisa: CTA. No carrossel deles o
rodapé diz "ARRASTA"; aqui a metade de baixo, que neles fica vazia, carrega o
botão.
"""
import base64, pathlib, sys
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).parent
FONTES = pathlib.Path.home() / "Projetos/carousel-generator/fonts"

PALETAS = {
    "creme":  dict(fundo="#F2ECE0", tinta="#1A1915", destaque="#BB6450", suave="#DDD3C2"),
    "casa":   dict(fundo="#F2ECE0", tinta="#1A1915", destaque="#7A8C0A", suave="#DDD3C2"),
}

# (código, kicker, manchete com <i> no termo, selo do rodapé)
PECAS = [
    ("I1", "DIAGNÓSTICO / CUSTO",
     'R$ 1.244 por ano numa <i>IA</i> que você abre uma vez por mês.',
     "12 FERRAMENTAS · 23 TAREFAS · 2 MINUTOS"),
    ("I2", "DIAGNÓSTICO / PROVA",
     'Respondi meu próprio <i>diagnóstico</i> e ele mandou cortar uma que eu pago.',
     "12 FERRAMENTAS · 23 TAREFAS · 2 MINUTOS"),
    ("I3", "DIAGNÓSTICO / COMPARAÇÃO",
     'Mesmo pedido, quatro <i>IAs</i>. Três você não manda pra ninguém.',
     "12 FERRAMENTAS · 23 TAREFAS · 2 MINUTOS"),
    ("I4", "DIAGNÓSTICO / TAREFAS",
     '11 <i>tarefas</i>, a IA certa pra cada uma.',
     "12 FERRAMENTAS · 23 TAREFAS · 2 MINUTOS"),
    ("I6", "DIAGNÓSTICO / MÉTODO",
     'Dominar o <i>ChatGPT</i> é o conselho mais caro que te deram esse ano.',
     "12 FERRAMENTAS · 23 TAREFAS · 2 MINUTOS"),
]

def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family:Archivo; src:url(data:font/ttf;base64,{archivo}); font-weight:100 900; }}
@font-face {{ font-family:Garamond; src:url(data:font/ttf;base64,{garamond}); font-style:italic; }}
@font-face {{ font-family:Mono; src:url(data:font/ttf;base64,{mono}); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1080px; height:1350px; background:{fundo}; color:{tinta};
       font-family:Archivo; position:relative; overflow:hidden; }}
/* crop marks: é o detalhe que dá o ar de prova de impressão na referência */
.marca {{ position:absolute; width:34px; height:34px; border:2px solid {tinta}; opacity:.55; }}
.tl {{ top:44px; left:44px; border-right:0; border-bottom:0; }}
.tr {{ top:44px; right:44px; border-left:0; border-bottom:0; }}
.bl {{ bottom:44px; left:44px; border-right:0; border-top:0; }}
.br {{ bottom:44px; right:44px; border-left:0; border-top:0; }}
.quadro {{ position:absolute; inset:96px 96px 104px; display:flex; flex-direction:column; }}
.topo {{ display:flex; justify-content:space-between; align-items:baseline; }}
.kicker {{ color:{destaque}; font-size:23px; font-weight:600; letter-spacing:.19em; }}
.contador {{ font-family:Mono; font-size:23px; letter-spacing:.12em; }}
.asterisco {{ color:{destaque}; font-size:76px; line-height:1; margin:44px 0 30px; }}
h1 {{ font-size:{tamanho}px; font-weight:700; line-height:1.1; letter-spacing:-.022em; }}
h1 i {{ font-family:Garamond; font-style:italic; color:{destaque}; font-weight:400;
       letter-spacing:0; padding-right:.04em; }}
.risco {{ width:96px; height:5px; background:{destaque}; margin-top:38px; }}
.meio {{ flex:1; }}
.cta {{ display:inline-flex; align-items:center; gap:20px; align-self:flex-start;
       background:{tinta}; color:{fundo}; padding:26px 40px; border-radius:6px;
       font-size:33px; font-weight:600; letter-spacing:-.01em; }}
.cta span {{ color:{destaque}; }}
.selo {{ color:{destaque}; font-size:21px; font-weight:600; letter-spacing:.17em; margin-bottom:26px; }}
.rodape {{ border-top:1px solid {suave}; padding-top:24px; margin-top:34px;
          display:flex; justify-content:space-between; font-family:Mono; font-size:21px;
          letter-spacing:.1em; opacity:.62; }}
</style></head><body>
<div class="marca tl"></div><div class="marca tr"></div>
<div class="marca bl"></div><div class="marca br"></div>
<div class="quadro">
  <div class="topo"><div class="kicker">{kicker}</div><div class="contador">{codigo}</div></div>
  <div class="asterisco">&#10057;</div>
  <h1>{manchete}</h1>
  <div class="risco"></div>
  <div class="meio"></div>
  <div class="selo">{selo}</div>
  <div class="cta">descobrir a minha stack <span>&rarr;</span></div>
  <div class="rodape"><div>DIAGNOSTICO.NOAHAI.COM.BR</div><div>R$ 67 &middot; 2 MIN</div></div>
</div></body></html>"""

def main():
    variante = sys.argv[1] if len(sys.argv) > 1 else "creme"
    cores = PALETAS[variante]
    fontes = dict(archivo=b64(FONTES/"Archivo.ttf"), garamond=b64(AQUI/"EBGaramond-Italic.ttf"),
                  mono=b64(FONTES/"IBMPlexMono-Regular.ttf"))
    with sync_playwright() as pw:
        pagina = pw.chromium.launch().new_page(viewport={"width":1080,"height":1350})
        for codigo, kicker, manchete, selo in PECAS:
            # a referência quebra em 4 a 6 linhas; manchete curta pede corpo maior
            n = len(manchete.replace('<i>','').replace('</i>',''))
            tamanho = 88 if n <= 45 else 78 if n <= 62 else 70
            html = AQUI/f"_v2_{codigo}.html"
            html.write_text(HTML.format(**fontes, **cores, kicker=kicker, codigo=codigo,
                                        manchete=manchete, selo=selo, tamanho=tamanho))
            pagina.goto(html.as_uri())
            pagina.screenshot(path=AQUI/f"{codigo}-{variante}.png")
            html.unlink()
            print("ok ->", f"{codigo}-{variante}")

main()
