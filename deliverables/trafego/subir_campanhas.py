#!/usr/bin/env python3
"""Sobe a primeira rodada de criativos do Qual IA Usar no gerenciador.

Cria tudo PAUSADO, na conta CA - 001 - INFO, com o pixel do funil e o
utm_content de cada peça já no link. Nada entrega enquanto você não ligar.

    export ACCESS_TOKEN=...            # ou: . ~/.nsm-meta/_shared.env
    python3 subir_campanhas.py --dry-run     # mostra o que faria
    python3 subir_campanhas.py               # cria de verdade, pausado

Estrutura, que vem do playbook (ABO e CBO os dois, lateralizar por criativo,
conjuntos separados por família, nunca duplicar campanha à exaustão):

    QIU | VENDAS | IMAGEM | CBO      R$ 500   3 conjuntos, 10 anúncios
      A  imita conteúdo              A1 A4 A2 A3
      M  veste a marca               M4 M2-conteudo M1 M3
      M2 teste de público            M2-negocio M2-vendas
    QIU | VENDAS | VIDEO | ABO       criada, mas fora desta rodada
      V01 gráfico · V03 prompts · V06 advogados

Os vídeos saíram em 25/08 porque o playbook põe imagem para testar e vídeo para
escalar: o que converter aqui é que vira vídeo. A campanha deles ficou como
"[FASE 2, NAO LIGAR]" e o orçamento voltou para o CBO.

O bid cap que o playbook pede fica para a segunda rodada, de propósito: sem
CPA medido nesta conta, um teto chutado trava a entrega em vez de baratear o
leilão. Primeiro sai o CPA real, depois o teto.

Acessos, resolvidos por API em 25/08 (POST /{objeto}/assigned_users):
  o system user do app "Clickup - NSM" ganhou MANAGE na conta e na Página
  Alison Araujo. Sem os dois a API recusa, e o erro da Página só aparece na
  hora de criar o criativo, não antes.

O que continua fora do alcance da API, e é só seu:
  - saldo. A conta é pré-paga e está zerada. O spend_cap dela não é editável
    ("alteração inválida para uma conta pré-paga"): ele espelha o que já foi
    carregado, então quem levanta o teto é o saldo entrando, não um POST
  - vincular o @aalisonaraujo ao business. Reivindicar perfil exige o fluxo de
    login com confirmação do dono, que não existe em token de system user.
    Enquanto isso, os criativos ficam com a identidade da Página
"""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.error
import urllib.request

AQUI = pathlib.Path(__file__).parent
CONTA = "act_828815582355498"          # CA - 001 - INFO
PIXEL = "827402089420392"              # o que a LP dispara
PAGINA = "897860133421433"             # Alison Araujo
IG_ACTOR = "17841400503107410"         # @aalisonaraujo
LINK = ("https://diagnostico.noahai.com.br/?utm_source=ig&utm_medium=paid"
        "&utm_campaign=stack&utm_content={peca}")
INICIO = "2026-08-26T00:00:00-0300"
FIM = "2026-08-29T00:00:00-0300"       # 3 dias, que é o mínimo do playbook

# O fecho é o mesmo nas treze, palavra por palavra com o botão da LP (regra 121).
FECHO = ("O link tá aqui embaixo. Clica em descobrir a minha stack, responde o "
         "diagnóstico. Dois minutos.")

