#!/usr/bin/env python3
"""Põe o preço no texto primário das nove peças de imagem que vão rodar.

O preço morava só na descrição, e a descrição não aparece no feed do Instagram
nem no feed do Facebook em celular. O texto primário é o único campo que os dois
posicionamentos da rodada mostram, então é lá que o preço passa a morar. A frase
entra ANTES do fecho, para o CTA continuar sendo a última linha (regra 121).

    . ~/.nsm-meta/_shared.env
    python3 preco_no_texto.py --dry-run
    python3 preco_no_texto.py

Criativo não se edita: cria um novo com a mesma mídia, a mesma identidade e a
mesma UTM, aponta o anúncio para ele e só então apaga o velho. Mesmo padrão do
trocar_identidade.py. A A3 fica de fora: ela saiu da rodada.
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
CONTA = "act_828815582355498"
API = "https://graph.facebook.com/v21.0"
PRECO = "São R$ 67, pagamento único, com 7 dias de garantia."
FECHO = "O link tá aqui embaixo."
FORA = {"A3"}                          # saiu da rodada, não vale recriar

CORPO_M2 = """Cada uma delas tem uma IA que resolve melhor que as outras. O diagnóstico diz qual \
usar em cada uma e entrega o prompt escrito para a sua área."""

# as três M2 subiram com a instrução do documento colada no lugar da copy: o texto
# trazia o "(trocar só a primeira linha por área)" e as três áreas juntas, o que
# apagava justamente o que o conjunto 3 existe para comparar. Aqui elas nascem de novo.
REESCRITAS = {
    "M2-conteudo": "Seis tarefas comem a sua semana de conteúdo: roteiro, vídeo, imagem, "
                   "pauta, leitura de resultado e direct.",
    "M2-negocio": "Seis tarefas comem o seu dia: proposta, número, mercado, processo, "
                  "reunião e o sistema que ninguém cuida.",
    "M2-vendas": "Sua venda trava em seis pontos: qualificar, abordar, objeção, "
                 "follow-up, memória e o cliente que sumiu.",
}


def graph(caminho, metodo="GET", tolerante=False, **campos):
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
        if tolerante:
            return None
        sys.exit(f"falhou {metodo} /{caminho}")


def com_preco(texto):
    """Insere o preço como parágrafo próprio, logo antes do fecho."""
    if PRECO in texto:
        return None
    corte = texto.find(FECHO)
    if corte == -1:
        return f"{texto.rstrip()}\n\n{PRECO}"
    return f"{texto[:corte].rstrip()}\n\n{PRECO}\n\n{texto[corte:]}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    ids = json.loads((AQUI / "ids-da-subida.json").read_text())
    trocados = {}
    for peca, anuncio in ids["anuncios"].items():
        if peca in FORA or peca.startswith("V-"):
            print(f"   {peca:<14} fora da rodada, pulando")
            continue
        spec = graph(anuncio, fields="creative{object_story_spec}"
                     )["creative"]["object_story_spec"]
        dados = spec.get("link_data")
        if not dados:
            print(f"   {peca:<14} não é peça de link, pulando")
            continue
        if peca in REESCRITAS:
            texto = (f"{REESCRITAS[peca]}\n\n{CORPO_M2}\n\n"
                     f"{FECHO} Clica em descobrir a minha stack, responde o "
                     f"diagnóstico. Dois minutos.")
        else:
            texto = dados.get("message", "")
        novo_texto = com_preco(texto)
        if novo_texto is None:
            print(f"   {peca:<14} já tem o preço no texto, pulando")
            continue
        dados["message"] = novo_texto
        # a leitura devolve a mesma imagem em picture E image_hash, e a escrita
        # aceita só um dos dois ("ObjectStorySpecRedundant")
        if "image_hash" in dados:
            dados.pop("picture", None)
        if args.dry_run:
            print(f"   {peca:<14} texto novo:\n{novo_texto}\n")
            continue
        velho = graph(anuncio, fields="creative{id}")["creative"]["id"]
        novo = graph(f"{CONTA}/adcreatives", "POST",
                     name=f"QIU | {peca} | preco",
                     object_story_spec=json.dumps(spec))["id"]
        graph(anuncio, "POST", creative=json.dumps({"creative_id": novo}))
        trocados[peca] = novo
        print(f"   {peca:<14} {velho} -> {novo}")

    if trocados and not args.dry_run:
        ids["criativos"] = {**ids.get("criativos", {}), **trocados}
        (AQUI / "ids-da-subida.json").write_text(
            json.dumps(ids, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n{len(trocados)} peças agora dizem o preço no texto primário.")


if __name__ == "__main__":
    main()
