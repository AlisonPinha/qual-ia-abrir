#!/usr/bin/env python3
"""
Gera public/index.html com todo o conteúdo já escrito no HTML.

O motivo de existir: antes a lista era montada por JavaScript no navegador, então
o robô do Google, o gerador de preview do WhatsApp e leitores de tela recebiam uma
página vazia. Agora o JS só liga a busca, o filtro e o envio do formulário sobre o
que já está no HTML.

Fonte dos dados: _build/dados.json
Estilo:          _build/estilo.css
Uso:             python3 _build/gerar.py && vercel deploy --prod --yes
"""

import json
import math
import pathlib
import sys
import unicodedata
from html import escape

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BUILD = RAIZ / "_build"
SAIDA = RAIZ / "public" / "index.html"
SITE = "https://diagnostico.noahai.com.br"
INSTA = "https://instagram.com/aalisonaraujo"

# As URLs e o preço vivem em _build/config.py, para não haver dois lugares
# onde a mesma constante precisa ser colada.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from config import (CAPTURA_URL, ANALITICO_URL, CHECKOUT_URL, PRECO,  # noqa: E402
                    PIXEL_META, GA4_ID)
from config import VARIANTES  # noqa: E402
import questionario  # noqa: E402

# Variante do teste seco de nome chiclete: "" é o controle, na raiz.
SLUG = sys.argv[1] if len(sys.argv) > 1 else ""
if SLUG not in VARIANTES:
    raise SystemExit(f"variante desconhecida: {SLUG!r}. Use uma de {list(VARIANTES)}")
V = VARIANTES[SLUG]
CHECKOUT_URL = V["checkout"] or CHECKOUT_URL
SAIDA = RAIZ / "public" / SLUG / "index.html" if SLUG else RAIZ / "public" / "index.html"
NOINDEX = '<meta name="robots" content="noindex,nofollow">' if SLUG else ""

d = json.loads((BUILD / "dados.json").read_text(encoding="utf-8"))
CSS = (BUILD / "estilo.css").read_text(encoding="utf-8")
MOTOR_JS = (BUILD / "motor.js").read_text(encoding="utf-8")
SESSAO_JS = (BUILD / "sessao.js").read_text(encoding="utf-8")
ESPELHO_JS = (BUILD / "espelho.js").read_text(encoding="utf-8")
CODIGO_JS = (BUILD / "codigo.js").read_text(encoding="utf-8")
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
        f'<section class="grupo"><h3>{escape(titulo)}</h3>'
        f'<ul class="linhas">{"".join(itens)}</ul></section>'
    )

# ---------- blocos da lista ----------

chips = "".join(
    f'<button type="button" class="chip" aria-pressed="false" data-ferr="{escape(n, quote=True)}">'
    f'<img src="/logos/{F[n]["logo"]}" alt="" width="18" height="18">{escape(n)}</button>'
    for n in F if n != "Claude Code"
)

# As 4 conhecidas saem com nome e logo: são prova emprestada e não revelam nada, porque
# quem chega aqui já ouviu falar das quatro. As outras 9 saem por categoria, sem nome e sem
# logo, senão a página entrega o catálogo e a pessoa vai atrás sozinha.
ESC = d["escopo"]
cards = "".join(
    f'<div class="f-card">'
    f'<img src="/logos/{F[n]["logo"]}" alt="" width="42" height="42" loading="lazy">'
    f'<span class="nome">{escape(n)}</span></div>'
    for n in ESC["conhecidas"]
)
ocultas = "".join(
    f'<li><span class="esc-off" aria-hidden="true"></span>{escape(x)}</li>'
    for x in ESC["sem_nome"]
)

# ---------- prova social ----------
# Só existe quando houver depoimento real, dito pela pessoa e com print guardado. Com a lista
# vazia a seção inteira some, e é assim que ela deve ficar até alguém falar de verdade:
# depoimento escrito por nós, ainda que "para trocar depois", é publicidade enganosa.
PROVA = d["prova"]
if PROVA["depoimentos"]:
    provas = "".join(
        f'<figure class="dep">'
        f'<blockquote>{escape(texto)}</blockquote>'
        f'<figcaption>{escape(quem)}</figcaption>'
        f'</figure>'
        for quem, texto in PROVA["depoimentos"]
    )
    prova_html = f"""
<section class="sec" id="depoimentos">
  <div class="env">
    <div class="cabeca">
      <span class="eyebrow">{escape(PROVA["eyebrow"])}</span>
      <h2>{escape(PROVA["titulo"])}</h2>
    </div>
    <div class="deps">{provas}</div>
  </div>
</section>"""
else:
    prova_html = ""

problemas = "".join(
    f'<article class="p-card"><span class="p-n">{i}</span>'
    f'<span class="nome">{escape(titulo)}</span>'
    f'<span class="txt">{escape(txt)}</span></article>'
    for i, (titulo, txt) in enumerate(d["problema"], start=1)
)

# ---------- órbita de categorias ----------

# ícone por categoria; se o título mudar no JSON, cai no genérico sem quebrar
ICONES = {
    "Escrever e comunicar":
        '<path d="M3 13.5L12.4 4.1a1.6 1.6 0 012.2 0l.3.3a1.6 1.6 0 010 2.2L5.5 16H3v-2.5z"/>',
    "Pensar e decidir":
        '<path d="M9.5 2a5.2 5.2 0 013 9.4V13h-6v-1.6A5.2 5.2 0 019.5 2z"/><rect x="7" y="14.4" width="5" height="1.7" rx=".85"/>',
    "Pesquisar e entender":
        '<circle cx="8.3" cy="8.3" r="5.1" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12.4 12.4l4 4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "Criar imagem e vídeo":
        '<rect x="2" y="3.5" width="15" height="12" rx="2.4" fill="none" stroke="currentColor" stroke-width="1.9"/><circle cx="6.6" cy="7.6" r="1.4"/><path d="M3.4 13.6l3.9-3.6 3 2.6 2.4-2 2.9 3z"/>',
    "Construir":
        '<path d="M11.6 2.2a4.4 4.4 0 00-4 5.9L2.8 12.9a1.5 1.5 0 002.1 2.1l4.8-4.8a4.4 4.4 0 005.6-5.5l-2.3 2.3-2.1-2.1 2.3-2.3a4.4 4.4 0 00-1.6-.4z"/>',
}
GENERICO = '<circle cx="9.5" cy="9.5" r="4.4" fill="none" stroke="currentColor" stroke-width="2"/>'

# posições radiais de verdade: pentágono a partir do topo, num campo elíptico
# (elipse porque as pílulas são largas e um círculo puro jogaria as laterais fora da tela)
VB_W, VB_H = 1000.0, 500.0
CX, CY, RX, RY = 500.0, 250.0, 358.0, 198.0

def ponto(i, n, escala=1.0):
    ang = math.radians(90 - i * (360.0 / n))
    return CX + RX * escala * math.cos(ang), CY - RY * escala * math.sin(ang)

cats = [(titulo, len(linhas)) for titulo, linhas in d["grupos"]]
n_cats = len(cats)

# teia de fundo: anéis concêntricos, raios até cada pílula e nós ao longo deles
linhas_svg, nos_svg = [], []
for i in range(n_cats):
    x, y = ponto(i, n_cats)
    linhas_svg.append(f'<line x1="{CX:.0f}" y1="{CY:.0f}" x2="{x:.0f}" y2="{y:.0f}"/>')
    for frac in (0.34, 0.58, 0.82):
        px, py = ponto(i, n_cats, frac)
        nos_svg.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="{4.2 - frac * 1.6:.1f}"/>')
    # nó no meio do arco entre esta pílula e a próxima, como na referência
    ang_meio = math.radians(90 - (i + 0.5) * (360.0 / n_cats))
    mx, my = CX + RX * 0.62 * math.cos(ang_meio), CY - RY * 0.62 * math.sin(ang_meio)
    nos_svg.append(f'<circle cx="{mx:.0f}" cy="{my:.0f}" r="2.6"/>')

