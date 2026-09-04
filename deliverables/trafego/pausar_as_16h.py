#!/usr/bin/env python3
"""Acompanha a v2 até as 16h de 27/08 e pausa se não houver avanço.

Decisão do Alison em 27/08 de manhã: deixar rodar até as 16h, e se não der
avanço, pausar. Este script existe para essa decisão não depender do terminal
ficar aberto: ele roda destacado e executa a pausa sozinho no horário.

    export ACCESS_TOKEN=...            # ou: . ~/.nsm-meta/_shared.env
    nohup python3 pausar_as_16h.py >> monitor-27ago.log 2>&1 &
    python3 pausar_as_16h.py --dry-run   # mostra o que faria, sem pausar

O critério de avanço foi fixado ANTES de olhar o resultado, que é o que
impede a leitura das 16h de virar opinião. Vale qualquer um dos três:

  A. 4 ou mais aberturas de quiz acumuladas na rodada (3 novas). Com as ~1.000
     visitas que a rodada terá às 16h, 4 é o número que faz o teto do IC95%
     voltar acima de 1% e destravar o gate escrito no LEIA.txt. Uma ou duas
     aberturas novas não contam: 2/1000 dá [0,05%; 0,73%] e 3/1000 dá
     [0,10%; 0,88%], ou seja o gate continua disparado e a decisão é a mesma
  B. 1 ou mais InitiateCheckout vindo de anúncio, que nunca aconteceu
  C. 1 ou mais Purchase atribuído à campanha, idem

Se houver avanço o script NÃO pausa nada: ele sai e deixa o registro no log,
porque a decisão de continuar é do Alison, não do critério.

Conclusão de quiz só aparece na planilha, não no pixel, e por isso não entra
na conta aqui: para concluir é preciso abrir, então o ViewContent cobre o caso.
"""
import datetime
import json
import os
import sys
import time
import urllib.parse
import urllib.request

CAMPANHA = "120249034223980685"          # QIU | VENDAS | IMAGEM | CBO | 26-08 v2
LIMITE = datetime.datetime(2026, 8, 27, 16, 0)
INTERVALO = 1200                          # 20 min entre as medições
SECO = "--dry-run" in sys.argv

if "ACCESS_TOKEN" not in os.environ:
    caminho = os.path.expanduser("~/.nsm-meta/_shared.env")
    for linha in open(caminho):
        if "=" in linha and not linha.startswith("#"):
            chave, valor = linha.strip().split("=", 1)
            os.environ.setdefault(chave, valor.strip('"'))
TOKEN = os.environ["ACCESS_TOKEN"]


def registrar(texto):
    print(f"{datetime.datetime.now():%d/%m %H:%M}  {texto}", flush=True)


def medir():
    campos = {"time_range": json.dumps({"since": "2026-08-26", "until": "2026-08-27"}),
              "fields": "spend,impressions,inline_link_clicks,inline_link_click_ctr,actions",
              "access_token": TOKEN}
    url = f"https://graph.facebook.com/v21.0/{CAMPANHA}/insights?" + urllib.parse.urlencode(campos)
    with urllib.request.urlopen(url, timeout=30) as r:
        dados = json.load(r)["data"]
    if not dados:
        return None
    linha = dados[0]
    acoes = {a["action_type"]: int(a["value"]) for a in linha.get("actions", [])}
    return {"gasto": float(linha["spend"]),
            "impressoes": int(linha["impressions"]),
            "cliques": int(linha.get("inline_link_clicks", 0)),
            "ctr": float(linha.get("inline_link_click_ctr", 0)),
            "lpv": acoes.get("landing_page_view", 0),
            "aberturas": acoes.get("offsite_conversion.fb_pixel_view_content", 0),
            "checkouts": acoes.get("offsite_conversion.fb_pixel_initiate_checkout", 0),
            "compras": acoes.get("offsite_conversion.fb_pixel_purchase", 0)}


def pausar():
    if SECO:
        registrar("DRY-RUN: pausaria a campanha aqui")
        return
    dados = urllib.parse.urlencode({"status": "PAUSED", "access_token": TOKEN}).encode()
    pedido = urllib.request.Request(f"https://graph.facebook.com/v21.0/{CAMPANHA}", data=dados)
    with urllib.request.urlopen(pedido, timeout=30) as r:
        registrar(f"PAUSA EXECUTADA, resposta da Meta: {r.read().decode()}")


registrar(f"acompanhando ate {LIMITE:%d/%m %H:%M} (medicao a cada {INTERVALO // 60} min)"
          + (" [DRY-RUN]" if SECO else ""))

while True:
    agora = datetime.datetime.now()
    m = None
    try:
        m = medir()
    except Exception as erro:                       # rede oscila, uma falha não derruba o resto
        registrar(f"ERRO na medicao: {erro}")
    if m:
        taxa = 100 * m["aberturas"] / m["lpv"] if m["lpv"] else 0
        registrar(f"R$ {m['gasto']:7.2f} | {m['impressoes']:6} impr | {m['cliques']:4} cliq | "
                  f"CTR {m['ctr']:.2f}% | {m['lpv']:4} LPV | abertura {m['aberturas']} ({taxa:.2f}%) | "
                  f"checkout {m['checkouts']} | compra {m['compras']}")
        if m["aberturas"] >= 4 or m["checkouts"] >= 1 or m["compras"] >= 1:
            registrar("AVANCO: o criterio bateu. Campanha SEGUE NO AR, a decisao e do Alison.")
            sys.exit(0)
    if agora >= LIMITE:
        registrar("16h SEM AVANCO pelo criterio fixado. Pausando.")
        pausar()
        sys.exit(0)
    time.sleep(INTERVALO)