# Os três vídeos não estavam no COPY-DOS-ANUNCIOS.md, que só cobre as dez A e M.
COPY_VIDEO = {
    "V-GRAFICO": {
        "arquivo": "01 - Grafico adocao de IA.mp4",
        "body": (
            "Se você acha que está atrasado no mundo da IA, esse gráfico resolve "
            "isso em quarenta segundos.\n\n"
            "A maior parte do mundo nunca abriu uma IA na vida, e quem já paga por "
            "uma quase nunca usa metade do que ela faz. O atraso não é ter chegado "
            "depois, é abrir a errada para o que você precisa fazer.\n\n" + FECHO),
        "title": "Você não está atrasado em IA",
        "desc": "Diagnóstico de 2 minutos. R$ 67, pagamento único, 7 dias de garantia.",
    },
    "V-PROMPT": {
        "arquivo": "03 - Prompts melhores.mp4",
        "body": (
            "Não peça faz um texto. Peça três versões, tom direto.\n\n"
            "A forma como você pede muda a resposta que volta. E antes disso tem uma "
            "escolha que quase ninguém faz: qual IA abrir para aquela tarefa. As duas "
            "juntas são o que separa resposta genérica de resposta que serve.\n\n" + FECHO),
        "title": "Não é a IA. É como você pede.",
        "desc": "66 tarefas mapeadas, com o prompt de cada uma. R$ 67, pagamento único.",
    },
    "V-JUR": {
        "arquivo": "06 - IAs para advogados.mp4",
        "body": (
            "Dez tarefas de advogado, e a IA certa para cada uma.\n\n"
            "Petição, jurisprudência, revisão de contrato, cálculo trabalhista: são "
            "tarefas diferentes, e a ferramenta que resolve bem uma faz mal a outra. O "
            "diagnóstico separa as seis que comem a sua semana e devolve, para cada "
            "uma, qual usar e o prompt pronto para colar.\n\n" + FECHO),
        "title": "A IA certa para cada tarefa do escritório",
        "desc": "Diagnóstico de 2 minutos. R$ 67, pagamento único, 7 dias de garantia.",
    },
}

# peça -> qual entrada da copy ela usa (as três M2 dividem o mesmo texto)
CONJUNTOS_IMAGEM = [
    ("QIU | A | imita conteudo | BR", ["A1", "A4", "A2", "A3"]),
    ("QIU | M | veste a marca | BR", ["M4", "M2-conteudo", "M1", "M3"]),
    ("QIU | M2 | teste de publico | BR", ["M2-negocio", "M2-vendas"]),
]
CONJUNTOS_VIDEO = [
    ("QIU | V01 | grafico | BR", "V-GRAFICO", 6666),
    ("QIU | V03 | prompts | BR", "V-PROMPT", 6666),
    ("QIU | V06 | advogados | BR", "V-JUR", 6668),
]


def copy_das_imagens():
    """Lê o COPY-DOS-ANUNCIOS.md e devolve {peça: {body, title, desc}}."""
    texto = (AQUI / "COPY-DOS-ANUNCIOS.md").read_text(encoding="utf-8")
    saida = {}
    for bloco in texto.split("\n## ")[1:]:
        codigo = bloco.split(" ")[0].strip()
        if not re.fullmatch(r"[AM]\d", codigo):
            continue
        corpo = bloco.split("**Texto primário**", 1)[1].split("**Título:**", 1)[0]
        linhas = [l[2:].strip() for l in corpo.strip().splitlines() if l.startswith("> ")]
        # o markdown quebra o parágrafo em várias linhas; "> " sozinho separa
        paragrafos, atual = [], []
        for l in corpo.strip().splitlines():
            l = l.lstrip(">").strip()
            if l:
                atual.append(l)
            elif atual:
                paragrafos.append(" ".join(atual))
                atual = []
        if atual:
            paragrafos.append(" ".join(atual))
        saida[codigo] = {
            "body": "\n\n".join(paragrafos),
            "title": re.search(r"\*\*Título:\*\* (.+)", bloco).group(1).strip(),
            "desc": re.search(r"\*\*Descrição:\*\* (.+)", bloco).group(1).strip(),
        }
        assert linhas, codigo
    return saida


def meta(*args, dry=False):
    """Chama a CLI oficial e devolve o JSON da resposta.

    A CLI imprime uma linha de texto ("Created campaign ...") antes do JSON,
    então o parse começa no primeiro colchete, não no início da saída.
    """
    cmd = ["meta", "--no-input", "--output", "json", "ads", *[str(a) for a in args]]
    if dry:
        print("   $", " ".join(f'"{c}"' if " " in c else c for c in cmd))
        return {"id": "DRY"}
    r = subprocess.run(cmd, capture_output=True, text=True,
                       env={**os.environ, "AD_ACCOUNT_ID": CONTA})
    corte = min((i for i in (r.stdout.find("["), r.stdout.find("{")) if i >= 0),
                default=-1)
    if r.returncode or corte < 0:
        print(r.stdout or r.stderr, file=sys.stderr)
        sys.exit(f"falhou: {' '.join(str(a) for a in args[:3])}")
    dados = json.loads(r.stdout[corte:])
    return dados[0] if isinstance(dados, list) else dados


