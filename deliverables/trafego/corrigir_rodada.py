#!/usr/bin/env python3
"""Refaz a rodada de imagem com a otimização que entrega, e pausa a antiga.

A rodada de 26/08 subiu otimizando PURCHASE num pixel com 7 compras em 28 dias.
Em 11h30 no ar isso deu 84 impressões, zero clique e CPM de R$ 159,76: sem
exemplo de comprador a probabilidade estimada fica perto de zero, o lance
efetivo desaba e o anúncio perde todo leilão bom. O que sobra é inventário
residual, e o CPM alto é o sintoma disso, não a doença.

    export ACCESS_TOKEN=...            # ou: . ~/.nsm-meta/_shared.env
    python3 corrigir_rodada.py --dry-run     # mostra o que faria
    python3 corrigir_rodada.py               # cria de verdade, ATIVO

Por que campanha nova, e não um POST na antiga: em CBO com custo mais baixo a
Meta exige o mesmo optimization_goal nos três conjuntos e valida objeto por
objeto, então nenhuma ordem de edição passa, nem pausada nem em batch. Zerar o
orçamento para virar ABO também é recusado ("orçamento muito baixo"). A
otimização é imutável depois de criada, e a saída é nascer certo.

O que muda em relação à antiga, e só isso:
  - LANDING_PAGE_VIEWS no lugar de OFFSITE_CONVERSIONS/PURCHASE. Esta rodada
    testa dez criativos: o que ela precisa é volume de visita para separar
    CTR e CPC. Quem converteu sai da planilha por utm_content, que é como o
    LEIA.txt já definiu a leitura. Otimização por compra volta na escala,
    quando houver InitiateCheckout acumulado
  - posicionamento automático no lugar de facebook:feed + instagram:stream.
    O corte tirava Reels, Stories e Explore, que é justo o inventário barato
  - diário no lugar de vitalício. O vitalício de 3 dias com pacing standard
    segura verba no começo da janela, e já se perdeu meio dia

O resto é igual de propósito: mesmo público (BR, 18-65, advantage_audience),
mesmos criativos (reaproveitados por creative_id, então nada de subir imagem
de novo) e mesmo utm_content por peça, para a planilha continuar comparável.

O A3 fica de fora: já estava marcado "[FORA DA RODADA, NAO LIGAR]".

O orçamento respeita o saldo, não o desejo: a conta é pré-paga e a folga do
spend_cap é o teto real. Ver reference_meta_api_armadilhas_criacao, item 7.
"""
import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

AQUI = pathlib.Path(__file__).parent
CONTA = "act_828815582355498"          # CA - 001 - INFO
PIXEL = "827402089420392"              # o que a LP dispara
ANTIGA = "120249018613980685"          # QIU | VENDAS | IMAGEM | CBO | 26-08
FIM = "2026-08-29T00:00:00-0300"       # mesma janela da rodada original
DIARIO = 15000                         # R$ 150,00 por dia, em centavos

# Os conjuntos da rodada, com os anúncios que cada um leva. O creative_id vem
# de GET /{adset_id}/ads, nunca do ids-da-subida.json: aquele arquivo já
# envelheceu uma vez (o A1 mudou de criativo quando o conjunto foi refeito).
RODADA = [
    ("QIU | M2 | teste de publico | BR", "120249019554480685"),
    ("QIU | M | veste a marca | BR",      "120249019558720685"),
    ("QIU | A | imita conteudo | BR",     "120249019560960685"),
]
FORA = "A3"                            # marcado como fora da rodada na subida