teia = (
    f'<svg class="teia" viewBox="0 0 {VB_W:.0f} {VB_H:.0f}" preserveAspectRatio="none" aria-hidden="true">'
    f'<g class="t-linhas">{"".join(linhas_svg)}</g>'
    f'<g class="t-aneis">'
    f'<circle cx="{CX:.0f}" cy="{CY:.0f}" r="58"/>'
    f'<circle cx="{CX:.0f}" cy="{CY:.0f}" r="84"/>'
    f'<circle cx="{CX:.0f}" cy="{CY:.0f}" r="116"/>'
    f'<ellipse cx="{CX:.0f}" cy="{CY:.0f}" rx="{RX:.0f}" ry="{RY:.0f}" class="externo"/>'
    f'</g>'
    f'<g class="t-nos">{"".join(nos_svg)}</g>'
    f'</svg>'
)

orbes = []
for i, (titulo, n) in enumerate(cats):
    x, y = ponto(i, n_cats)
    ico_svg = ICONES.get(titulo, GENERICO)
    estilo = f'left:{x / VB_W * 100:.2f}%;top:{y / VB_H * 100:.2f}%'
    orbes.append(
        f'<li class="orbe" style="{estilo}">'
        f'<span class="orbe-ico"><svg width="19" height="19" viewBox="0 0 19 19" fill="currentColor">{ico_svg}</svg></span>'
        f'{escape(titulo)}<span class="n">{n}</span><span class="seta">›</span></li>'
    )

orbita_itens = "".join(orbes)

# ---------- diagnóstico ----------

DG = d["diagnostico"]
CL = d["captura_lead"]
DG["mecanismo"] = V["mecanismo"]
DG["crenca"] = V["crenca"]
d["oferta"]["nome"] = V["nome"]
# o break do One Belief carrega o nome do mecanismo
DG["perguntas"] = [
    [p[0], p[1].replace("A Regra das 3 IAs", V["mecanismo"]), *p[2:]] if p[0] == "break1" else p
    for p in DG["perguntas"]
]

# As perguntas vão escritas no HTML (existem sem JavaScript). O JS só soma os pesos.
# Passo com pid "break*" é uma tela de conteúdo, não pergunta: quebra o clique
# automático de quem só vai batendo em "próximo". O título traz manchete e corpo
# separados por " | ", e o botão único avança pelo mesmo caminho de uma opção.
passos_html, regras, n_perguntas = questionario.montar(DG["perguntas"], DG["aberta"])
perguntas_html = [passos_html]

n_passos = len(DG["perguntas"]) + 1
if CAPTURA_URL:
    perguntas_html.append(
        f'<fieldset class="passo passo-lead" data-passo="{n_passos}" data-q="lead">'
        f'<legend><span class="num">{n_perguntas + 1} de {n_perguntas + 1}</span>{escape(CL["titulo"])}</legend>'
        f'<p class="lead-sub">{escape(CL["sub"])}</p>'
        f'<label class="campo-lead">Seu nome'
        f'<input id="lead-nome" type="text" autocomplete="given-name" required'
        f' placeholder="Como posso te chamar?"></label>'
        f'<label class="campo-lead">WhatsApp'
        f'<input id="lead-zap" type="tel" inputmode="numeric" autocomplete="tel" required'
        f' placeholder="(11) 99999-0000" maxlength="16"></label>'
        f'<button type="button" class="btn-cta" id="lead-ok">{escape(CL["botao"])}</button>'
        f'<p class="form-aviso" id="lead-aviso">{escape(CL["aviso"])}</p>'
        f'</fieldset>'
    )

# Dado que o motor consome no navegador: pesos, custo e o primeiro passo de cada ferramenta.
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
    "mudaram": DG["mudaram"],
    "espelhoPronto": DG["espelhoPronto"],
    "cabem": DG["cabem"],
    "teto": DG["teto"],
    "foco": DG["foco"],
    "celular": DG["celular"],
    "semCelular": DG["semCelular"],
    "perfil": DG["perfil"],
    # o preço em número, para o JS decidir se pode dizer que cortar uma já paga o mapa
    "preco": int(d["oferta"]["preco"]),   # OF só é definido depois deste bloco
    "analitico": ANALITICO_URL,
    "origem": SLUG or "site",
    "pids": [p[0] for p in DG["perguntas"] if not p[0].startswith("break")],
    "ferramentas": {
        # só o que o teaser exibe. logo, url, descrição e custo completo são do produto.
        # "vitoria" é o que o card mostra no lugar do preço, e não nomeia nem descreve a
        # ferramenta: é o resultado que a pessoa leva. "mes" é o custo em real, usado só
        # na conta do que ela NÃO precisa assinar, que é onde o custo joga a favor.
        n: {"curto": DG["acesso"][n]["curto"], "faixa": DG["acesso"][n]["faixa"],
            "free": DG["acesso"][n]["free"], "vitoria": DG["acesso"][n]["vitoria"],
            "mes": DG["acesso"][n]["mes"],
            "generalista": DG["acesso"][n].get("generalista", False)}
        for n in F
    },
}

if CHECKOUT_URL:
    oferta_cta = (f'<a class="btn-cta" href="{CHECKOUT_URL}" target="_blank" rel="noopener">'
                  f'Quero a stack completa por {PRECO} →</a>')
    oferta_nota = "Pagamento único. Acesso na hora."
else:
    oferta_nota = ("Ainda estou fechando o checkout. Manda <b>STACK</b> no direct que você "
                   "entra na lista e recebe com o preço de lançamento.")
    oferta_cta = (f'<a class="btn-cta" href="{INSTA}" target="_blank" rel="noopener">'
                  f'Entrar na lista pelo direct →</a>')

faixa_itens = "".join(
    f'<span><b>{escape(n)}</b>{escape(txt)}</span>' for n, txt in d["faixa"]
)

PD = d["pedidos"]
# alturas fixas da onda: nada de aleatório, o build tem que ser reprodutível
ONDA = [7, 12, 18, 9, 22, 14, 26, 11, 19, 8, 24, 16, 10, 21, 13, 6, 17, 23, 9, 12]
onda = "".join(f'<i style="height:{h}px"></i>' for h in ONDA)

casos = "".join(
    f'<article class="caso">'
    f'<span class="caso-tag">{escape(tag)}</span>'
    f'<h3>{escape(titulo)}</h3>'
    f'<div class="audio"><span class="play">▶</span><span class="onda">{onda}</span>'
    f'<span class="dur">{escape(dur)}</span></div>'
    f'<p class="caso-fala">“{escape(fala)}”</p>'
    f'<div class="caso-resp">'
    f'<span class="linha-r"><b>Ferramenta</b><i></i></span>'
    f'<span class="linha-r"><b>Prompt pronto</b><i class="i2"></i></span>'
    f'<span class="selo-mapa">🔒 no seu mapa</span>'
    f'</div></article>'
    for tag, titulo, fala, dur in PD["casos"]
)
outros = "".join(f"<span>{escape(o)}</span>" for o in PD["outros"])

# ---------- oferta ----------

OF = d["oferta"]
PRECO_N = OF["preco"]

entregaveis = "".join(
    f'<li><b>{escape(titulo)}</b><span>{escape(txt)}</span></li>'
    for titulo, txt in OF["entregaveis"]
)
garantias_of = "".join(f"<span>{escape(x)}</span>" for x in OF["garantias"])
para_quem = "".join(
    f'<div class="pq-card {"sim" if i == 0 else "nao"}"><b>{escape(t2)}</b><p>{escape(txt)}</p></div>'
    for i, (t2, txt) in enumerate(OF["para_quem"])
)

