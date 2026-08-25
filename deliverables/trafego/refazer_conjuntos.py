#!/usr/bin/env python3
"""Refaz os três conjuntos de imagem com o que não dá para editar depois.

Dois campos justificam recriar em vez de editar:

  attribution_spec  IMUTÁVEL. Nasceram só com 7 dias de clique; o padrão da
                    Meta é 7 dias de clique mais 1 de visualização, e mais
                    sinal de conversão importa quando o volume é baixo.
  posicionamento    as dez peças são 1080x1350, desenhadas como post de feed
                    ("proporção 4:5 de post de feed, não formato de anúncio",
                    CRIATIVOS.md). Em Stories e Reels a Meta corta ou põe
                    barra, e as peças A deixam de parecer print de post.

Os treze criativos NÃO são recriados: eles já têm a identidade do
@aalisonaraujo e o utm_content, e criativo se reaproveita entre conjuntos.

    . ~/.nsm-meta/_shared.env
    python3 refazer_conjuntos.py --dry-run
    python3 refazer_conjuntos.py
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

CONTA = "act_828815582355498"
CAMPANHA = "120249018613980685"
PIXEL = "827402089420392"
INICIO, FIM = "2026-08-26T00:00:00-0300", "2026-08-29T00:00:00-0300"
API = "https://graph.facebook.com/v21.0"

POSICIONAMENTO = {
    "publisher_platforms": ["facebook", "instagram"],
    "facebook_positions": ["feed"],
    "instagram_positions": ["stream"],
}


def graph(caminho, metodo="GET", **campos):
    campos["access_token"] = os.environ["ACCESS_TOKEN"]
    dados = urllib.parse.urlencode(campos).encode()
    req = (urllib.request.Request(f"{API}/{caminho}", dados) if metodo == "POST"
           else urllib.request.Request(f"{API}/{caminho}?{dados.decode()}", method=metodo))
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(f"falhou {metodo} /{caminho}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    dry = p.parse_args().dry_run

    antigos = graph(f"{CAMPANHA}/adsets", fields="name")["data"]
    mapa = {}
    for s in antigos:
        ads = graph(f"{s['id']}/ads", fields="name,creative{id}")["data"]
        mapa[s["name"]] = [(a["name"], a["creative"]["id"]) for a in ads]
        print(f"  {s['name']:<34} {len(ads)} anúncios, criativos preservados")

    if dry:
        print("\n(dry-run: nada foi criado nem apagado)")
        return

    novos = []
    for nome, ads in mapa.items():
        s = graph(f"{CONTA}/adsets", "POST",
                  campaign_id=CAMPANHA, name=nome,
                  optimization_goal="OFFSITE_CONVERSIONS",
                  billing_event="IMPRESSIONS",
                  bid_strategy="LOWEST_COST_WITHOUT_CAP",
                  destination_type="WEBSITE",
                  promoted_object=json.dumps(
                      {"pixel_id": PIXEL, "custom_event_type": "PURCHASE"}),
                  attribution_spec=json.dumps([
                      {"event_type": "CLICK_THROUGH", "window_days": 7},
                      {"event_type": "VIEW_THROUGH", "window_days": 1}]),
                  targeting=json.dumps(
                      {"geo_locations": {"countries": ["BR"]}, **POSICIONAMENTO}),
                  start_time=INICIO, end_time=FIM, status="PAUSED")["id"]
        for nome_ad, criativo in ads:
            graph(f"{CONTA}/ads", "POST", adset_id=s, name=nome_ad,
                  creative=json.dumps({"creative_id": criativo}),
                  status="PAUSED")
        novos.append((nome, s))
        print(f"  {nome:<34} recriado como {s}")

    # só apaga o antigo depois que o novo existe inteiro
    for s in antigos:
        graph(s["id"], "DELETE")
        print(f"  antigo {s['id']} apagado")

    caminho = os.path.join(os.path.dirname(__file__), "ids-da-subida.json")
    ids = json.load(open(caminho))
    ids["conjuntos"] = {**{n: i for n, i in novos},
                        **{k: v for k, v in ids["conjuntos"].items() if "V0" in k}}
    json.dump(ids, open(caminho, "w"), indent=2, ensure_ascii=False)
    print(f"\n{len(novos)} conjuntos refeitos, pausados.")


if __name__ == "__main__":
    main()
