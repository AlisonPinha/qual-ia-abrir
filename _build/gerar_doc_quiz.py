"""
Gera _docs/DIAGNOSTICO.md: o mapa do quiz, para ler antes de mexer.

Sai do dados.json, nunca da memória de quem escreve. Documento de quiz escrito à mão
desatualiza no primeiro ajuste de peso e passa a mentir, que é pior do que não existir.

Uso: python3 _build/gerar_doc_quiz.py
"""

import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BUILD = RAIZ / "_build"
SAIDA = RAIZ / "_docs" / "DIAGNOSTICO.md"

sys.path.insert(0, str(BUILD))
import questionario  # noqa: E402

d = json.loads((BUILD / "dados.json").read_text(encoding="utf-8"))
DG = d["diagnostico"]
P = DG["perguntas"]
_html, regras, total = questionario.montar(P, DG["aberta"])

pid_de = {p[0]: p for p in P}
areas = [t for t, _ in pid_de["area"][2]]


def vota(p):
    return any(pesos for _t, pesos in p[2])


def favorecidas(p):
    """Quem cada opção favorece, na ordem em que aparece."""
    linhas = []
    for texto, pesos in p[2]:
        if pesos:
            top = ", ".join(f"{n} +{v}" for n, v in sorted(pesos.items(), key=lambda x: -x[1]))
        else:
            top = "não vota"
        linhas.append(f"| {texto} | {top} |")
    return linhas


L = []
L.append("# O diagnóstico, por dentro\n")
L.append("**Gerado por `_build/gerar_doc_quiz.py` a partir do `dados.json`. Não editar à mão:")
L.append("rode o gerador depois de mexer no quiz.**\n")
L.append(f"São **{len(P)} passos no banco** e **{total} perguntas por pessoa** no caminho mais longo.")
L.append("Quem nunca usou IA responde menos, porque três perguntas dependem de já ter ferramenta.\n")

L.append("## O fluxo, na ordem\n")
L.append("| # | Passo | Tipo | Só aparece se |")
L.append("|---|---|---|---|")
for i, p in enumerate(P, 1):
    pid = p[0]
    if pid == "break_espelho":
        tipo = "espelho: repete as respostas antes do resultado"
    elif pid.startswith("break"):
        tipo = "break: conteúdo entre blocos"
    elif vota(p):
        tipo = "pergunta, **vota** no motor"
    else:
        tipo = "pergunta, não vota (implicação e espelho)"
    cond = regras.get(pid)
    if cond:
        partes = []
        for q, vals in cond.items():
            rot = [pid_de[q][2][v][0] for v in vals if v < len(pid_de[q][2])]
            partes.append(f"`{q}` = {' ou '.join(rot) if len(rot) < 4 else f'{len(rot)} opções'}")
        cond = " e ".join(partes)
    L.append(f"| {i} | `{pid}` | {tipo} | {cond or 'sempre'} |")

L.append("\n## As 10 trilhas\n")
L.append("Cada área tem 5 perguntas próprias. É o que faz a personalização ser real, e é a")
L.append("parte do quiz que mais muda a stack.\n")
for i, area in enumerate(areas):
    proprias = [p for p in P if regras.get(p[0], {}).get("area") == [i]]
    L.append(f"**{i}. {area}**")
    for p in proprias:
        L.append(f"- `{p[0]}` {p[1]}")
    L.append("")

L.append("## O tronco, igual para todo mundo\n")
L.append("| pid | Pergunta | Vota? |")
L.append("|---|---|---|")
for p in P:
    if p[0] in regras or p[0].startswith("break"):
        continue
    L.append(f"| `{p[0]}` | {p[1]} | {'sim' if vota(p) else 'não'} |")

L.append("\n## O que cada resposta faz com a stack\n")
L.append("Só as perguntas que votam. Peso alto manda: 7 é resposta dominante, 1 a 3 é reforço.\n")
for p in P:
    if not vota(p):
        continue
    L.append(f"### `{p[0]}` {p[1]}\n")
    L.append("| Resposta | Favorece |")
    L.append("|---|---|")
    L.extend(favorecidas(p))
    L.append("")

L.append("## As regras do motor, que valem depois dos pesos\n")
L.append("Estão em `_build/motor.js`, e é aqui que a maior parte das surpresas mora.\n")
teto = DG["teto"]
orc = [t for t, _ in pid_de["orcamento"][2]]
L.append("**Teto por orçamento.** A faixa declarada tira da mesa o que não cabe nela:\n")
L.append("| Orçamento | Aceita |")
L.append("|---|---|")
for i, t in enumerate(orc):
    v = teto[i]
    L.append(f"| {t} | {'só o que tem camada gratuita de verdade' if v < 0 else f'ferramenta de faixa até {v}'} |")
L.append("")
L.append(f"**Quantas entram já:** `cabem` = {DG['cabem']}, uma posição por faixa de orçamento.")
L.append(f"Quem responde \"{pid_de['estilo'][2][DG['foco'][1]][0]}\" recebe uma só na primeira camada.\n")
L.append(f"**No celular** saem {', '.join(DG['semCelular'])}, que não se opera pelo telefone.\n")
L.append("**A stack nunca volta com menos de três.** Se o filtro esvaziar o ranking, entra")
L.append("especialista antes de generalista, porque quem paga não paga para ouvir as quatro óbvias.\n")

L.append("## Onde mexer, por tipo de mudança\n")
L.append("| Quero | Mexo em |")
L.append("|---|---|")
L.append("| Trocar texto de pergunta ou opção | `_build/dados.json`, bloco `diagnostico.perguntas` |")
L.append("| Mudar o que uma resposta favorece | os pesos da opção, no mesmo bloco |")
L.append("| Criar pergunta de trilha | mesma lista, com `{\"area\": [n]}` no fim. **As 10 trilhas precisam ficar do mesmo tamanho**, ou o build para |")
L.append("| Criar pergunta condicional | mesmo formato, com a condição que não seja de área |")
L.append("| Mudar preço, custo ou camada gratuita | `diagnostico.acesso` |")
L.append("| Mudar regra de bolso, celular ou ordem | `_build/motor.js` mais as constantes em `diagnostico` |")
L.append("| Mudar o que o espelho repete | `diagnostico.espelho` |")
L.append("")
L.append("**Depois de qualquer mudança:** `node _build/testar_motor.mjs`, que pega peso apontando")
L.append("para ferramenta inexistente, trilha de tamanho errado e ferramenta que virou peso morto.")
L.append("E rode este gerador de novo, senão este documento passa a mentir.\n")

SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text("\n".join(L), encoding="utf-8")
print(f"{SAIDA.relative_to(RAIZ)}: {len(P)} passos, {total} perguntas por pessoa, {sum(1 for p in P if vota(p))} votam")