# O botão do fim do quiz ficava a 582px da dobra no iPhone e a 815px num Android pequeno,
# medido em 19/08: a pessoa via o resultado e não via como comprar. A correção pontual 2 da
# Frente 6 do playbook é justamente essa. Este é o mesmo link, logo abaixo do resultado, e o
# JS decora os dois com a UTM e o código.
if CHECKOUT_URL:
    botao_topo = (f'<a class="btn-cta" href="{CHECKOUT_URL}" target="_blank" rel="noopener">'
                  f'Desbloquear as minhas 3 por R$ {OF["preco"]} →</a>')
    botao_compra = (f'<a class="btn-cta" href="{CHECKOUT_URL}" target="_blank" rel="noopener">'
                    f'Quero a minha stack por R$ {PRECO_N} →</a>')
    botao_oferta = (f'<a class="btn-cta" href="{CHECKOUT_URL}" target="_blank" rel="noopener" '
                    f'data-pronto="Quero a minha stack por R$ {PRECO_N} →">'
                    f'Fazer o diagnóstico e desbloquear por R$ {PRECO_N} →</a>')
    aviso_compra = "Pagamento único, acesso imediato e 7 dias de garantia."
else:
    botao_topo = ""
    botao_compra = (f'<a class="btn-cta" href="{INSTA}" target="_blank" rel="noopener">'
                    f'Entrar na lista de lançamento →</a>')
    botao_oferta = botao_compra
    aviso_compra = ("O checkout abre em instantes. Manda <b>STACK</b> no direct que você entra na "
                    "lista e leva o preço de lançamento.")

# ---------- números e faq ----------

CT = d["conta"]
conta_linhas = "".join(
    f'<li><span class="c-txt">{escape(txt)}</span>'
    f'<span class="c-val">{escape(val)}<i>{escape(per)}</i></span></li>'
    for txt, val, per in CT["linhas"]
)

faq_html = "".join(
    f"<details><summary>{escape(p)}</summary><p>{escape(r)}</p></details>"
    for p, r in d["faq"]
)

# ---------- hero: prévia da busca ----------

# avatar do remetente no mockup: a marca, sem inventar pessoa
ico_zap = '<span class="av">?</span>'

# Dados estruturados: ajuda o Google a entender que é uma lista de recomendações.
schema = json.dumps({
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Product",
            "name": OF["nome"],
            "description": OF["promessa"],
            "brand": {"@type": "Brand", "name": "Alison Araújo"},
            "offers": {
                "@type": "Offer",
                "price": OF["preco"],
                "priceCurrency": "BRL",
                "availability": "https://schema.org/InStock",
                "url": f"{SITE}/#oferta",
            },
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": p,
                 "acceptedAnswer": {"@type": "Answer", "text": r}}
                for p, r in d["faq"]
            ],
        },
    ],
}, ensure_ascii=False, separators=(",", ":"))


# Snippet oficial do Meta. Fica fora da f-string do template: o código do Meta tem
# chaves e seria interpretado como campo de interpolação.
PIXEL = ""
if PIXEL_META:
    PIXEL = ("""<script>
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','__ID__');fbq('track','PageView');
</script>
<noscript><img height="1" width="1" style="display:none" alt=""
src="https://www.facebook.com/tr?id=__ID__&ev=PageView&noscript=1"></noscript>
""").replace("__ID__", PIXEL_META)

# gtag oficial do Google. Fora da f-string do template pelo mesmo motivo do pixel:
# o snippet tem chaves e seria lido como campo de interpolação.
GA4 = ""
if GA4_ID:
    GA4 = ("""<script async src="https://www.googletagmanager.com/gtag/js?id=__ID__"></script>
<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}
gtag('js',new Date());gtag('config','__ID__');
</script>
""").replace("__ID__", GA4_ID)

