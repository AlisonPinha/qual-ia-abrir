#!/usr/bin/env python3
"""
Gera a matéria de pré-venda em /materia a partir do dados.json.

**Ela não entrega nada, e essa é a decisão inteira.** A /cola entregava 11 tarefas com a IA de
cada uma, e o número disse o que isso fazia: 16 pessoas abriram, nenhuma clicou no CTA. Nem uma.
O motivo não era o botão. Os Shorts do YouTube já entregam "10 tarefas e a IA certa para cada",
a cola entregava 11 e o produto promete 23: a mesma coisa três vezes, cada vez com um pouco
mais. Quem chega na cola já está servido.

A matéria vira o eixo. Em vez de responder, ela mostra o tamanho da pergunta. Ideia do Alison, e
o formato é o do A4 da MODELAGEM-ALAN.md, que já existia como imagem de anúncio: manchete em
terceira pessoa, lead com o mecanismo, foto em contexto. Aqui ela vira página.

**O que NUNCA pode entrar aqui**, senão vira cola outra vez: nome de ferramenta ligado a uma
tarefa, prompt pronto, ordem de assinatura. A matéria fala do erro e do mecanismo; a resposta
mora atrás do diagnóstico.

**Veracidade, que é o único gate que sobrou no projeto:** nenhum nome de veículo, nenhuma
manchete de "última hora", nenhum fato afirmado sobre terceiro. A forma é de portal porque
formato de portal converte melhor (linha 277 do playbook); forjar notícia é outra coisa. A
assinatura no rodapé diz de quem é o conteúdo, e ela não é decorativa.

**A paleta é de portal, não a da marca.** Mesma razão do A2: matéria roxa não parece matéria,
parece banner. A continuidade com a LP se faz pelo rosto e pelo nome.

Uso:  python3 _build/gerar_materia.py
"""
import json
import pathlib
import re
import shutil
import sys

AQUI = pathlib.Path(__file__).parent
RAIZ = AQUI.parent
DADOS = json.loads((AQUI / "dados.json").read_text(encoding="utf-8"))
SAIDA = RAIZ / "public" / "materia"
FOTO_FONTE = RAIZ / "_private" / "criativos-imagem" / "palco-alison-med.jpg"

GA4 = "G-J1383RJMK8"
# o host vem do config, que é onde ele já existe para as LPs
sys.path.insert(0, str(AQUI))
from config import DOMINIO_PRODUCAO as HOST, PIXEL_META  # noqa: E402

problema = DADOS["problema"]
diagnostico = DADOS["diagnostico"]

# A conta refeita em 23/08/2026 na varredura completa (_private/conta_corte.mjs). Os R$ 479 e os
# 91,4% morreram com a saída da Poppy AI; o que sobrou é sobre UMA assinatura, não sobre a soma.
COMBINACOES = "587.776"
PAGA_SOZINHA = "90"