def graph(caminho, dry=False, **campos):
    """O que a CLI não expõe: estratégia de lance e criação de conjunto.

    Esta conta tem LOWEST_COST_WITH_BID_CAP como padrão, e ele desce para todo
    objeto novo. Na CBO dá para consertar na campanha antes de criar os
    conjuntos; na ABO a estratégia mora em cada conjunto, e editar depois não
    salva, porque a criação já falha pedindo bid_amount. Por isso o conjunto de
    vídeo nasce daqui, com a estratégia junto.
    """
    if dry:
        print(f"   $ POST /{caminho} {list(campos)}")
        return {"id": "DRY"}
    dados = urllib.parse.urlencode(
        {**campos, "access_token": os.environ["ACCESS_TOKEN"]}).encode()
    try:
        with urllib.request.urlopen(
                f"https://graph.facebook.com/v21.0/{caminho}", dados) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(f"falhou POST /{caminho}")


def criativo_video(peca, arquivo, dry=False):
    """Sobe o vídeo e monta o criativo na mão.

    A CLI não serve aqui: ela põe link_url dentro de video_data e a API recusa.
    Em vídeo o destino mora em call_to_action.value.link, e a miniatura tem que
    ser escolhida (a API não assume nenhuma sozinha).
    """
    c = COPY_VIDEO[peca]
    if dry:
        print(f"   $ POST /{CONTA}/advideos + /adcreatives  ({arquivo.name})")
        return "DRY"
    print(f"   subindo {arquivo.name}...")
    vid = json.loads(subprocess.run(
        ["curl", "-s", "-F", f"source=@{arquivo}", "-F",
         f"access_token={os.environ['ACCESS_TOKEN']}",
         f"https://graph.facebook.com/v21.0/{CONTA}/advideos"],
        capture_output=True, text=True).stdout)["id"]
    for _ in range(60):                       # o vídeo só aceita uso depois de processado
        with urllib.request.urlopen(
                f"https://graph.facebook.com/v21.0/{vid}?fields=status"
                f"&access_token={os.environ['ACCESS_TOKEN']}") as r:
            if json.load(r)["status"]["video_status"] == "ready":
                break
        time.sleep(5)
    else:
        sys.exit(f"o vídeo {vid} não terminou de processar")
    with urllib.request.urlopen(
            f"https://graph.facebook.com/v21.0/{vid}/thumbnails"
            f"?access_token={os.environ['ACCESS_TOKEN']}") as r:
        thumbs = json.load(r)["data"]
    capa = next((t for t in thumbs if t.get("is_preferred")), thumbs[0])["uri"]
    historia = {"page_id": PAGINA, "video_data": {
        "video_id": vid, "image_url": capa,
        "message": f"{c['body']}\n\n{c['desc']}", "title": c["title"],
        "call_to_action": {"type": "LEARN_MORE",
                           "value": {"link": LINK.format(peca=peca)}}}}
    if IG_ACTOR:
        historia["instagram_actor_id"] = IG_ACTOR
    return graph(f"{CONTA}/adcreatives", name=f"QIU | {peca}",
                 object_story_spec=json.dumps(historia))["id"]


def criar_conjunto(campanha, nome, orcamento=None, dry=False):
    """Conjunto sempre pela Graph API, nunca pela CLI.

    Três campos justificam isso: bid_strategy (a conta impõe teto de lance a
    todo objeto novo), destination_type (nasce UNDEFINED e a otimização é para
    site) e attribution_spec, que é IMUTÁVEL depois da criação ("não é possível
    atualizar a janela de atribuição, você deve criar um novo conjunto").
    """
    campos = dict(
        campaign_id=campanha, name=nome,
        optimization_goal="OFFSITE_CONVERSIONS", billing_event="IMPRESSIONS",
        bid_strategy="LOWEST_COST_WITHOUT_CAP", destination_type="WEBSITE",
        promoted_object=json.dumps(
            {"pixel_id": PIXEL, "custom_event_type": "PURCHASE"}),
        attribution_spec=json.dumps([
            {"event_type": "CLICK_THROUGH", "window_days": 7},
            {"event_type": "VIEW_THROUGH", "window_days": 1}]),
        targeting=json.dumps({"geo_locations": {"countries": ["BR"]}}),
        start_time=INICIO, end_time=FIM, status="PAUSED")
    if orcamento:
        campos["lifetime_budget"] = orcamento
    return graph(f"{CONTA}/adsets", dry=dry, **campos)["id"]