JS = """
  const el = id => document.getElementById(id);

  // Meta: PROD é o nome da variante, e é ele que separa o teste no Events Manager.
  const px = ev => window.fbq && fbq("track", ev, {content_name: PROD});
  // o mesmo evento vai para os dois: o Meta é quem otimiza a campanha, o GA4 é quem quebra
  // por UTM sem cobrar. Nome em português e em snake_case, que é como o relatório lê melhor.
  const ga = (ev, extra) => window.gtag && gtag("event", ev, Object.assign({ variante: PROD }, extra || {}));
  // a origem viaja junto para a Cakto: sem ela toda venda aparece como direta
  const origem = origemTrafego();
  let abrirDiagnostico = () => {};
  const checkoutComDiagnostico = a => {
    try {
      return /^qia2_.{8,}\\.[A-Za-z0-9_-]{20,}$/.test(new URL(a.href).searchParams.get("sck") || "");
    } catch (_) { return false; }
  };
  for (const a of document.querySelectorAll('a[href*="pay.cakto.com.br"]')) {
    if (origem) a.href += (a.href.includes("?") ? "&" : "?") + origem;
    a.addEventListener("click", e => {
      // Comprar antes de responder cria um pedido sem diagnóstico, perde o acesso automático
      // e obriga o cliente a refazer o quiz depois de pagar. O checkout só abre quando o sck
      // já leva código + claim; antes disso, o mesmo clique começa ou retoma o diagnóstico.
      if (!checkoutComDiagnostico(a)) {
        e.preventDefault();
        abrirDiagnostico(e);
        return;
      }
      px("InitiateCheckout");
      ga("iniciou_checkout", { currency: "BRL" });
    });
  }

  // diagnóstico: soma os pesos das respostas e devolve as 3 ferramentas com a ordem de compra
  const quiz = el("quiz");
  const modal = el("modal");
  // o quiz vive num pop-up: quem só leu a página não abandonou quiz nenhum, e não pode
  // entrar na conta de abandono
  let abriuQuiz = false;
  if (modal) {
    // O pop-up não existia no histórico: um gesto de voltar no meio do quiz levava a pessoa
    // para fora do site, com metade das respostas dadas. Empilhando um estado, o voltar passa
    // a fechar o pop-up, que é o que qualquer pessoa espera de um modal no celular.
    let noHistorico = false;
    const abrir = e => {
      e.preventDefault();
      modal.showModal();
      abriuQuiz = true;
      px("ViewContent");
      ga("abriu_diagnostico");
      document.body.classList.add("travado");
      if (!noHistorico) { history.pushState({ diag: 1 }, "", location.href); noHistorico = true; }
      modal.querySelector(".passo:not([hidden]) .opc")?.focus();
    };
    abrirDiagnostico = abrir;
    for (const b of document.querySelectorAll(".abre-diag")) b.addEventListener("click", abrir);
    // quem já respondeu parte e voltou não recomeça do zero: o quiz retoma na primeira
    // pergunta sem resposta, e quem já tinha terminado cai direto no resultado
    window.__retomar = () => {};
    for (const b of document.querySelectorAll(".abre-diag"))
      b.addEventListener("click", () => window.__retomar());
    // o × também passa pela tela de saída: fechar o pop-up é tentar sair, e era o caminho
    // em que a pessoa sumia sem nem a pergunta
    el("fecha").addEventListener("click", () => { if (!segurar()) modal.close(); });

    // Voltar com o quiz começado mostra o que a pessoa perde, uma vez só. Quem insiste sai:
    // segurar duas vezes deixa de ser retenção e vira sequestro do botão do navegador.
    // Uma vez em cada momento, porém, e não uma vez na vida: a tela do meio do quiz segura,
    // e a do fim entrega o código do diagnóstico. Quem já tinha sido segurado na pergunta 5
    // ficava sem o código ao sair no resultado, que é justamente quem mais precisa dele.
    const jaSegurou = { meio: false, pronto: false };

    // A tela de saída, usada pelos dois caminhos de fechar: o gesto de voltar e o ×.
    // Devolve true quando segurou, e false quando é para deixar sair de vez.
    const segurar = () => {
      const ret = el("retencao");
      const pronto = !el("resultado").hidden;
      const comecou = document.querySelector("#quiz .passo:not([hidden])")?.dataset.q !== "area"
                   || pronto;
      const momento = pronto ? "pronto" : "meio";
      if (!ret || jaSegurou[momento] || !comecou) return false;
      jaSegurou[momento] = true;
      el("ret-passo1").hidden = false;
      el("ret-passo2").hidden = true;
      el("retencao-titulo").textContent = pronto
        ? "O seu diagnóstico já está pronto"
        : "Falta pouco pro seu mapa";
      const contador = window.__contador || "";
      // nada de "você vai perder tudo": a página guarda as respostas a cada clique, e
      // assustar com o que não acontece é da mesma família da escassez inventada
      el("retencao-txt").textContent = pronto
        ? "As suas 3 já foram calculadas. Sair agora não apaga nada: as respostas ficam neste aparelho."
        : (contador ? "Você já respondeu " + contador + ". " : "")
          + "Sair agora não apaga nada: as respostas ficam neste aparelho.";
      el("retencao-fica").textContent = pronto ? "Ver o meu resultado" : "Continuar de onde parei";
      // o WhatsApp é o único app que a pessoa tem nos dois aparelhos, e o link vai com o
      // código dentro: do outro lado é um toque, sem digitar nada. O link é o DESTA página,
      // nunca o da entrega paga. O código devolve somente as respostas e o teaser.
      if (pronto && window.__codigo) {
        const texto = "O meu diagnóstico do " + PROD + ": " + window.__codigo
          + ". O link abre direto neste resultado gratuito, em qualquer aparelho: "
          + location.origin + location.pathname + "?c=" + encodeURIComponent(window.__codigo);
        el("ret-codigo-valor").textContent = window.__codigo;
        el("ret-codigo-zap").href = "https://wa.me/?text=" + encodeURIComponent(texto);
        el("saida-enviar").href = "https://wa.me/?text=" + encodeURIComponent(texto);
      }
      ret.hidden = false;
      // quem rolou o resultado estava com o topo do pop-up fora da tela, e a retenção nasce
      // lá em cima: sem isto ela aparecia para o código e não para a pessoa
      ret.scrollIntoView({ block: "start" });
      return true;
    };

    window.addEventListener("popstate", () => {
      noHistorico = false;
      if (!modal.open) return;
      if (!segurar()) { modal.close(); return; }
      history.pushState({ diag: 1 }, "", location.href);
      noHistorico = true;
    });
    modal.addEventListener("close", () => document.body.classList.remove("travado"));
    // clique no fundo fecha, igual ao que todo mundo espera de modal
    modal.addEventListener("click", e => { if (e.target === modal) modal.close(); });
  }
  if (quiz) {
    const passos = [...quiz.querySelectorAll(".passo")];
    const resp = {};
    const livre = {};        // o que a pessoa escreveu quando nenhuma opção era a dela
    let atual = 0;
    let terminouQuiz = false;

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
      // o porquê vive na primeira tela: depois dela a pessoa já está dentro
      const porque = el("modal-porque");
      if (porque) porque.hidden = atual !== 0;
      const fila = passos.map((_p, i) => i).filter(vale);
      const pos = fila.indexOf(atual);
      // o passo atual conta como iniciado: barra vazia na pergunta 1 derruba a conclusão
      el("barra-fill").style.width = ((pos + 0.4) / fila.length * 100) + "%";
      const num = passos[atual].querySelector(".num");
      // o total sai da fila, não de uma constante: com pergunta condicional, um número fixo
      // mentiria para quem pula duas, e contador que mente faz abandonar o quiz
      if (num && ehPergunta(atual)) {
        num.textContent = fila.filter(i => i <= atual && ehPergunta(i)).length
                        + " de " + totalPerguntas();
        // guardado porque o break não tem contador, e a retenção do voltar precisa dele
        window.__contador = num.textContent;
      }
    };

    const proximo = () => { do { atual++; } while (atual < passos.length && !vale(atual)); };
    const calcular = () => calcularStack(MOTOR, resp);

    function render() {
      terminouQuiz = true;
      const { stack, corta } = calcular();
      // memória para o /mapa não pedir tudo de novo, e o anônimo para saber quem responde
      salvarSessao(resp, MOTOR.pids, livre, MOTOR);
      enviarAnalitico(MOTOR.analitico, MOTOR.origem, MOTOR, resp, stack, corta, livre);
      const [qArea, qOrc] = MOTOR.perfil;
      const area = MOTOR.rotulos[qArea][resp[qArea]];
      const orc = MOTOR.rotulos[qOrc][resp[qOrc]];

      el("res-titulo").textContent = "A sua stack está pronta";
      el("res-perfil").textContent = `${area} · ${orc}. Identifiquei ${stack.length} ferramentas pra você.`;

      // O código carrega apenas as respostas. Vai no campo customizado `sck` da Cakto para
      // o webhook associar pagamento e diagnóstico; sozinho ele NÃO abre a entrega paga.
      // Quem tenta sair ainda pode guardá-lo para voltar ao teaser sem refazer o quiz.
      const codigo = gerarCodigo(MOTOR, resp);
      if (codigo) {
        window.__codigo = codigo;
        const claim = claimCheckout();
        for (const a of document.querySelectorAll('a[href*="pay.cakto.com.br"]')) {
          const url = new URL(a.href);
          if (claim) url.searchParams.set("sck", "qia2_" + codigo + "." + claim);
          a.href = url.toString();
        }
        const ofertaPronta = document.querySelector("#oferta [data-pronto]");
        if (ofertaPronta) ofertaPronta.textContent = ofertaPronta.dataset.pronto;
      }

      el("res-stack").innerHTML = stack.map((s, i) => `
        <li class="oculto">
          <div class="res-cab">
            <span class="res-logo-off" aria-hidden="true"></span>
            <div>
              <span class="res-nome-off"></span>
              <span class="res-quando">${s.quando} · ${s.vitoria}</span>
            </div>
            <span class="res-n">${i + 1}</span>
          </div>
          <span class="res-vazio" aria-hidden="true"></span>
        </li>`).join("");

      // O custo saiu dos cards e aparece aqui, que é onde ele joga a favor: no card,
      // somado, ele é a conta que a pessoa vai pagar todo mês, e assusta antes do preço.
      // Aqui é o que ela deixa de pagar. Cada frase só entra se o número a sustentar:
      // "cortar já paga o mapa" com uma ferramenta de R$ 52 seria promessa falsa.
      const custosCorte = corta.map(n => MOTOR.ferramentas[n].mes || 0);
      const somaCorte = custosCorte.reduce((a, b) => a + b, 0);
      const maiorCorte = custosCorte.reduce((a, b) => (a > b ? a : b), 0);
      const emReal = n => "R$ " + n.toLocaleString("pt-BR");
      el("res-corta").innerHTML =
        `<b>E ${corta.length} que você não precisa assinar.</b> `
        + (somaCorte > 0 ? `Juntas dão ${emReal(somaCorte)} por mês. ` : "")
        + (maiorCorte >= MOTOR.preco
            ? `Só a mais cara sai por ${emReal(maiorCorte)}: cortar ela já paga o mapa no primeiro mês.`
            : "O mapa diz quais são e por que nenhuma delas é para agora.");

      quiz.hidden = true;
      // "as suas 3 saem do que você responder aqui" é texto de quem ainda vai responder:
      // quem retoma direto no resultado via essa frase acima da própria stack
      const porqueRender = el("modal-porque");
      if (porqueRender) porqueRender.hidden = true;
      el("resultado").hidden = false;
      el("barra-fill").style.width = "100%";
      el("resultado").scrollIntoView({ block: "center", behavior: "smooth" });
      ga("concluiu_diagnostico", { area });
      el("res-titulo").focus();   // leitor de tela precisa saber que o resultado chegou
    }

    // WhatsApp: máscara e validação de número brasileiro (10 ou 11 dígitos com DDD)
    const zap = el("lead-zap");
    if (zap) {
      zap.addEventListener("input", () => {
        const d = zap.value.replace(/\\D/g, "").slice(0, 11);
        zap.value = d.length > 10 ? `(${d.slice(0,2)}) ${d.slice(2,7)}-${d.slice(7)}`
                  : d.length > 6  ? `(${d.slice(0,2)}) ${d.slice(2,6)}-${d.slice(6)}`
                  : d.length > 2  ? `(${d.slice(0,2)}) ${d.slice(2)}` : d;
      });

      el("lead-ok").addEventListener("click", () => {
        const nome = el("lead-nome").value.trim();
        const digitos = zap.value.replace(/\\D/g, "");
        const aviso = el("lead-aviso");
        if (nome.length < 2) return aviso.textContent = "Escreve o seu nome pra eu saber com quem falo.";
        if (digitos.length < 10) return aviso.textContent = "Confere o WhatsApp: faltou dígito ou o DDD.";

        // envia e mostra o resultado sem esperar: a pessoa cumpriu a parte dela
        const { stack, corta } = calcular();
        const respostas = {};
        for (const [q, i] of Object.entries(resp)) respostas[q] = MOTOR.rotulos[q][i];
        try {
          if (DESTINO !== "DEMO") fetch(DESTINO, {
            method: "POST", mode: "no-cors", keepalive: true,
            headers: { "Content-Type": "text/plain;charset=utf-8" },
            body: JSON.stringify({
              nome, whatsapp: digitos, respostas,
              stack: stack.map(s => s.nome), cortar: corta,
              em: new Date().toISOString()
            })
          }).catch(() => {});
        } catch (e) { /* nunca travar o resultado por causa do envio */ }
        render();
      });
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
      // trocar a área depois de voltar derruba a trilha antiga
      limparOrfas(MOTOR, resp);
      // guarda a cada resposta, não só no fim: quem fecha no meio do quiz perdia tudo, e a
      // retenção do voltar promete justamente que não perde
      salvarSessao(resp, MOTOR.pids, livre, MOTOR);
        for (const irmao of b.parentNode.children)
          irmao.setAttribute("aria-pressed", String(irmao === b));
        if (abrirCampo(b)) return;
        proximo();
        if (atual < passos.length) mostrar(); else render();   // sem passo de contato, vai direto
      });
    }

    // retomada: aplica o que já foi respondido neste aparelho e anda até o que falta
    let jaRetomou = false;
    window.__retomar = () => {
      if (jaRetomou) return;
      const salvas = lerSessao(r => pidsExigidos(MOTOR, r), MOTOR);
      if (!salvas) return;
      jaRetomou = true;
      Object.assign(resp, salvas.resp);
      Object.assign(livre, salvas.livre);
      for (const b of quiz.querySelectorAll(".opc"))
        if (resp[b.dataset.q] === +b.dataset.i) b.setAttribute("aria-pressed", "true");
      if (salvas.completa) { render(); return; }
      atual = -1;
      do { atual++; } while (atual < passos.length
                             && (!vale(atual) || (MOTOR.pids.includes(passos[atual].dataset.q)
                                                  && passos[atual].dataset.q in resp)));
      if (atual < passos.length) mostrar(); else render();
    };

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

    const ret = el("retencao");
  if (ret) {
    const sair = () => { ret.hidden = true; modal.close(); };
    el("retencao-fica").addEventListener("click", () => { ret.hidden = true; });

    // Confirmar a saída com o diagnóstico pronto abre o pedido de contato, que é o último
    // ponto em que dá para continuar a conversa com quem não comprou. Quem sai no meio do
    // quiz sai direto: sem as respostas todas não existe código, e pedir o número sem ter
    // o que entregar seria pedágio.
    el("retencao-sai").addEventListener("click", () => {
      if (el("resultado").hidden || !window.__codigo) return sair();
      el("ret-passo1").hidden = true;
      el("ret-passo2").hidden = false;
      ret.scrollIntoView({ block: "start" });
      el("saida-nome").focus();
    });
    el("saida-nao").addEventListener("click", sair);

    // máscara e validação de número brasileiro (10 ou 11 dígitos com DDD)
    const zapSaida = el("saida-zap");
    zapSaida.addEventListener("input", () => {
      const d = zapSaida.value.replace(/\\D/g, "").slice(0, 11);
      zapSaida.value = d.length > 10 ? `(${d.slice(0,2)}) ${d.slice(2,7)}-${d.slice(7)}`
                     : d.length > 6  ? `(${d.slice(0,2)}) ${d.slice(2,6)}-${d.slice(6)}`
                     : d.length > 2  ? `(${d.slice(0,2)}) ${d.slice(2)}` : d;
    });

    // é um link de verdade, com o href já montado: validar aqui e deixar o clique seguir é
    // o que faz o WhatsApp abrir sem esbarrar no bloqueio de pop-up do celular
    el("saida-enviar").addEventListener("click", e => {
      const nome = el("saida-nome").value.trim();
      const digitos = zapSaida.value.replace(/\\D/g, "");
      const aviso = el("saida-aviso");
      if (nome.length < 2) {
        e.preventDefault();
        aviso.textContent = "Escreve o seu nome pra eu saber com quem falo.";
        return;
      }
      if (digitos.length < 10) {
        e.preventDefault();
        aviso.textContent = "Confere o WhatsApp: faltou dígito ou o DDD.";
        return;
      }
      const { stack, corta } = calcular();
      enviarLead(MOTOR.analitico, MOTOR, resp, stack, corta, livre, nome, digitos);
      px("Lead");
      ga("lead_saida");
      // a conversa abre em outra aba, então esta fica: quem volta encontra o código na tela,
      // e não uma janela que sumiu depois de pedir o número dela
      el("saida-campos").hidden = true;
      el("saida-titulo").textContent = "Pronto, mandei no seu WhatsApp";
      el("saida-txt").textContent = "Se a conversa não abrir, o código está aqui embaixo.";
      el("ret-codigo").hidden = false;
      el("saida-nao").textContent = "Fechar";
    });
    // o botão de copiar existia no HTML sem nenhum listener nesta página: clicar não copiava
    // nada e ainda assim parecia ter copiado
    for (const b of document.querySelectorAll(".m-copiar[data-alvo]")) {
      b.addEventListener("click", async () => {
        try { await navigator.clipboard.writeText(el(b.dataset.alvo).textContent); }
        catch (e) { return; }
        const antes = b.textContent;
        b.textContent = "Copiado";
        setTimeout(() => { b.textContent = antes; }, 1600);
      });
    }
  }

  el("refazer").addEventListener("click", () => {
    limparSessao();          // refazer é para começar do zero, inclusive no que ficou guardado
      for (const k of Object.keys(resp)) delete resp[k];
      for (const b of quiz.querySelectorAll(".opc")) b.setAttribute("aria-pressed", "false");
      atual = 0;
      el("resultado").hidden = true;
      quiz.hidden = false;
      mostrar();
      el("diagnostico").scrollIntoView({ block: "center", behavior: "smooth" });
    });

    // funil: em que pergunta a pessoa parou. É o que diz se as 19 perguntas seguram ou
    // derrubam, e não dava para saber, porque o envio anônimo só sai de quem chega ao fim.
    rastrearFunil(MOTOR.analitico, MOTOR.origem, () => {
      if (!abriuQuiz) return null;
      const passo = passos[Math.min(atual, passos.length - 1)];
      const legenda = passo.querySelector("legend");
      const caminho = passos.map((_p, i) => i).filter(i => vale(i) && ehPergunta(i));
      const [qArea] = MOTOR.perfil;
      return {
        pid: terminouQuiz ? "(concluiu)" : passo.dataset.q,
        // o enunciado sai do DOM porque o contador "n de m" é o primeiro filho do legend
        pergunta: terminouQuiz || !legenda || !legenda.lastChild
                ? "" : legenda.lastChild.textContent.trim(),
        posicao: terminouQuiz ? ""
               : caminho.filter(i => i <= atual).length + " de " + totalPerguntas(),
        respondidas: Object.keys(resp).filter(q => MOTOR.pids.includes(q)).length,
        total: totalPerguntas(),
        area: qArea in resp ? MOTOR.rotulos[qArea][resp[qArea]] : "",
        concluiu: terminouQuiz ? "sim" : ""
      };
    });

    mostrar();

    // quem guardou o link no WhatsApp volta com o código na URL: cai no resultado dela sem
    // responder nada de novo, que é a promessa do botão. Depois do mostrar() inicial de
    // propósito: antes dele, a barra de progresso voltava para a primeira pergunta
    const codigoDaUrl = new URLSearchParams(location.search).get("c");
    const doLink = codigoDaUrl ? lerCodigo(MOTOR, codigoDaUrl) : null;
    if (doLink) {
      salvarSessao(doLink, MOTOR.pids, {}, MOTOR);
      document.querySelector(".abre-diag")?.click();
    }
  }

"""