def api(caminho, campos=None, metodo="GET", dry=False):
    """Chama a Graph API. GET sem campos, POST com eles."""
    token = os.environ["ACCESS_TOKEN"]
    if metodo == "GET":
        url = (f"https://graph.facebook.com/v21.0/{caminho}?"
               + urllib.parse.urlencode({**(campos or {}), "access_token": token}))
        with urllib.request.urlopen(url) as r:
            return json.load(r)
    if dry:
        print(f"   $ POST /{caminho} {sorted(campos)}")
        return {"id": "DRY"}
    dados = urllib.parse.urlencode({**campos, "access_token": token}).encode()
    try:
        with urllib.request.urlopen(
                f"https://graph.facebook.com/v21.0/{caminho}", dados) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(f"falhou POST /{caminho}")


def folga_de_saldo():
    """Quanto ainda cabe gastar antes do spend_cap, em reais.

    Conta pré-paga: o spend_cap espelha o saldo carregado e não é editável.
    Passar dele não dá erro na criação, dá anúncio parado no meio da janela.
    """
    c = api(CONTA, {"fields": "spend_cap,amount_spent"})
    return (int(c["spend_cap"]) - int(c["amount_spent"])) / 100


def anuncios_vivos(adset):
    """Lê os anúncios do conjunto direto da API, com o criativo de cada um."""
    r = api(f"{adset}/ads", {"fields": "name,effective_status,creative{id}",
                             "limit": "50"})
    return [a for a in r.get("data", []) if FORA not in a["name"]]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    dry = args.dry_run

    folga = folga_de_saldo()
    print(f"folga de saldo: R$ {folga:.2f}  (diário pedido: R$ {DIARIO/100:.2f})")
    if folga < DIARIO / 100:
        sys.exit("saldo não cobre nem um dia: carregue a conta antes")

    print("\n1. pausando a rodada antiga")
    api(ANTIGA, {"status": "PAUSED"}, "POST", dry)

    print("\n2. campanha nova")
    camp = api(f"{CONTA}/campaigns", {
        "name": "QIU | VENDAS | IMAGEM | CBO | 26-08 v2",
        "objective": "OUTCOME_SALES",
        "special_ad_categories": "[]",
        "daily_budget": str(DIARIO),
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "status": "ACTIVE",
    }, "POST", dry)["id"]
    print(f"   {camp}")

    ids = {"campanha": camp, "conjuntos": {}, "anuncios": {}}
    for nome, antigo in RODADA:
        print(f"\n3. conjunto {nome}")
        # O targeting sai do conjunto antigo e só perde o recorte de
        # posicionamento: tudo o mais (geo, idade, advantage_audience)
        # continua igual, senão a rodada deixa de ser comparável.
        alvo = api(antigo, {"fields": "targeting"})["targeting"]
        for k in ("publisher_platforms", "facebook_positions",
                  "instagram_positions", "device_platforms"):
            alvo.pop(k, None)
        novo = api(f"{CONTA}/adsets", {
            "name": nome,
            "campaign_id": camp,
            "optimization_goal": "LANDING_PAGE_VIEWS",
            "billing_event": "IMPRESSIONS",
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
            "destination_type": "WEBSITE",
            "promoted_object": json.dumps({"pixel_id": PIXEL,
                                           "custom_event_type": "CONTENT_VIEW"}),
            "targeting": json.dumps(alvo),
            "end_time": FIM,
            "status": "ACTIVE",
        }, "POST", dry)["id"]
        ids["conjuntos"][nome] = novo
        print(f"   {novo}")

        for a in anuncios_vivos(antigo):
            peca = a["name"].replace("QIU | ", "").strip()
            novo_ad = api(f"{CONTA}/ads", {
                "name": a["name"],
                "adset_id": novo,
                "creative": json.dumps({"creative_id": a["creative"]["id"]}),
                "status": "ACTIVE",
            }, "POST", dry)["id"]
            ids["anuncios"][peca] = novo_ad
            print(f"   - {peca:<14} {novo_ad}")

    if not dry:
        destino = AQUI / "ids-da-correcao.json"
        destino.write_text(json.dumps(ids, indent=2, ensure_ascii=False) + "\n")
        print(f"\nids em {destino.name}")


if __name__ == "__main__":
    main()
