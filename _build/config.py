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