DESC = ("Responda ao diagnóstico e receba as 3 ferramentas de IA certas para o seu trabalho e "
        "orçamento, na ordem de assinar, com o prompt pronto de cada tarefa da sua área.")

html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(V["titulo"])}</title>
{NOINDEX}
<meta name="description" content="{escape(DESC, quote=True)}">
<meta name="author" content="Alison Araújo">
<link rel="canonical" href="{SITE}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="@aalisonaraujo">
<meta property="og:locale" content="pt_BR">
<meta property="og:url" content="{SITE}/">
<meta property="og:title" content="{escape(V["titulo"], quote=True)}">
<meta property="og:description" content="As 3 IAs certas pro seu trabalho, na ordem de assinar, com o prompt de cada uma. R$ 67.">
<meta property="og:image" content="{SITE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(V["titulo"], quote=True)}">
<meta name="twitter:description" content="As 3 IAs certas pro seu trabalho, na ordem de assinar, com o prompt de cada uma. R$ 67.">
<meta name="twitter:image" content="{SITE}/og.png">
<meta name="theme-color" content="#0c0a10">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap">
<script type="application/ld+json">{schema}</script>
{PIXEL}{GA4}<style>
{CSS}
</style>
</head>
<body>

<a class="pula" href="#oferta">Pular para a oferta</a>

