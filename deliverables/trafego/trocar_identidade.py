#!/usr/bin/env python3
"""Troca a identidade dos anúncios já criados para o perfil do Instagram.

Os treze criativos subiram em 25/08 com a identidade da Página, porque o
@aalisonaraujo ainda não estava no business. Criativo não se edita: o jeito é
criar um novo e apontar o anúncio para ele.

    . ~/.nsm-meta/_shared.env
    python3 trocar_identidade.py --dry-run
    python3 trocar_identidade.py

Reaproveita a mídia que já está na conta (image_hash e video_id do criativo
antigo), então não sobe imagem nem vídeo de novo. O criativo antigo é apagado
depois que o anúncio já aponta para o novo, nunca antes.
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
IG_ACTOR = "17841400503107410"        # @aalisonaraujo
API = "https://graph.facebook.com/v21.0"


def graph(caminho, metodo="GET", **campos):
    campos["access_token"] = os.environ["ACCESS_TOKEN"]
    dados = urllib.parse.urlencode(campos).encode()
    req = (urllib.request.Request(f"{API}/{caminho}", dados) if metodo == "POST"
           else urllib.request.Request(f"{API}/{caminho}?{dados.decode()}",
                                       method=metodo))
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(f"falhou {metodo} /{caminho}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    ids = json.loads((AQUI / "ids-da-subida.json").read_text())
    trocados = {}
    for peca, anuncio in ids["anuncios"].items():
        atual = graph(anuncio, fields="name,creative{id,object_story_spec}")
        velho = atual["creative"]["id"]
        spec = atual["creative"]["object_story_spec"]
        if spec.get("instagram_user_id") == IG_ACTOR:
            print(f"   {peca:<14} já está no perfil, pulando")
            continue
        # o campo é instagram_user_id: em instagram_actor_id a API responde
        # "must be a valid Instagram account id", mesmo com o id certo
        spec["instagram_user_id"] = IG_ACTOR
        # a leitura devolve a miniatura em image_url E image_hash, e a escrita
        # aceita só um dos dois ("ObjectStorySpecRedundant")
        if "image_hash" in spec.get("video_data", {}):
            spec["video_data"].pop("image_url", None)
        if args.dry_run:
            print(f"   {peca:<14} criativo {velho} -> novo (dry-run)")
            continue
        novo = graph(f"act_828815582355498/adcreatives", "POST",
                     name=f"QIU | {peca}",
                     object_story_spec=json.dumps(spec))["id"]
        graph(anuncio, "POST", creative=json.dumps({"creative_id": novo}))
        graph(velho, "DELETE")          # só depois que o anúncio já aponta pro novo
        trocados[peca] = novo
        print(f"   {peca:<14} {velho} -> {novo}")

    if trocados and not args.dry_run:
        ids["criativos"] = {**ids.get("criativos", {}), **trocados}
        (AQUI / "ids-da-subida.json").write_text(
            json.dumps(ids, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n{len(trocados)} anúncios agora saem como @aalisonaraujo.")


if __name__ == "__main__":
    main()
