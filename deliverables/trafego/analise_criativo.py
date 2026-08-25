#!/usr/bin/env python3
"""Leitura de criativo de vídeo no pago: hook, corpo, curva e custo por peça.

A skill meta-ads-analyzer lê estrutura (aprendizado, sobreposição, pacing) e é
cega para vídeo. Isto é a outra metade.

    . ~/.nsm-meta/_shared.env
    python3 analise_criativo.py act_828815582355498
    python3 analise_criativo.py act_828815582355498 --campanha 120249018613980685 --dias 7

O que cada número quer dizer:

  início quantos deram play, sobre impressões. Em feed com autoplay isso é
         quase 100% e não diz nada sozinho: é o denominador, não o resultado.
  hook   quem passou do primeiro quarto, sobre impressões. É o teste da
         primeira dobra, e é o número que julga a abertura.
  hold   ThruPlay (15s, ou o vídeo inteiro se for menor) sobre impressões.
  p25..  onde a audiência cai. A queda entre dois marcos diz em que trecho o
         vídeo perde, e o trecho é que se reescreve, não o vídeo todo.
  curva  video_play_curve_actions: retenção segundo a segundo, direto da Meta.
         É a mesma leitura da curva do Reel orgânico, e quase ninguém usa.

Atenção às duas métricas mortas: video_3_sec_watched_actions foi DESCONTINUADO
na v21 e devolve erro "not valid for fields param"; e
video_continuous_2_sec_watched_actions é aceito no fields mas volta VAZIO, o que
é pior, porque calcula hook 0% sem reclamar. Toda receita de hook rate que você
achar na internet usa uma dessas duas. O que a Meta preenche hoje é
video_play_actions, thruplay, p25/p50/p75/p95/p100 e avg_time.

CAC não sai daqui, e não sai da Meta: com checkout Cakto e Pix, o Purchase que
a Meta enxerga é só o que a CAPI manda. O CAC por peça é investimento dividido
por comprador, cruzando o utm_content com a planilha de vendas.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

CAMPOS = ("ad_name,spend,impressions,clicks,actions,cost_per_action_type,"
          "video_play_actions,video_continuous_2_sec_watched_actions,"
          "video_thruplay_watched_actions,video_avg_time_watched_actions,"
          "video_p25_watched_actions,video_p50_watched_actions,"
          "video_p75_watched_actions,video_p95_watched_actions,"
          "video_p100_watched_actions")
# a curva sai numa chamada só dela: pedida junto com o resto, a Meta a OMITE
# sem avisar, e o resultado parece "esse anúncio não tem curva"
CAMPO_CURVA = "ad_name,video_play_curve_actions"


def buscar(caminho, **params):
    params["access_token"] = os.environ["ACCESS_TOKEN"]
    url = f"https://graph.facebook.com/v21.0/{caminho}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(e.read().decode("utf-8"))


def n(registro, campo):
    """Insights devolve tudo como lista de ações, mesmo o que é um número só."""
    v = registro.get(campo)
    if isinstance(v, list) and v:
        return float(v[0].get("value", 0))
    return float(v or 0)


def barra(fracao, largura=22):
    cheio = round(fracao * largura)
    return "█" * cheio + "·" * (largura - cheio)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("conta")
    p.add_argument("--campanha")
    p.add_argument("--dias", type=int, default=90)
    a = p.parse_args()

    alvo = a.campanha or a.conta
    d = buscar(f"{alvo}/insights", level="ad", fields=CAMPOS, limit=100,
               date_preset=f"last_{a.dias}d" if a.dias in (7, 14, 30, 90) else "last_90d")
    curvas = {r["ad_name"]: r["video_play_curve_actions"][0]["value"]
              for r in buscar(f"{alvo}/insights", level="ad", fields=CAMPO_CURVA,
                              limit=100, date_preset=d.get("_preset", "last_90d")).get("data", [])
              if r.get("video_play_curve_actions")}
    linhas = [r for r in d.get("data", []) if n(r, "video_play_actions")]
    if not linhas:
        sys.exit("nenhum anúncio de vídeo com entrega no período")

    print(f"{'anúncio':<30}{'gasto':>9}{'impr':>8}{'início':>8}{'hook':>7}"
          f"{'hold':>7}{'p50':>7}{'p100':>7}{'médio':>7}  resultado")
    print("-" * 104)
    for r in sorted(linhas, key=lambda x: -float(x["spend"])):
        impr, plays = float(r["impressions"]), n(r, "video_play_actions")
        inicio = plays / impr if impr else 0
        dois_seg = n(r, "video_continuous_2_sec_watched_actions")
        hook = (dois_seg or n(r, "video_p25_watched_actions")) / impr if impr else 0
        hold = n(r, "video_thruplay_watched_actions") / impr if impr else 0
        p50 = n(r, "video_p50_watched_actions") / plays if plays else 0
        p100 = n(r, "video_p100_watched_actions") / plays if plays else 0
        acoes = {x["action_type"]: float(x["value"]) for x in r.get("actions", [])}
        custos = {x["action_type"]: float(x["value"]) for x in r.get("cost_per_action_type", [])}
        chave = next((k for k in ("purchase", "lead", "onsite_conversion.lead_grouped",
                                  "onsite_conversion.messaging_conversation_started_7d")
                      if k in acoes), None)
        res = f"{int(acoes[chave])} a R$ {custos.get(chave, 0):.0f}" if chave else "sem resultado"
        print(f"{r['ad_name'][:29]:<30}{float(r['spend']):>9.2f}{int(impr):>8}"
              f"{inicio:>8.0%}{hook:>7.0%}{hold:>7.0%}{p50:>7.0%}{p100:>7.0%}"
              f"{n(r, 'video_avg_time_watched_actions'):>6.0f}s  {res}")

    # o corpo do vídeo: onde a audiência sai, peça a peça
    print("\nONDE CADA UM PERDE (sobre quem deu play)")
    for r in sorted(linhas, key=lambda x: -float(x["spend"]))[:5]:
        plays = n(r, "video_play_actions")
        if not plays:
            continue
        print(f"\n  {r['ad_name'][:60]}")
        anterior = 1.0
        for marco in (25, 50, 75, 95, 100):
            frac = n(r, f"video_p{marco}_watched_actions") / plays
            queda = anterior - frac
            aviso = "  <- maior queda" if queda > 0.25 else ""
            print(f"    {marco:>3}%  {barra(frac)}  {frac:>4.0%}   perdeu {queda:>4.0%}{aviso}")
            anterior = frac

    # a curva vem só quando a Meta acumulou audiência suficiente
    if curvas:
        print("\nCURVA DE RETENÇÃO, SEGUNDO A SEGUNDO")
        for r in sorted(linhas, key=lambda x: -float(x["spend"]))[:3]:
            v = curvas.get(r["ad_name"])
            if not v:
                continue
            print(f"\n  {r['ad_name'][:60]}")
            for seg, val in enumerate(v):
                if seg % 2 == 0:
                    print(f"    {seg:>2}s  {barra(float(val) / 100)}  {float(val):>5.1f}%")
    else:
        print("\n(nenhuma peça acumulou audiência suficiente para a Meta devolver a curva)")


if __name__ == "__main__":
    main()