<nav class="nav">
  <div class="nav-in">
    <span class="marca"><span class="bolha">?</span> <span class="marca-nome">{escape(V["marca"])}</span></span>
    <div class="nav-links">
      <a href="#diagnostico">Diagnóstico</a>
      <a href="#oferta">O que vem</a>
      <a href="#prova">Resultados</a>
    </div>
    <a class="btn-nav abre-diag" href="#diagnostico">Descobrir a minha stack →</a>
  </div>
</nav>

<header class="hero">
  <div class="env">
    <div>
      <h1>Pare de assinar IA<br>que você <span class="g">não usa.</span></h1>
      <!-- o H1 tem 2 linhas por desenho: se mudar a copy, confira a quebra em 1440 e em 390 -->
      <p class="tese">
        <b class="crenca">{escape(DG["crenca"])}</b>
        Responde o diagnóstico e recebe a sua stack: as 3 certas pro seu trabalho e orçamento,
        na ordem de assinar, <b>com o prompt exato de cada uma</b>.
      </p>
      <div class="acoes">
        <a class="btn btn-p abre-diag" href="#diagnostico">Descobrir a minha stack →</a>
        <a class="btn" href="#oferta">Ver o que vem no mapa</a>
      </div>
      <ul class="bullets">
        <li>Diagnóstico de 2 minutos</li>
        <li>Pagamento único de R$ {PRECO_N}</li>
        <li>7 dias de garantia</li>
      </ul>
    </div>

    <div class="fone" aria-hidden="true">
      <div class="fone-tela zap">
        <span class="ilha"></span>

        <div class="status status-claro">
          <span class="hora">12:45</span>
          <span class="sinais">
            <svg width="17" height="11" viewBox="0 0 17 11" fill="currentColor">
              <rect x="0" y="7.5" width="3" height="3.5" rx="1"/>
              <rect x="4.5" y="5.5" width="3" height="5.5" rx="1"/>
              <rect x="9" y="3" width="3" height="8" rx="1"/>
              <rect x="13.5" y="0" width="3" height="11" rx="1"/>
            </svg>
            <svg width="15" height="11" viewBox="0 0 15 11" fill="none">
              <path d="M1 3.6a9.5 9.5 0 0113 0" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M3.6 6.3a5.8 5.8 0 017.8 0" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              <circle cx="7.5" cy="9.3" r="1.3" fill="currentColor"/>
            </svg>
            <svg width="27" height="13" viewBox="0 0 27 13" fill="none">
              <rect x="0.6" y="0.6" width="22.8" height="11.8" rx="3.6" fill="currentColor" fill-opacity=".28"/>
              <rect x="1.8" y="1.8" width="12.6" height="9.4" rx="2.6" fill="currentColor"/>
              <text x="18" y="9.3" font-size="7.6" font-weight="600" fill="currentColor" text-anchor="middle">41</text>
              <path d="M25 4.6v3.8a2.1 2.1 0 000-3.8z" fill="currentColor" fill-opacity=".4"/>
            </svg>
          </span>
        </div>

        <div class="zap-topo">
          <svg class="volta" width="11" height="19" viewBox="0 0 11 19" fill="none">
            <path d="M9.5 1.5L2 9.5l7.5 8" stroke="#000" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="zap-ava">?</span>
          <span class="zap-quem">Qual IA abrir</span>
          <svg class="zap-ico" width="24" height="16" viewBox="0 0 24 16" fill="none">
            <rect x="1" y="1" width="15.5" height="14" rx="4" stroke="#000" stroke-width="1.9"/>
            <path d="M18.6 6.2l3.4-2.4a.6.6 0 011 .5v7.4a.6.6 0 01-1 .5l-3.4-2.4z" stroke="#000" stroke-width="1.9" stroke-linejoin="round"/>
          </svg>
          <svg class="zap-ico" width="19" height="19" viewBox="0 0 19 19" fill="none">
            <path d="M4.2 1.6c.7-.3 1.5 0 1.8.7l1.2 2.5c.3.6.1 1.3-.4 1.7l-1.1.9a10.5 10.5 0 004.9 4.9l.9-1.1c.4-.5 1.1-.7 1.7-.4l2.5 1.2c.7.3 1 1.1.7 1.8l-.7 1.5c-.3.7-1 1.1-1.8 1A15.4 15.4 0 011.7 3.6c-.1-.8.3-1.5 1-1.8z" stroke="#000" stroke-width="1.8" stroke-linejoin="round"/>
          </svg>
        </div>

        <div class="zap-corpo">
          <div class="push">
            <span class="push-ico">?</span>
            <div class="push-txt">
              <b>{escape(V["nome"])}</b><i>agora</i>
              <span>Seu prompt de carrossel está pronto 📋</span>
            </div>
          </div>

          <span class="zap-dia">HOJE</span>

          <div class="msg eu b1">Quero criar um carrossel hoje<span class="hr">15:41<b>✓✓</b></span></div>

          <div class="msg ele b2">
            <span class="quem">{ico_zap}<b>Assessor de IA</b><span class="ver">✓</span><i>· diagnóstico</i></span>
            É pra <b>vender</b>, <b>ensinar</b> ou <b>crescer</b>?
            <span class="hr">15:41</span>
          </div>

          <div class="msg eu b3">Ensinar<span class="hr">15:41<b>✓✓</b></span></div>

          <div class="msg ele b4">
            <span class="quem">{ico_zap}<b>Assessor de IA</b><span class="ver">✓</span><i>· resultado</i></span>
            Então não é o ChatGPT ❌<br>
            Abre o <b>Claude</b> ✅
            <span class="zap-prompt">
              <i>Prompt pronto</i>
              7 slides. Capa que quebra uma crença. <b>1 ideia por slide</b>, máximo 12 palavras. Fecha pedindo pra salvar.
            </span>
            <span class="hr">15:41</span>
          </div>

          <div class="chips-zap b5"><span>Carrossel</span><span>Claude</span><span>Ensinar</span></div>
        </div>

        <div class="zap-input">
          <svg class="mais" width="22" height="22" viewBox="0 0 22 22" fill="none">
            <path d="M11 3v16M3 11h16" stroke="#3c3c43" stroke-width="1.9" stroke-linecap="round"/>
          </svg>
          <span class="campo">
            <svg width="17" height="17" viewBox="0 0 17 17" fill="none">
              <path d="M1 5.5A4.5 4.5 0 015.5 1h6A4.5 4.5 0 0116 5.5v2.9c0 .5-.2 1-.6 1.4l-5.6 5.6c-.4.4-.9.6-1.4.6H5.5A4.5 4.5 0 011 11.5z" stroke="#8e8e93" stroke-width="1.5"/>
              <path d="M16 8.3h-3.6a3 3 0 00-3 3V15" stroke="#8e8e93" stroke-width="1.5"/>
            </svg>
          </span>
          <svg class="zap-cam" width="22" height="19" viewBox="0 0 22 19" fill="none">
            <path d="M1 6.2A2.2 2.2 0 013.2 4h2.3l1.3-2.2h8.4L16.5 4h2.3A2.2 2.2 0 0121 6.2v9.1a2.2 2.2 0 01-2.2 2.2H3.2A2.2 2.2 0 011 15.3z" stroke="#3c3c43" stroke-width="1.7" stroke-linejoin="round"/>
            <circle cx="11" cy="10.4" r="3.7" stroke="#3c3c43" stroke-width="1.7"/>
          </svg>
          <svg class="zap-mic" width="15" height="20" viewBox="0 0 15 20" fill="none">
            <rect x="4.6" y="1" width="5.8" height="10.6" rx="2.9" stroke="#3c3c43" stroke-width="1.7"/>
            <path d="M1.6 9.2v1.2a5.9 5.9 0 0011.8 0V9.2M7.5 16.3V19" stroke="#3c3c43" stroke-width="1.7" stroke-linecap="round"/>
          </svg>
        </div>
        <span class="indicador"></span>
      </div>
    </div>
  </div>
