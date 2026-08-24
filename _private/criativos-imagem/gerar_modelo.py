#!/usr/bin/env python3
"""
Modelagem dos anúncios do Bravy School / @jp.asv para o Qual IA Usar?

O playbook manda modelar a ORDEM dos elementos de uma peça validada, não as
palavras (seção "Do funil de VSL"). Cada modelo aqui é a estrutura invisível de
um anúncio dele, com o conteúdo do nosso produto no lugar.

PALETA: a da LP, lida de public/index.html, não a dos Reels.
  fundo #0c0a10 · card #14111c · destaque linear-gradient(96deg,#c183fb,#e27bb7)
  texto sobre o gradiente #14111c · apoio #9ca3af · claro #f5f0eb
O #CCF912 das constantes do CRIATIVOS.md é a régua do VÍDEO orgânico, medida nos
dois Reels campeões. Anúncio pago clica na LP, então ele veste a LP: quem chega
tem que reconhecer a página como a continuação do anúncio. Ver MODELAGEM-BRAVY.md.

O que NÃO vem dele, porque as constantes do CRIATIVOS.md vencem:
  - nenhuma promessa de substituir trabalho ("em 5 minutos, sem contratar")
  - nenhuma das 9 ferramentas escondidas aparece: elas são o que a pessoa compra
  - CTA "descobrir a minha stack", que casa palavra por palavra com o botão da LP

Todo número aqui saiu do _build/dados.json e está conferido.

Uso:  python3 gerar_modelo.py M1 | M2-conteudo | M2-negocio | M2-vendas | M3 | M4
"""
import base64, pathlib, sys
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).parent
FONTES = pathlib.Path.home() / "Projetos/carousel-generator/fonts"

def b64(caminho):
    return base64.b64encode(pathlib.Path(caminho).read_bytes()).decode()