def conjuntos_existentes(campanha):
    """Nome -> id do que já está na campanha, para uma retomada não duplicar."""
    url = (f"https://graph.facebook.com/v21.0/{campanha}/adsets?fields=name"
           f"&limit=50&access_token={os.environ['ACCESS_TOKEN']}")
    with urllib.request.urlopen(url) as r:
        return {a["name"]: a["id"] for a in json.load(r).get("data", [])}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--so-video", metavar="CAMPANHA_ID",
                   help="pula a parte de imagem e usa esta campanha para os vídeos")
    args = p.parse_args()
    dry = args.dry_run

    copy = copy_das_imagens()
    copy["M2-conteudo"] = copy["M2-negocio"] = copy["M2-vendas"] = copy["M2"]
    feito = {"campanhas": {}, "conjuntos": {}, "anuncios": {}}

    def criativo(peca, arquivo, midia):
        # video_data não aceita description: nos três vídeos o preço vai no fim
        # do texto primário, que é o único campo que sobra para ele
        imagem = midia == "--image"
        c = copy[peca] if imagem else COPY_VIDEO[peca]
        corpo = c["body"] if imagem else f"{c['body']}\n\n{c['desc']}"
        extra = ["--instagram-actor-id", IG_ACTOR] if IG_ACTOR else []
        extra += ["--description", c["desc"]] if imagem else []
        return meta("creative", "create", "--name", f"QIU | {peca}",
                    midia, str(arquivo), "--page-id", PAGINA,
                    "--body", corpo, "--title", c["title"],
                    "--link-url", LINK.format(peca=peca),
                    "--call-to-action", "learn_more", *extra, dry=dry)["id"]

    if (AQUI / "ids-da-subida.json").exists():
        feito.update(json.loads((AQUI / "ids-da-subida.json").read_text()))

    if not args.so_video:
        print("CAMPANHA 1 · imagem, CBO, R$ 300")
        c1 = meta("campaign", "create", "--name", "QIU | VENDAS | IMAGEM | CBO | 26-08",
                  "--objective", "outcome_sales", "--lifetime-budget", 30000,
                  "--status", "paused", dry=dry)["id"]
        graph(c1, bid_strategy="LOWEST_COST_WITHOUT_CAP", dry=dry)
        feito["campanhas"]["imagem"] = c1
        for nome, pecas in CONJUNTOS_IMAGEM:
            s = criar_conjunto(c1, nome, dry=dry)
            feito["conjuntos"][nome] = s
            for peca in pecas:
                cid = criativo(peca, AQUI / f"{peca}.png", "--image")
                a = meta("ad", "create", s, "--name", f"QIU | {peca}",
                         "--creative-id", cid, "--pixel-id", PIXEL,
                         "--status", "paused", dry=dry)["id"]
                feito["anuncios"][peca] = a
                print(f"   {peca:<14} criativo {cid}  anúncio {a}")

    print("CAMPANHA 2 · vídeo, ABO, R$ 200")
    c2 = args.so_video or meta(
        "campaign", "create", "--name", "QIU | VENDAS | VIDEO | ABO | 26-08",
        "--objective", "outcome_sales", "--status", "paused", dry=dry)["id"]
    feito["campanhas"]["video"] = c2
    ja_existe = {} if dry else conjuntos_existentes(c2)
    for nome, peca, orcamento in CONJUNTOS_VIDEO:
        s = ja_existe.get(nome) or criar_conjunto(c2, nome, orcamento, dry)
        feito["conjuntos"][nome] = s
        cid = criativo_video(peca, AQUI / COPY_VIDEO[peca]["arquivo"], dry)
        a = meta("ad", "create", s, "--name", f"QIU | {peca}",
                 "--creative-id", cid, "--pixel-id", PIXEL,
                 "--status", "paused", dry=dry)["id"]
        feito["anuncios"][peca] = a
        print(f"   {peca:<14} criativo {cid}  anúncio {a}")

    if not dry:
        (AQUI / "ids-da-subida.json").write_text(
            json.dumps(feito, indent=2, ensure_ascii=False), encoding="utf-8")
        print("\nids em ids-da-subida.json. Tudo pausado.")


if __name__ == "__main__":
    if not IG_ACTOR:
        print("aviso: IG_ACTOR vazio, os anúncios sobem com a identidade da Página.\n"
              "       vincule o @aalisonaraujo e preencha antes de rodar valendo.\n")
    main()
