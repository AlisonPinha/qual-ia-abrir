"""
Os passos do diagnóstico em HTML, e as regras de trilha que o navegador precisa.

Existe para o site e a entrega paga nunca perguntarem coisas diferentes: os dois
geradores chamam `montar()` e recebem o mesmo HTML e as mesmas regras, do mesmo
jeito que os dois injetam o mesmo motor.js.

Uma pergunta pode ter um quarto item, a regra que a liga:

    ["c_tarefa", "Na sua semana de conteúdo...", [...], {"area": [0]}]

Sem esse item, a pergunta é do tronco e vale para todo mundo. Com ele, é de
trilha: só aparece para quem respondeu aquela área.
"""

from collections import Counter
from html import escape
import json


def montar(perguntas, aberta=None):
    """Devolve (html dos passos, regras por pid, total de perguntas de uma pessoa).

    `aberta` é {pid: rótulo}: nesses passos, a última opção é a saída de quem não se vê
    em nenhuma das outras. Ela abre um campo de texto em vez de avançar, para o quiz não
    forçar ninguém a mentir sobre o próprio trabalho e não perder quem não se encaixou.
    """
    html = []
    aberta = aberta or {}
    regras = {p[0]: p[3] for p in perguntas if len(p) > 3}

    for i, pergunta in enumerate(perguntas, start=1):
        pid, titulo, opcoes = pergunta[0], pergunta[1], pergunta[2]
        botoes = "".join(
            f'<button type="button" class="opc" data-q="{escape(pid, quote=True)}" data-i="{j}">'
            f'{escape(texto)}</button>'
            for j, (texto, _pesos) in enumerate(opcoes)
        )
        if pid.startswith("break"):
            manchete, _, corpo = titulo.partition(" | ")
            html.append(
                f'<fieldset class="passo passo-break" data-passo="{i}" data-q="{escape(pid, quote=True)}">'
                f'<legend>{escape(manchete)}</legend>'
                f'<p class="break-corpo">{escape(corpo)}</p>'
                f'<div class="opcoes">{botoes}</div></fieldset>'
            )
            continue
        campo = ""
        if pid in aberta:
            campo = (
                f'<div class="campo-aberto" hidden>'
                f'<label for="livre-{escape(pid, quote=True)}">{escape(aberta[pid])}</label>'
                f'<input id="livre-{escape(pid, quote=True)}" type="text" maxlength="120"'
                f' autocomplete="off" placeholder="Escreve com as suas palavras">'
                f'<button type="button" class="btn-livre">Continuar →</button></div>'
            )
        # o "n de m" sai vazio de propósito: com trilha, a posição da pergunta só
        # é conhecida depois da resposta de área. Quem preenche é o JS.
        html.append(
            f'<fieldset class="passo" data-passo="{i}" data-q="{escape(pid, quote=True)}">'
            f'<legend><span class="num"></span>{escape(titulo)}</legend>'
            f'<div class="opcoes">{botoes}</div>{campo}</fieldset>'
        )

    return "".join(html), regras, total(perguntas)


def total(perguntas):
    """Quantas perguntas uma pessoa responde: o tronco mais uma trilha.

    Exige que todas as trilhas tenham o mesmo tamanho. Se uma tiver três perguntas
    e outra duas, o contador "n de m" mentiria para metade das pessoas, e mentir no
    contador é o tipo de detalhe que faz abandonar o quiz na metade.
    """
    tronco = sum(1 for p in perguntas if len(p) == 3 and not p[0].startswith("break"))
    trilhas = Counter(json.dumps(p[3], sort_keys=True) for p in perguntas if len(p) > 3)
    if len(set(trilhas.values())) > 1:
        raise SystemExit(f"trilhas de tamanhos diferentes: {dict(trilhas)}")
    return tronco + (max(trilhas.values()) if trilhas else 0)