</header>

<div class="faixa" aria-hidden="true">
  <div class="faixa-in">{faixa_itens}{faixa_itens}</div>
</div>

<section class="sec">
  <div class="env">
    <div class="cabeca">
      <span class="eyebrow">Por que não está funcionando</span>
      <h2>O problema não é falta de ferramenta.<br><span class="g">É não saber qual abrir.</span></h2>
      <p>Se você se reconhecer em duas dessas quatro, o mapa resolve em menos de uma semana.</p>
    </div>
    <div class="cinco-grid">{problemas}</div>
  </div>
</section>

<section class="sec sec-cor" id="pedidos">
  <div class="env">
    <div class="cabeca">
      <span class="eyebrow">Serve pra qualquer pedido</span>
      <h2>Você fala do seu jeito.<br>O mapa responde as duas.</h2>
      <p>Qual ferramenta abrir <b>e</b> o prompt exato pra pedir. Vale pro consultório, pro
         escritório e pro fechamento do mês, e vale igual pra passagem, a hospedagem e a
         compra que você adia há semanas. <b>Não é só trabalho.</b></p>
    </div>
    <div class="casos">{casos}</div>
    <div class="outros-pedidos">{outros}</div>
    <div class="acoes" style="justify-content:center;margin-top:30px">
      <a class="btn btn-p abre-diag" href="#diagnostico">Descobrir a minha stack →</a>
    </div>
  </div>
</section>

<section class="sec diag-sec" id="diagnostico">
  <div class="env">
    <div class="cabeca">
      <span class="eyebrow">Como funciona</span>
      <h2>Você não precisa de mais ferramentas.<br><span class="g">Precisa saber quais três usar.</span></h2>
      <p>Um diagnóstico rápido sobre o seu trabalho e o seu orçamento. O mapa sai do seu contexto:
         as três ferramentas certas, na ordem de assinar, com o prompt exato de cada uma e a
         conta do que você corta.</p>
    </div>

    <div class="diag-chamada">
      <ul class="diag-passos">
        <li><b>1</b> Responde às perguntas do seu perfil</li>
        <li><b>2</b> Recebe a sua stack e os prompts</li>
        <li><b>3</b> Aplica com o prompt pronto</li>
      </ul>
      <button type="button" class="btn btn-p abre-diag">{escape(V["headline"])} →</button>
      <p class="diag-nota">{escape(DG["aviso_custo"])}</p>
    </div>
  </div>
</section>

<section class="sec sec-claro">
  <div class="env">
    <div class="banner">
      <div class="b-txt">
        <h3>Para de assinar IA que você não usa.</h3>
        <p>O diagnóstico diz quais três valem pro seu trabalho e orçamento, e o que cortar agora.</p>
      </div>
      <a class="btn btn-p abre-diag" href="#diagnostico">Descobrir a minha stack →</a>
    </div>
  </div>
</section>

<section class="sec" id="ferramentas">
  <div class="env">
    <div class="cabeca">
      <span class="eyebrow">{escape(ESC["eyebrow"])}</span>
      <h2>{escape(ESC["titulo"])}<br><span class="g">{escape(ESC["titulo_2"])}</span></h2>
      <p>{escape(ESC["sub"])}</p>
    </div>
    <span class="esc-rot">{escape(ESC["conhecidas_rot"])}</span>
    <div class="ferr-grid ferr-grid-4">{cards}</div>
    <span class="esc-rot esc-rot-2">{escape(ESC["sem_nome_rot"])}</span>
    <ul class="esc-lista">{ocultas}</ul>
    <p class="esc-fecho">{escape(ESC["fecho"])}</p>
  </div>
</section>

<section class="sec sec-claro">
  <div class="env">
    <div class="cabeca">
      <span class="eyebrow">Por onde começar</span>
      <h2>Não tem um jeito certo de usar.<br><span class="g">Tem a sua semana.</span></h2>
      <p>As tarefas estão separadas por tipo de trabalho. Escolhe a categoria que mais aparece
         na sua semana e começa por ela.</p>
    </div>
    <div class="orbita">
      {teia}
      <ul class="orbes">{orbita_itens}</ul>
      <span class="orbita-nucleo" aria-hidden="true">
        <svg width="26" height="26" viewBox="0 0 20 20" fill="none">
          <circle cx="8.6" cy="8.6" r="5.4" stroke="currentColor" stroke-width="2.2"/>
          <path d="M12.9 12.9l4.2 4.2" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
        </svg>
      </span>
    </div>
  </div>
</section>

<section class="sec" id="prova">
  <div class="env">
    <div class="cabeca">
      <span class="eyebrow">A conta que ninguém faz</span>
      <h2>Errar sai mais caro<br><span class="g">do que acertar.</span></h2>
      <p>Não é o preço da IA que pesa. É o da que você assina, não abre e esquece de cancelar.</p>
    </div>

    <div class="conta">
      <ul class="conta-lista">{conta_linhas}</ul>
      <div class="conta-fecho">
        <span class="c-txt"><b>{escape(CT["fecho"][0])}</b></span>
        <span class="c-val">{escape(CT["fecho"][1])}<i>{escape(CT["fecho"][2])}</i></span>
      </div>
      <p class="conta-remate">{escape(CT["remate"])}</p>
      <div class="acoes" style="justify-content:center">
        <a class="btn btn-p abre-diag" href="#diagnostico">Descobrir a minha stack →</a>
      </div>
      <p class="conta-rodape">{escape(CT["rodape"])}</p>
    </div>
  </div>
</section>

{prova_html}
<section class="sec sec-claro" id="oferta">
  <div class="env">
    <div class="cabeca">
      <span class="eyebrow">O mapa completo</span>
      <h2>A ferramenta certa é metade.<br><span class="g">O prompt certo é a outra.</span></h2>
      <p>{escape(OF["promessa"])}</p>
    </div>

    <div class="para-quem">{para_quem}</div>

    <div class="oferta-card">
      <div class="oferta-topo">
        <span class="selo-rosa">{escape(OF["nome"])}</span>
        <div class="preco">
          <span class="de">de R$ {OF["de"]} por</span>
          <span class="valor"><b>R$</b>{PRECO_N}</span>
          <span class="unico">pagamento único</span>
        </div>
        {botao_oferta}
        <p class="form-aviso">{aviso_compra}</p>
        <div class="garantias">{garantias_of}</div>
      </div>
      <div class="inclusos">
        <div class="inclusos-topo">
          <span class="rot">O que vem no mapa</span>
          <span class="selo-verde">{escape(OF["selo_inclusos"])}</span>
        </div>
        <ul class="entregaveis">{entregaveis}</ul>
      </div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="env">
    <div class="cabeca">
      <span class="eyebrow">Tire suas dúvidas</span>
      <h2>Perguntas frequentes</h2>
      <p>O que costumam me perguntar no direct sobre esta lista.</p>
    </div>
    <div class="faq" id="faq">{faq_html}</div>
  </div>
</section>

