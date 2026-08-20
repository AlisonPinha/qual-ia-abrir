"""
Constantes de deploy do qual-ia-abrir. Lidas por gerar.py e por gerar_mapa.py,
para não existirem dois lugares onde a mesma URL precisa ser colada.
"""

# Web App do Apps Script que grava o lead do diagnóstico na planilha.
# Vazio: o passo de contato é pulado e o resultado aparece direto, porque prender
# a pessoa num formulário que não salva nada seria perder o lead e a venda.
# "DEMO": mostra a tela para conferência visual, sem enviar nada. Nunca publicar assim.
CAPTURA_URL = ""

# Web App do Apps Script que grava o diagnóstico ANÔNIMO (sem nome e sem WhatsApp).
# Serve para saber qual perfil responde, onde as pessoas abandonam e qual ferramenta
# mais aparece. Pode ser a mesma implantação de CAPTURA_URL: o Apps Script separa
# por "tipo" no payload e grava em abas diferentes.
# Vazio: nada é enviado e nada quebra.
ANALITICO_URL = "https://script.google.com/macros/s/AKfycbzY1PYcR4EC_AUXE3zASDVd7UWySYdltrwg1IX1RqjbZFGccNxf2fiDo0-b5jnMLMVqLA/exec"

# Checkout do "Qual IA Usar?" (R$ 67). Vazio = o resultado do diagnóstico oferece a
# lista de espera pelo direct em vez de um botão de compra que não leva a lugar nenhum.
CHECKOUT_URL = "https://pay.cakto.com.br/3fxqxg5_1049811"
PRECO = "R$ 67"

# Checkout do upsell "Sua primeira semana pronta", vendido dentro da entrega (/mapa).
# O preço aqui é o líquido: R$ 197 do pacote menos os R$ 67 que a pessoa já pagou pelo
# mapa. Quem chega no /mapa é comprador, então o crédito vale sempre, e não só na
# primeira tela: escassez inventada é proibida no projeto.
# Vazio: a tela pós-compra e o CTA de ascensão não aparecem, e a entrega segue intacta.
CHECKOUT_UPSELL = "https://pay.cakto.com.br/j79id6y_1051180"

# Pixel do Meta das quatro LPs. É o mesmo nos quatro: um pixel só aprende junto,
# quatro pixels separados fragmentam o aprendizado e não somam. O que separa as
# variantes no Events Manager é a URL do evento e o content_name que vai em
# ViewContent e InitiateCheckout.
# Vazio: nada é injetado e nada quebra.
PIXEL_META = "827402089420392"

# Measurement ID do GA4 ("G-XXXXXXXXXX"). O pixel do Meta já mede a venda e o Web Analytics
# da Vercel já mede a visita: o que só o GA4 dá, sem pagar, é a quebra por UTM, que no plano
# Hobby da Vercel é recurso pago. É por isso que ele existe aqui, e não por completude.
# Vazio: nada é injetado, nenhum evento é disparado e nada quebra.
GA4_ID = ""

# ---------- variantes do teste seco de nome chiclete ----------
# Uma LP por nome, servida em pasta própria. Só o nome muda e o que ele
# obriga (título, marca, mecanismo, crença e a headline do diagnóstico).
# Layout, seções, perguntas, preço e oferta ficam 100% idênticos: se mais de
# uma variável mudar, o teste não diz qual delas ganhou.
#
# As variantes saem com noindex para não competirem com a raiz no Google.
VARIANTES = {
    # controle: o que já está no ar
    "": {
        "nome": "Qual IA Usar?",
        "marca": "qual ia abrir",
        "mecanismo": "Regra das 3 IAs",
        "titulo": "Qual IA Usar? A sua stack de IA em 2 minutos",
        "headline": "Descubra quais são as suas 3 IAs",
        "crenca": ("Escolher a IA certa para cada tarefa é a chave para a IA finalmente devolver "
                   "resposta útil, e isso é possível através da Regra das 3 IAs."),
        "checkout": CHECKOUT_URL,
    },
    "abas": {
        "nome": "Método das 3 Abas",
        "marca": "método das 3 abas",
        "mecanismo": "Método das 3 Abas",
        "titulo": "Método das 3 Abas: a sua stack de IA em 2 minutos",
        "headline": "Descubra quais são as suas 3 abas",
        "crenca": ("Deixar aberta a aba certa para cada tarefa é a chave para a IA finalmente "
                   "devolver resposta útil, e isso é possível através do Método das 3 Abas."),
        "checkout": "https://pay.cakto.com.br/32hjw7j_1049893",
    },
    "regra": {
        "nome": "Regra das 3 IAs",
        "marca": "regra das 3 IAs",
        "mecanismo": "Regra das 3 IAs",
        "titulo": "Regra das 3 IAs: a sua stack de IA em 2 minutos",
        "headline": "Descubra quais são as suas 3 IAs",
        "crenca": ("Escolher a IA certa para cada tarefa é a chave para a IA finalmente devolver "
                   "resposta útil, e isso é possível através da Regra das 3 IAs."),
        "checkout": "https://pay.cakto.com.br/8t2cigd_1049903",
    },
    "stack": {
        "nome": "Stack Mínima",
        "marca": "stack mínima",
        "mecanismo": "Stack Mínima",
        "titulo": "Stack Mínima: as 3 IAs que bastam para o seu trabalho",
        "headline": "Descubra a sua stack mínima",
        "crenca": ("Ficar só com as ferramentas que você de fato usa é a chave para a IA "
                   "finalmente devolver resposta útil, e isso é possível através da Stack Mínima."),
        "checkout": "https://pay.cakto.com.br/3dtj6z8_1049909",
    },
}