BASE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family:Archivo; src:url(data:font/ttf;base64,@@ARCHIVO@@); font-weight:100 900; }
@font-face { font-family:Anton; src:url(data:font/ttf;base64,@@ANTON@@); }
:root { --dark:#0c0a10; --dark-2:#14111c; --claro:#f5f0eb; --cinza:#9ca3af;
        --cinza-min:#6b7280; --roxo:#c183fb;
        --grad:linear-gradient(96deg,#c183fb 0%,#e27bb7 100%);
        --linha:rgba(255,255,255,.08); }
* { margin:0; padding:0; box-sizing:border-box; }
body { width:1080px; height:1350px; font-family:Archivo; background:var(--dark);
       color:#fff; overflow:hidden; display:flex; flex-direction:column; }
/* texto pintado com o mesmo gradiente do .g da LP */
.g { background:var(--grad); -webkit-background-clip:text; background-clip:text;
     color:transparent; }
.eyebrow { font-size:22px; font-weight:700; letter-spacing:.2em; color:var(--cinza); }
.marca { font-size:22px; font-weight:800; letter-spacing:.22em; color:var(--cinza); }
.topo { display:flex; justify-content:space-between; align-items:center; padding:58px 62px 0; }
.pe { padding:34px 62px 52px; }
.linha { display:flex; align-items:center; justify-content:space-between; }
.cta { background:var(--grad); color:#14111c; font-size:34px; font-weight:800;
       padding:23px 38px; border-radius:999px; letter-spacing:-.01em; }
.dominio { color:var(--cinza-min); font-size:23px; text-align:right; line-height:1.4; }
@@CSS@@
</style></head><body>@@CORPO@@</body></html>"""


# ── M1: o número que ancora. Modela "R$ 67.926 por ano. Todo ano." ────────────
M1_CSS = """
.miolo { flex:1; display:flex; flex-direction:column; justify-content:center; padding:0 62px; }
.setup { font-size:38px; font-weight:600; color:var(--claro); letter-spacing:-.01em; }
.numero { font-family:Anton; font-size:210px; line-height:1.06; letter-spacing:-.02em;
          margin:6px 0 2px; }
.fecho { font-family:Anton; font-size:66px; line-height:1.12; letter-spacing:-.01em; }
/* a barra lateral é o gradiente pintado como fundo, para respeitar o raio */
.caixa { background:linear-gradient(180deg,#c183fb,#e27bb7) top left/9px 100% no-repeat,
         var(--dark-2); border-radius:0 14px 14px 0; padding:28px 32px 28px 41px;
         margin-top:38px; font-size:31px; line-height:1.42; color:var(--claro); }
.stats { display:flex; gap:20px; margin-top:38px; }
.stat { flex:1; background:var(--dark-2); border-radius:14px; padding:24px 22px; }
.stat b { display:block; font-family:Anton; font-size:52px; letter-spacing:-.01em; }
.stat span { display:block; font-size:21px; color:var(--cinza); line-height:1.35; margin-top:8px; }
"""

M1_CORPO = """
<div class="topo"><div class="eyebrow">O QUE VOCÊ JÁ PAGA HOJE</div><div class="marca">NOAHAI</div></div>
<div class="miolo">
  <div class="setup">Três IAs que você assinou só pra testar custam</div>
  <div class="numero g">R$ 3.600+</div>
  <div class="fecho">por ano. Todo ano.</div>
  <div class="caixa">E o problema nem é o quanto sai. É usar a mesma para tudo,
    inclusive para o que ela faz pior.</div>
  <div class="stats">
    <div class="stat"><b class="g">66</b><span>tarefas mapeadas, seis em cada uma das onze áreas</span></div>
    <div class="stat"><b class="g">12</b><span>ferramentas no mapa, e o diagnóstico diz qual em cada tarefa</span></div>
    <div class="stat"><b class="g">2 min</b><span>para saber qual usar em cada coisa que você faz</span></div>
  </div>
</div>
<div class="pe">
  <div class="linha"><div class="cta">descobrir a minha stack</div>
    <div class="dominio">diagnostico<br>.noahai.com.br</div></div>
</div>"""


# ── M2: o mapa da cobertura por área. Modela o organograma "EXCLUSIVO PARA" ───
M2_CSS = """
.faixa { background:var(--grad); color:#14111c; padding:52px 62px 44px; }
.faixa .k { font-family:Anton; font-size:38px; letter-spacing:.02em; }
.faixa .h { font-family:Anton; font-size:84px; line-height:1.18; letter-spacing:-.01em; }
.corpo { flex:1; padding:44px 62px 0; display:flex; flex-direction:column; }
.sub { font-size:32px; line-height:1.42; color:var(--claro); text-align:center;
       max-width:830px; margin:0 auto; }
.raiz { align-self:center; margin-top:34px; background:var(--grad); color:#14111c;
        font-family:Anton; font-size:46px; padding:18px 44px; border-radius:14px;
        letter-spacing:-.01em; }
.haste { align-self:center; width:3px; height:28px; background:#3a3348; }
.trilho { height:3px; background:#3a3348; margin:0 159px; }
.pernas { display:grid; grid-template-columns:repeat(3,1fr); }
.pernas i { display:block; width:3px; height:22px; background:#3a3348; margin:0 auto; }
.grade { display:grid; grid-template-columns:repeat(3,1fr); grid-auto-rows:1fr; gap:18px;
         margin-top:4px; flex:1; }
.bloco { background:linear-gradient(96deg,#c183fb,#e27bb7) top left/100% 5px no-repeat,
         var(--dark-2); border-radius:12px; padding:28px 24px; }
.bloco b { display:block; font-size:32px; font-weight:800; letter-spacing:-.01em; }
.bloco span { display:block; font-size:21px; color:var(--cinza); line-height:1.4; margin-top:10px; }
.nota { text-align:center; font-size:25px; color:var(--cinza); padding:28px 0 16px; }
.nota i { font-style:normal; font-weight:700; color:var(--roxo); }
"""

M2_CORPO = """
<div class="faixa"><div class="k">EXCLUSIVO PARA</div><div class="h">@@PUBLICO@@</div></div>
<div class="corpo">
  <div class="sub">@@SUB@@</div>
  <div class="raiz">Qual IA em cada uma?</div>
  <div class="haste"></div><div class="trilho"></div>
  <div class="pernas"><i></i><i></i><i></i></div>
  <div class="grade">@@BLOCOS@@</div>
  <div class="nota">O mapa diz <i>qual usar</i> em cada uma delas, e entrega o
    <i>prompt</i> escrito para a sua área.</div>
</div>
<div class="pe">
  <div class="linha"><div class="cta">descobrir a minha stack</div>
    <div class="dominio">diagnostico<br>.noahai.com.br</div></div>
</div>"""

# ── M4: quem começou agora. Modela "Não é um robô. É o escritório inteiro." ───
# A negação na primeira linha e a afirmação na segunda são a estrutura dele. O
# público é a opção "Comecei agora" da pergunta tempo_ia: quem nunca usou IA não
# tem o problema da conta (M1) nem as seis tarefas de profissão (M2), tem a
# paralisia de não saber por onde entrar. Os três passos são o que o produto
# entrega mesmo: dados.json → diagnostico.comeco traz o primeiro movimento e o
# primeiro prompt de cada ferramenta.
M4_CSS = """
.miolo { flex:1; display:flex; flex-direction:column; justify-content:center; padding:0 62px; }
.h1 { font-family:Anton; font-size:88px; line-height:1.16; letter-spacing:-.01em; }
.h2 { font-size:32px; line-height:1.42; color:var(--claro); margin-top:18px; max-width:900px; }
.passos { margin-top:48px; display:flex; flex-direction:column; gap:18px; }
.passo { background:var(--dark-2); border-radius:16px; padding:36px 30px; display:flex;
         align-items:center; gap:26px; }
.num { font-family:Anton; font-size:56px; line-height:1; width:56px; flex:none;
       text-align:center; }
.passo b { display:block; font-size:34px; font-weight:800; letter-spacing:-.01em; }
.passo span { display:block; font-size:23px; color:var(--cinza); margin-top:6px; }
.selos { display:flex; gap:14px; margin-top:38px; }
.selo { border:2px solid #2b2639; color:var(--cinza); font-size:23px; font-weight:600;
        padding:12px 24px; border-radius:999px; }
"""

M4_CORPO = """
<div class="topo"><div class="eyebrow">PRA QUEM COMEÇOU AGORA</div><div class="marca">NOAHAI</div></div>
<div class="miolo">
  <div class="h1">NÃO É APRENDER IA.<br><span class="g">É SABER QUAL USAR.</span></div>
  <div class="h2">São 12 no mapa. O diagnóstico diz qual usar em cada tarefa sua,
    com o prompt pronto para colar.</div>
  <div class="passos">
    <div class="passo"><div class="num g">1</div><div><b>Qual usar</b>
      <span>a certa para cada tarefa sua, não a que está na moda</span></div></div>
    <div class="passo"><div class="num g">2</div><div><b>Em que ordem</b>
      <span>a de hoje, a dos próximos 30 dias e a de quando escalar</span></div></div>
    <div class="passo"><div class="num g">3</div><div><b>O que digitar</b>
      <span>o primeiro movimento e o primeiro prompt de cada uma</span></div></div>
  </div>
  <div class="selos"><div class="selo">14 perguntas</div>
    <div class="selo">2 minutos</div></div>
</div>
<div class="pe">
  <div class="linha"><div class="cta">descobrir a minha stack</div>
    <div class="dominio">diagnostico<br>.noahai.com.br</div></div>
</div>"""


# as tarefas são as opções reais do quiz (dados.json → diagnostico.perguntas)
AREAS = {
    "conteudo": ("QUEM VIVE DE CONTEÚDO",
                 "O diagnóstico separa as seis tarefas que comem a sua semana e devolve, "
                 "para cada uma, a IA certa de usar.",
                 [("Roteiro", "escrever legenda e sair com a sua voz"),
                  ("Vídeo", "gravar, editar e narrar"),
                  ("Imagem", "capa, thumbnail e carrossel"),
                  ("Pauta", "achar a que ainda não saturou"),
                  ("Leitura", "por que um post foi e o outro não"),
                  ("Direct", "responder comentário sem sumir")]),
    "negocio": ("QUEM TOCA O PRÓPRIO NEGÓCIO",
                "O diagnóstico separa as seis tarefas que comem o seu dia e devolve, "
                "para cada uma, a IA certa de usar.",
                [("Proposta", "contrato, e-mail e orçamento"),
                 ("Número", "olhar a planilha pra decidir"),
                 ("Mercado", "preço, concorrente e pesquisa"),
                 ("Processo", "documentar e treinar equipe"),
                 ("Reunião", "apresentação e relatório"),
                 ("Incêndio", "o sistema que ninguém cuida")]),
    "vendas": ("QUEM VIVE DE VENDER",
               "O diagnóstico separa os seis pontos onde a sua venda trava e devolve, "
               "para cada um, a IA certa de usar.",
               [("Qualificar", "achar quem vale o seu tempo"),
                ("Abordagem", "a primeira mensagem sem cara de robô"),
                ("Objeção", "responder na hora, no WhatsApp"),
                ("Follow-up", "proposta e retomada"),
                ("Memória", "o que foi falado com cada um"),
                ("Sumiço", "entender por que o cliente parou")]),
}


# ── M3: a cobrança em formato de notificação. Modela "Enquanto você dormia" ───
M3_CSS = """
.miolo { flex:1; display:flex; flex-direction:column; justify-content:center; padding:0 62px; }
.h1 { font-family:Anton; font-size:96px; line-height:1.14; letter-spacing:-.01em; }
.h2 { font-size:34px; color:var(--claro); margin-top:12px; }
.cards { margin-top:40px; display:flex; flex-direction:column; gap:14px; }
.card { background:var(--dark-2); border-radius:16px; padding:24px 26px; display:flex;
        align-items:center; gap:20px; }
.ic { width:58px; height:58px; border-radius:14px; background:#fff; flex:none;
      display:flex; align-items:center; justify-content:center; }
.ic img { width:36px; height:36px; }
.txt { flex:1; }
.txt b { display:block; font-size:30px; font-weight:800; letter-spacing:-.01em; }
.txt span { display:block; font-size:22px; color:var(--cinza); margin-top:4px; }
.dia { font-size:22px; color:var(--cinza-min); width:110px; text-align:right; flex:none; }
.total { display:flex; justify-content:space-between; align-items:center; margin-top:22px;
         background:var(--grad); color:#14111c; border-radius:16px; padding:22px 26px; }
.total b { font-size:29px; font-weight:800; }
.virada { margin-top:26px; font-size:34px; font-weight:700; line-height:1.34;
          letter-spacing:-.01em; }
.total i { font-family:Anton; font-size:44px; font-style:normal; letter-spacing:-.01em; }
"""

M3_CORPO = """
<div class="topo"><div class="eyebrow">O SEU DIA · ONTEM</div><div class="marca">NOAHAI</div></div>
<div class="miolo">
  <div class="h1">QUATRO TAREFAS.<br>A MESMA ABA.</div>
  <div class="h2">e cada uma delas tinha uma IA melhor</div>
  <div class="cards">@@CARDS@@</div>
  <div class="total"><b>Não é a ferramenta que é fraca</b><i>é o reflexo</i></div>
  <div class="virada">O problema quase nunca é a IA.
    <span class="g">É a tarefa na ferramenta errada, pedida do jeito errado.</span></div>
</div>
<div class="pe">
  <div class="linha"><div class="cta">descobrir a minha stack</div>
    <div class="dominio">diagnostico<br>.noahai.com.br</div></div>
</div>"""

# só as quatro que a LP já cita pelo nome. As outras oito são o que a pessoa compra.
LOGOS = pathlib.Path.home() / "Projetos/qual-ia-abrir/public/logos"
# o mesmo logo nas quatro é o argumento, não descuido de arte
REFLEXO = [("Ler o PDF de 80 páginas", "colou aos pedaços e perdeu o meio", "09h12"),
           ("Escrever a proposta", "voltou genérica, você reescreveu inteira", "11h40"),
           ("Conferir um dado", "veio sem fonte, não deu para checar", "15h05"),
           ("Montar a apresentação", "virou lista de tópicos, não virou slide", "18h30")]


def montar(peca):
    if peca == "M1":
        return M1_CSS, M1_CORPO
    if peca == "M4":
        return M4_CSS, M4_CORPO
    if peca == "M3":
        icone = b64(LOGOS / "chatgpt.svg")
        cards = "".join(
            f"<div class='card'><div class='ic'><img src='data:image/svg+xml;base64,"
            f"{icone}'></div><div class='txt'><b>{tarefa}</b><span>{saida}</span></div>"
            f"<div class='dia'>{hora}</div></div>"
            for tarefa, saida, hora in REFLEXO)
        return M3_CSS, M3_CORPO.replace("@@CARDS@@", cards)
    if peca.startswith("M2-"):
        publico, sub, tarefas = AREAS[peca[3:]]
        blocos = "".join(f"<div class='bloco'><b>{t}</b><span>{d}</span></div>" for t, d in tarefas)
        return M2_CSS, (M2_CORPO.replace("@@PUBLICO@@", publico)
                        .replace("@@SUB@@", sub).replace("@@BLOCOS@@", blocos))
    raise SystemExit(f"peça desconhecida: {peca}")


def main():
    pecas = sys.argv[1:] or ["M1", "M2-conteudo", "M3", "M4"]
    with sync_playwright() as pw:
        pagina = pw.chromium.launch().new_page(viewport={"width": 1080, "height": 1350})
        for peca in pecas:
            css, corpo = montar(peca)
            html = AQUI / f"_m_{peca}.html"
            html.write_text(BASE.replace("@@ARCHIVO@@", b64(FONTES / "Archivo.ttf"))
                            .replace("@@ANTON@@", b64(FONTES / "Anton.ttf"))
                            .replace("@@CSS@@", css).replace("@@CORPO@@", corpo))
            pagina.goto(html.as_uri())
            pagina.screenshot(path=AQUI / f"{peca}.png")
            html.unlink()
            print("ok ->", f"{peca}.png")


main()