<section class="sec">
  <div class="env">
    <div class="fecho-card">
      <span class="selo-rosa">Última coisa</span>
      <h2>Você vai abrir uma IA hoje de qualquer jeito.<br><span class="g">A questão é se vai ser a certa.</span></h2>
      <p>
        Em dois minutos você sabe quais três valem pro seu trabalho, em que ordem assinar,
        o prompt exato de cada uma e o que cortar agora. Por <b>R$ {PRECO_N}</b>, uma vez,
        com sete dias de garantia.
      </p>
      <div class="acoes">
        <a class="btn btn-p abre-diag" href="#diagnostico">Descobrir a minha stack →</a>
      </div>
      <p class="fecho-nota">Se em sete dias você achar que não valeu, devolvo o valor inteiro. Sem justificar.</p>
    </div>
  </div>
</section>

<footer class="rodape">
  <div class="env">
    <div class="rodape-topo">
      <div class="rodape-marca">
        <span class="marca"><span class="bolha">?</span> <span class="marca-nome">{escape(V["marca"])}</span></span>
        <p>O mapa que diz qual IA abrir pra cada tarefa do seu trabalho, e o prompt exato
           pra pedir. Feito por quem usa IA em projeto de cliente todo dia.</p>
        <div class="rodape-selos">
          <span>Pagamento único</span><span>7 dias de garantia</span><span>Sem link de afiliado</span>
        </div>
      </div>
      <div class="rodape-col">
        <b>O produto</b>
        <a href="#pedidos">Pra que serve</a>
        <a href="#oferta">O que vem no mapa</a>
        <a href="#prova">Quanto custa errar</a>
        <a class="abre-diag" href="#diagnostico">Descobrir a minha stack</a>
      </div>
      <div class="rodape-col">
        <b>Dúvidas</b>
        <a href="#faq">Perguntas frequentes</a>
        <a href="{INSTA}" target="_blank" rel="noopener">Falar comigo no direct</a>
      </div>
    </div>
    <div class="rodape-base">
      <span>© 2026 Alison Araújo. Todos os direitos reservados.</span>
      <span>Preços das ferramentas conferidos em 18/08/2026 e sujeitos a alteração pelos fornecedores.</span>
    </div>
  </div>
</footer>

<dialog id="modal" class="modal" aria-labelledby="modal-titulo">
  <div class="modal-topo">
    <span class="modal-marca"><span class="bolha">?</span> Diagnóstico</span>
    <button type="button" class="fecha" id="fecha" aria-label="Fechar o diagnóstico">×</button>
  </div>
  <div class="barra" aria-hidden="true"><span id="barra-fill"></span></div>

  <div class="modal-corpo">
    <div class="retencao" id="retencao" hidden>
      <div id="ret-passo1">
        <h3 id="retencao-titulo"></h3>
        <p id="retencao-txt"></p>
        <button type="button" class="btn-cta" id="retencao-fica">Continuar de onde parei</button>
        <button type="button" class="retencao-sai" id="retencao-sai">Sair mesmo assim</button>
      </div>
      <div id="ret-passo2" hidden>
        <h3 id="saida-titulo">Quer o seu diagnóstico no WhatsApp?</h3>
        <p id="saida-txt">Te mando o link que abre este resultado gratuito em qualquer aparelho, sem
           responder de novo.</p>
        <div id="saida-campos">
          <label class="campo-lead">Seu nome
            <input id="saida-nome" type="text" autocomplete="given-name"
                   placeholder="Como posso te chamar?"></label>
          <label class="campo-lead">WhatsApp
            <input id="saida-zap" type="tel" inputmode="numeric" autocomplete="tel"
                   placeholder="(11) 99999-0000" maxlength="16"></label>
          <a class="btn-cta" id="saida-enviar" target="_blank" rel="noopener" href="#">Me manda no WhatsApp</a>
          <p class="form-aviso" id="saida-aviso">Mando o seu diagnóstico e, de vez em quando, o
             que eu aprendo sobre IA. É só pedir para parar.</p>
        </div>
        <div class="res-codigo" id="ret-codigo" hidden>
          <span class="res-codigo-rot">O código do seu diagnóstico</span>
          <code id="ret-codigo-valor"></code>
          <button type="button" class="m-copiar" data-alvo="ret-codigo-valor">Copiar</button>
          <a class="m-copiar" id="ret-codigo-zap" target="_blank" rel="noopener">Guardar no WhatsApp</a>
          <p class="res-codigo-ajuda">Ele traz as suas respostas de volta, sem refazer nada.</p>
        </div>
        <button type="button" class="retencao-sai" id="saida-nao">Não, quero sair</button>
      </div>
    </div>
    <h2 id="modal-titulo" class="modal-h">Qual IA você deveria usar</h2>
    <p class="modal-porque" id="modal-porque">{escape(DG["porque"])}</p>
    <form id="quiz" novalidate>{"".join(perguntas_html)}</form>

    <div id="resultado" role="region" aria-live="polite" aria-label="Resultado do diagnóstico" hidden>
      <div class="res-topo">
        <span class="selo-rosa">Seu resultado</span>
        <h3 id="res-titulo" tabindex="-1">Sua stack</h3>
        <p id="res-perfil"></p>
        <div class="res-cta-topo">
          {botao_topo}
          <p class="res-cta-nota">Os nomes, a ordem, o prompt de cada tarefa e o que cortar.
             Pagamento único, acesso na hora.</p>
        </div>
      </div>
      <ol class="res-stack" id="res-stack"></ol>
      <div class="res-corta" id="res-corta"></div>
      <div class="res-oferta">
        <span class="selo-rosa">Desbloqueie o seu mapa</span>
        <h4>Suas 3 ferramentas, os prompts e o que não assinar.</h4>
        <p>Recebe agora quais são, em que ordem assinar, o <b>prompt pronto de cada tarefa da sua
           área</b>, o tutorial de cada uma e a lista do que cortar, com a conta do que isso te
           devolve por mês.</p>
        <div class="preco-inline">
          <span class="de">de R$ {OF["de"]} por</span>
          <span class="valor"><b>R$</b>{PRECO_N}</span>
        </div>
        {botao_compra}
        <p class="form-aviso">{aviso_compra}</p>
      </div>
      <button type="button" class="refazer" id="refazer">Refazer o diagnóstico</button>
    </div>
  </div>
</dialog>

<script>const DESTINO = {json.dumps(CAPTURA_URL)};
const PROD = {json.dumps(V["nome"], ensure_ascii=False)};
const MOTOR = {json.dumps(motor, ensure_ascii=False, separators=(",", ":"))};{MOTOR_JS}{ESPELHO_JS}{CODIGO_JS}{SESSAO_JS}{JS}</script>
<!-- Medição: Web Analytics ligado no painel da Vercel. Se o script voltar a dar 404,
     é o toggle que caiu, não o caminho. -->
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""

SAIDA.write_text(html, encoding="utf-8")
print(f"gerado: {SAIDA.relative_to(RAIZ)}  ({len(html):,} bytes)")
print(f"  {total} tarefas em {len(d['grupos'])} grupos, {len(F)} ferramentas")
print(f"  conteúdo no HTML, sem depender de JavaScript")
nao_conferido = [n for n, a in DG["acesso"].items() if not a["verificado"]]
if nao_conferido:
    print(f"  AVISO: custo não conferido para {', '.join(nao_conferido)}. O diagnóstico mostra")
    print("         esse texto ao usuário, então confirme o valor no site da ferramenta.")
if CAPTURA_URL == "DEMO":
    print("  ATENÇÃO: CAPTURA_URL em modo DEMO. A tela de contato aparece mas NÃO grava")
    print("           nada. Só para conferência visual. NÃO PUBLICAR ASSIM.")
elif not CAPTURA_URL:
    print("  AVISO: CAPTURA_URL vazia. O diagnóstico vai direto do último passo para o")
    print("         resultado, sem pedir nome e WhatsApp. Preencha a constante para capturar.")
if not CHECKOUT_URL:
    print("  AVISO: CHECKOUT_URL vazia. O resultado do diagnóstico oferece a lista de espera")
    print("         pelo direct em vez do botão de compra.")
