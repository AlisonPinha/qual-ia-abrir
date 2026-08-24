#!/usr/bin/env python3
"""
Gera as imagens de triagem (I1 a I6) do teste de criativo.

Regra do playbook que manda aqui (linha 273): "isolar UMA variável, resto 100%
idêntico". Por isso existe um fundo só e um template só: entre as peças muda a
headline, e nada mais. Fundo diferente por peça invalidaria a leitura.

O texto NÃO é gerado por IA. O Higgsfield entrega a cena vazia e a headline
entra por cima em CSS, senão o acento sai quebrado (é o mesmo método do
carousel-generator, ver reference_imagem_gemini_capa).
"""
import base64, pathlib, sys
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).parent
FONTES = pathlib.Path.home() / "Projetos/carousel-generator/fonts"
LIMAO = "#CCF912"

# A headline de cada peça é o G1 do corpo, palavra por palavra (CRIATIVOS.md).
PECAS = [
    ("I1", "R$ 1.244 por ano<br>numa IA que você abre<br>uma vez por mês", "dor financeira"),
    ("I2", "Respondi meu próprio<br>diagnóstico e ele mandou<br>cortar uma que eu pago", "demonstração"),
    ("I3", "Mesmo pedido,<br>quatro IAs. Três você<br>não manda pra ninguém", "comparação"),
    ("I4", "11 tarefas,<br>a IA certa<br>pra cada uma", "o ângulo de 98 mil views"),
    ("I6", "Dominar o ChatGPT<br>é o conselho mais caro<br>que te deram esse ano", "contra o consenso"),
]

def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Anton; src: url(data:font/ttf;base64,{anton}); }}
@font-face {{ font-family: Archivo; src: url(data:font/ttf;base64,{archivo}); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1080px; height:1350px; background:#151515; font-family:Archivo;
       overflow:hidden; display:flex; flex-direction:column; }}
.foto {{ height:780px; width:100%; flex:none;
        background:url(data:image/png;base64,{foto}) center 62% / cover no-repeat; }}
/* A foto não encosta no texto: a fatia escura evita a linha dura que aparece
   quando a imagem clareia justo na borda. */
.fade {{ height:140px; margin-top:-140px; flex:none;
        background:linear-gradient(to bottom, rgba(21,21,21,0), #151515); }}
.texto {{ flex:1; padding:0 72px 40px; display:flex; flex-direction:column; justify-content:center; }}
h1 {{ font-family:Anton; font-size:{tamanho}px;
     /* 1.18, não 1.02: em Anton o circunflexo de VOCÊ e MÊS extrapola tanto o
        em-box que o piso da nota geral ainda clipa. Medido no render, não no CSS. */
     line-height:1.18; color:#fff; text-transform:uppercase; letter-spacing:-.01em; }}
.cta {{ display:flex; align-items:center; gap:18px; margin-top:44px; }}
.pilula {{ background:{limao}; color:#151515; font-weight:700; font-size:34px;
          padding:20px 34px; border-radius:999px; letter-spacing:-.01em; }}
.seta {{ color:{limao}; font-size:40px; }}
.rodape {{ flex:none; padding:0 72px 52px; color:#7a7a7a; font-size:26px; }}
</style></head><body>
<div class="foto"></div><div class="fade"></div>
<div class="texto"><h1>{headline}</h1>
<div class="cta"><div class="pilula">descobrir a minha stack</div><div class="seta">&rarr;</div></div></div>
<div class="rodape">diagnostico.noahai.com.br</div>
</body></html>"""

def main():
    anton, archivo, foto = b64(FONTES/"Anton.ttf"), b64(FONTES/"Archivo.ttf"), b64(AQUI/"fundo-A.png")
    with sync_playwright() as pw:
        pagina = pw.chromium.launch().new_page(viewport={"width":1080,"height":1350})
        for codigo, headline, _ in PECAS:
            # Headline curta pede corpo maior; a régua é caber em 3 linhas.
            # A régua é a linha mais longa caber nos 936px úteis, não o total
            # de caracteres: "R$ 1.244 POR ANO" ocupa mais que 16 letras normais.
            maior = len(max(headline.split("<br>"), key=len))
            tamanho = 88 if maior <= 18 else 76 if maior <= 24 else 66
            html = AQUI / f"_{codigo}.html"
            html.write_text(HTML.format(anton=anton, archivo=archivo, foto=foto,
                                        headline=headline, tamanho=tamanho, limao=LIMAO))
            pagina.goto(html.as_uri())
            pagina.screenshot(path=AQUI / f"{codigo}.png")
            html.unlink()
            print("ok ->", codigo)

main()