esc = lambda t: (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def blocos_problema():
    """Os quatro modos de errar, do dados.json. São a cena, não a solução."""
    return "\n".join(
        f"""      <li>
        <h3>{esc(t)}</h3>
        <p>{esc(d)}</p>
      </li>"""
        for t, d in problema
    )


# A única frase da matéria escrita à mão em vez de montada do dados.json, e vale explicar por
# quê: os rótulos do `espelho` foram escritos para aparecer ao lado de um valor ("Pode investir
# por mês: R$ 150"), então em série eles truncam ("já foi embora em ferramenta parada, pode
# investir por mês e quer resolver"). A frase abaixo diz as mesmas seis coisas na ordem do
# espelho, e o build quebra se o espelho mudar de tamanho, que é quando ela passaria a mentir.
PERGUNTAS = ("onde a IA entraria primeiro no seu dia, qual tarefa mais come o seu tempo, quantas "
             "horas por semana ela toma, quanto já foi embora em ferramenta que você não abre, "
             "quanto dá para investir por mês e para quando aquilo precisa estar resolvido")
ESPELHO_ESPERADO = 6


CORPO = f"""
    <p class="lead">Quem pede uma coisa para a inteligência artificial e recebe de volta uma
      resposta genérica quase sempre chega à mesma conclusão: essa ferramenta é fraca. E desiste
      dela. Para {esc('Alison Araújo')}, que montou um diagnóstico para resolver exatamente isso,
      as duas explicações mais prováveis quase nunca são consideradas: <strong>abrir a ferramenta
      errada para aquela tarefa, e pedir do jeito errado</strong>.</p>

    <figure>
      <img src="/materia/palco.jpg" width="1200" height="629"
           alt="Alison Araújo durante uma apresentação sobre inteligência artificial"
           fetchpriority="high" decoding="async">
      <figcaption>Alison Araújo durante apresentação. Na tela ao fundo, a segunda causa que ele
        aponta: “quanto melhor você pedir, melhor ele entrega”.</figcaption>
    </figure>

    <p>O roteiro é quase sempre o mesmo, e aparece mais em quem já paga por pelo menos uma
      assinatura. A pessoa abre a
      ferramenta que conhece, pede a tarefa que precisa entregar, recebe algo morno e fecha. No
      dia seguinte repete com outra tarefa, e outra vez o resultado é morno. A conclusão que
      sobra é sempre a mesma, e é a errada.</p>

    <h2>Os quatro jeitos de errar</h2>
    <p>São quatro, e ele descreve cada um falando direto com quem está do outro lado:</p>
    <ol class="padroes">
{blocos_problema()}
    </ol>

    <h2>“Não é que a IA seja fraca”</h2>
    <p>O que essas quatro cenas têm em comum não é a ferramenta. São duas portas que levam ao
      mesmo engano.</p>
    <p><strong>A primeira é abrir a ferramenta errada para aquela tarefa.</strong> Ter várias
      contas de IA não é a mesma coisa que saber qual usar, e é essa distância que faz a pessoa
      desistir justamente da que resolveria o problema dela.</p>
    <p><strong>A segunda, mais comum ainda, é a forma de pedir.</strong> O pedido sai vago, a
      resposta volta genérica, e a culpa cai na ferramenta outra vez. Na maior parte das vezes,
      diz ele, não foi a IA que entregou pouco: foi o pedido que não disse o suficiente para ela
      ter como entregar.</p>
    <p>As duas portas dão no mesmo lugar. A pessoa julga a inteligência artificial pela pior
      tarefa que deu para ela, pedida do pior jeito que soube pedir, e conclui que a tecnologia
      não serve para o trabalho dela.</p>
    <p>O raciocínio dele é simples: não existe a melhor IA, existe a melhor para cada tarefa. A
      mesma tarefa tem resposta diferente conforme quanto tempo ela toma na semana e quanto a
      pessoa pode gastar por mês. E cada uma tem também uma forma própria de ser pedida.</p>

    <div class="cta cta-meio">
      <p>Quer saber quais são as três da sua rotina, e como pedir cada uma?</p>
      <a class="btn" data-diagnostico href="/">Fazer o meu diagnóstico</a>
      <p class="micro">Leva cerca de 2 minutos, sem cadastro.</p>
    </div>

    <h2>{COMBINACOES} combinações. Três são as suas</h2>
    <p>O diagnóstico que ele usa não devolve uma lista de ferramentas boas. Ele cruza as
      respostas e devolve as três que cobrem as tarefas daquela pessoa dentro do orçamento dela,
      mais as que ela deveria cortar. Rodando todas as respostas possíveis, o resultado sai
      diferente em <strong>{COMBINACOES} combinações</strong>.</p>
    <p>É por isso, diz ele, que uma lista pronta não resolve: ela é a mesma para todo mundo, e o
      problema não é.</p>
    <p class="destaque">Na varredura completa dessas combinações, a <strong>maior</strong> das
      assinaturas que o diagnóstico manda cortar paga sozinha o valor do próprio diagnóstico em
      <strong>{PAGA_SOZINHA}% dos casos</strong>. Não é promessa de gastar menos no total: é uma
      conta sobre a assinatura que está saindo do cartão sem ser aberta.</p>

    <h2>O que ele pergunta antes de responder</h2>
    <p>As perguntas são sobre a rotina, não sobre tecnologia: {PERGUNTAS}.</p>
    <p><strong>Nenhuma delas pergunta qual IA a pessoa prefere</strong>, e ele diz que isso é
      proposital. A preferência costuma ser exatamente o que está errado: é ela que faz a pessoa
      abrir a mesma ferramenta para tudo, inclusive para o que aquela ferramenta faz pior.</p>
    <p>Só depois disso o resultado aparece, e responde às duas portas de uma vez: qual ferramenta
      abrir para cada tarefa, em que ordem começar e como pedir cada uma para a resposta não
      voltar genérica.</p>
"""

# Snippet oficial do Meta, fora da f-string pelo mesmo motivo do gerar.py: o código do
# Meta tem chaves e seria interpretado como campo de interpolação.
#
# A matéria PRECISA do pixel, e não é medição opcional: `landing_page_view` da Meta é o
# PageView do pixel disparado no destino. Conjunto que otimiza LANDING_PAGE_VIEWS com o
# anúncio apontado para uma página sem pixel volta `conversions: 0`, que é exatamente o
# defeito que matou a rodada v1 otimizando PURCHASE.
#
# Só PageView. ViewContent na LP significa "abriu o quiz" e reusar o nome aqui misturaria
# duas etapas diferentes do funil no mesmo evento.
PIXEL = ""
if PIXEL_META:
    PIXEL = ("""<script>
if (location.hostname === '__HOST__') {
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','__ID__');fbq('track','PageView');
}
</script>
<noscript><img height="1" width="1" style="display:none" alt=""
src="https://www.facebook.com/tr?id=__ID__&ev=PageView&noscript=1"></noscript>
""").replace("__ID__", PIXEL_META).replace("__HOST__", HOST)

HTML = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Especialista abre o diagnóstico que usa para escolher a IA certa de cada tarefa</title>
<meta name="description" content="Quem recebe resposta genérica acha que a IA é fraca. Quase sempre é a tarefa na ferramenta errada, pedida do jeito errado.">
<meta name="robots" content="noindex">
<link rel="icon" href="/icon.svg">
<meta property="og:type" content="article">
<meta property="og:title" content="Especialista abre o diagnóstico que usa para escolher a IA certa de cada tarefa">
<meta property="og:description" content="Quem recebe resposta genérica acha que a IA é fraca. Quase sempre é a tarefa na ferramenta errada, pedida do jeito errado.">
<meta property="og:url" content="https://diagnostico.noahai.com.br/materia">
<meta property="og:image" content="https://diagnostico.noahai.com.br/materia/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  :root {{
    --tinta: #16181d;
    --fraco: #5b6270;
    --linha: #e3e5ea;
    --vermelho: #d8232a;
    --fundo: #fff;
  }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{
    background: var(--fundo); color: var(--tinta);
    font-family: Archivo, system-ui, -apple-system, sans-serif;
    font-size: 18px; line-height: 1.62;
  }}

  /* Barra de portal. Rótulo, não veículo: não existe jornal chamado "para quem usa IA". */
  .barra {{
    background: var(--vermelho); color: #fff;
    display: flex; align-items: center; justify-content: space-between;
    padding: 13px 20px; gap: 16px;
  }}
  .barra .menu, .barra .lupa {{ width: 22px; height: 22px; flex: none; opacity: .95; }}
  .barra strong {{
    font-weight: 700; font-size: 15px; letter-spacing: .09em; text-transform: uppercase;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }}

  .env {{ max-width: 680px; margin: 0 auto; padding: 0 20px; }}

  .editoria {{
    display: inline-block; margin: 30px 0 14px;
    background: var(--vermelho); color: #fff;
    font-size: 12px; font-weight: 700; letter-spacing: .13em; text-transform: uppercase;
    padding: 5px 10px;
  }}
  h1 {{
    font-family: Anton, Archivo, sans-serif; font-weight: 400;
    font-size: clamp(34px, 8.2vw, 54px); line-height: 1.03; letter-spacing: .004em;
    text-transform: uppercase; margin-bottom: 20px;
  }}
  .lead {{ font-size: clamp(19px, 4.4vw, 22px); line-height: 1.5; color: #2b2f39; }}
  .lead strong {{ color: var(--tinta); }}

  .assinatura {{
    display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: baseline;
    margin: 22px 0 26px; padding-bottom: 16px; border-bottom: 1px solid var(--linha);
    font-size: 14px; color: var(--fraco);
  }}
  .assinatura b {{ color: var(--tinta); font-weight: 600; }}

  figure {{ margin: 28px 0; }}
  figure img {{ width: 100%; height: auto; display: block; background: #eceef2; }}
  figcaption {{
    font-size: 14px; line-height: 1.45; color: var(--fraco);
    padding: 9px 2px 0; border-bottom: 1px solid var(--linha); padding-bottom: 14px;
  }}

  p {{ margin-bottom: 20px; }}
  h2 {{
    font-family: Anton, Archivo, sans-serif; font-weight: 400;
    font-size: clamp(24px, 5.6vw, 32px); line-height: 1.12; text-transform: uppercase;
    margin: 34px 0 14px; letter-spacing: .004em;
  }}

  .padroes {{ list-style: none; margin: 0 0 26px; counter-reset: p; }}
  .padroes li {{
    counter-increment: p; position: relative;
    padding: 0 0 18px 46px; margin-bottom: 18px; border-bottom: 1px solid var(--linha);
  }}
  .padroes li:last-child {{ border-bottom: 0; }}
  .padroes li::before {{
    content: counter(p); position: absolute; left: 0; top: 1px;
    font-family: Anton, sans-serif; font-size: 27px; line-height: 1; color: var(--vermelho);
  }}
  .padroes h3 {{ font-size: 19px; font-weight: 700; margin-bottom: 3px; line-height: 1.3; }}
  .padroes p {{ margin: 0; color: #3b414d; }}

  .destaque {{
    border-left: 4px solid var(--vermelho); background: #faf7f7;
    padding: 17px 18px; margin: 26px 0; font-size: 17px; line-height: 1.55;
  }}

  .cta {{
    margin: 34px 0 10px; padding: 26px 22px; text-align: center;
    background: #f5f6f8; border: 1px solid var(--linha);
  }}
  .cta p {{ font-size: 17px; margin-bottom: 16px; }}
  .btn {{
    display: inline-block; background: var(--vermelho); color: #fff; text-decoration: none;
    font-weight: 700; font-size: 17px; line-height: 1.25;
    padding: 15px 26px; border-radius: 4px;
  }}
  .micro {{ font-size: 13.5px; color: var(--fraco); margin: 12px 0 0; }}

  footer {{
    margin-top: 44px; border-top: 1px solid var(--linha); padding: 22px 0 46px;
    font-size: 13.5px; color: var(--fraco); line-height: 1.6;
  }}
  footer a {{ color: var(--fraco); }}
  footer .selo {{ display: block; margin-bottom: 8px; }}

  @media (min-width: 700px) {{
    body {{ font-size: 19px; }}
    .env {{ padding: 0 24px; }}
  }}
</style>
<script>
  // mesma guarda de host das LPs: QA local não pode virar sessão no relatório
  if (location.hostname === '{HOST}') {{
    var s = document.createElement('script'); s.async = 1;
    s.src = 'https://www.googletagmanager.com/gtag/js?id={GA4}';
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function(){{dataLayer.push(arguments);}};
    gtag('js', new Date());
    gtag('config', '{GA4}');
    gtag('event', 'abriu_materia');
  }}
</script>
{PIXEL}
</head>
<body>
  <header class="barra">
    <svg class="menu" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    <strong>Para quem usa IA</strong>
    <svg class="lupa" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
  </header>

  <article class="env">
    <span class="editoria">Qual IA usar?</span>
    <h1>Especialista abre o diagnóstico que ele usa para escolher a IA certa para cada tarefa</h1>

    <div class="assinatura">
      <span>Por <b>Alison Araújo</b></span>
      <span>·</span>
      <span>Leitura de 3 minutos</span>
    </div>
{CORPO}
    <div class="cta">
      <p><strong>Descubra quais são as suas três.</strong> O diagnóstico é o mesmo que ele usa,
        e devolve a sua stack, a ordem de começar e o que fazer dentro de cada ferramenta.</p>
      <a class="btn" data-diagnostico href="/">Fazer o meu diagnóstico</a>
      <p class="micro">Leva cerca de 2 minutos, sem cadastro, e o resultado aparece na hora.</p>
    </div>
  </article>

  <footer class="env">
    <span class="selo">Este é um conteúdo de Alison Araújo sobre o próprio produto. Não é
      matéria jornalística e não representa nenhum veículo de imprensa.</span>
    © 2026 Alison Araújo · @aalisonaraujo ·
    <a href="/privacidade">Privacidade e exclusão de dados</a>
  </footer>

  <script>{{JS}}</script>
</body>
</html>
"""


def main():
    if not FOTO_FONTE.exists():
        raise SystemExit(f"falta a foto de palco em {FOTO_FONTE}")

    # o cola.js já resolve o que esta página precisa: leva a cadeia de UTM inteira para a LP e
    # descarta o resto. O que muda é o nome do evento, para medir a matéria separada da cola.
    js = (AQUI / "cola.js").read_text(encoding="utf-8").replace(
        "clicou_diagnostico_cola", "clicou_diagnostico_materia"
    )
    html = HTML.replace("{JS}", js)

    SAIDA.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FOTO_FONTE, SAIDA / "palco.jpg")
    (SAIDA / "index.html").write_text(html, encoding="utf-8")

    espelho = len(diagnostico["espelho"])
    if espelho != ESPELHO_ESPERADO:
        raise SystemExit(
            f"o espelho do quiz tem {espelho} itens e a matéria descreve {ESPELHO_ESPERADO}: "
            "reescreva PERGUNTAS antes de gerar, senão a página passa a mentir sobre o quiz")

    proibidas = [f for f in DADOS["diagnostico"]["acesso"] if re.search(rf"\b{re.escape(f)}\b", CORPO)]
    if proibidas:
        raise SystemExit(f"a matéria nomeou ferramenta e virou cola: {', '.join(proibidas)}")

    print(f"gerado: public/materia/index.html  ({len(html):,} bytes)")
    print(f"        public/materia/palco.jpg   ({(SAIDA / 'palco.jpg').stat().st_size:,} bytes)")
    print(f"  {len(problema)} padrões de erro, {COMBINACOES} combinações, corte paga em {PAGA_SOZINHA}%")
    print("  nenhuma ferramenta nomeada, nenhum prompt, nenhuma ordem: a resposta segue atrás do quiz")


if __name__ == "__main__":
    main()
