# Os 6 Reels que viram criativo trocando só o CTA

Medido em 23/08/2026 a partir dos links que o Alison mandou. Os arquivos e as transcrições
ficaram em `_private/reels-cta/`. É a aplicação do caso que o playbook traz na seção Criativo:
vídeo que já viralizou, CTA trocado, melhor criativo da oferta inteira.

**Os seis têm a mesma frase de CTA**, palavra por palavra:

> "E pra aprender a IA mais rápido, me segue aqui, que todo dia tem conteúdo."

**E os seis têm o mesmo figurino no ponto de corte**, conferido em mosaico de frames: moletom
creme com capuz, óculos de armação redonda preta, mural de onda, mesmo enquadramento e mesma
luz. **Por isso um único take novo substitui o CTA dos seis**, e não seis takes.

| Reel | Data | Curtidas | Nicho | Total | CTA entra | Dura | Cita ferramenta paga |
|---|---|---|---|---|---|---|---|
| `Db37tHWCLMV` | 10/08 | **1.696** | geral | 22,57s | 19,61s | 2,96s | 🔴 Higgsfield |
| `DcPQ-X0gLBq` | 19/08 | **656** | jurídico | 31,21s | 28,30s | 2,91s | ✅ nenhuma |
| `DcFQw6PjM2J` | 16/08 | 173 | geral | 27,14s | 24,12s | 3,02s | 🔴 Grok |
| `DcLuQvwSZ7j` | 18/08 | 31 | contábil | 33,11s | 30,28s | 2,83s | ✅ nenhuma |
| `DcSBxcaDDrL` | 21/08 | 26 | saúde | 34,77s | 31,97s | 2,80s | 🔴 Gemini Notebook |
| `DcUnIodjCOr` | 22/08 | 12 | psicologia | 28,87s | 26,07s | 2,80s | 🔴 Higgsfield |

O `Db37tHWCLMV` bate com a medição independente feita na `timeline.ts` do
`reels-ferramentas-ia` (frame 591 de 676, a 30fps, dá 19,70s), o que confirma o método.

## O conflito com a regra do paywall, e ele é real

A constante das 18 peças diz que **só ChatGPT, Claude, Gemini e Perplexity** podem ser
citados, porque as outras oito do catálogo são o que a pessoa compra. **Quatro dos seis
furam essa regra.**

O tamanho do vazamento, medido e não estimado: cada Reel liga **uma** ferramenta a **uma**
tarefa. O produto entrega 23 tarefas cruzadas com 12 ferramentas, mais o prompt de cada uma e
a ordem de assinar. Uma linha não é o catálogo, mas é a regra que existe, e quem decide se
ela cede é o Alison.

**Os dois limpos sobem sem discussão**, e por sorte são justamente de nicho: jurídico e
contábil, duas das dez áreas do diagnóstico ramificado. Cada um pode apontar para a trilha
da própria área, o que é segmentação de campanha pronta sem gravar nada.

## O que grava

**Um take**, com o figurino acima, dizendo o fecho de anúncio:

> "O link tá aqui embaixo. Clica em descobrir a minha stack, responde o diagnóstico. Dois minutos."

**A peça quase não cresce, e o "uns 4s" que estava escrito aqui era chute.** O bloco antigo tem
15 palavras em 2,82s, ou seja, **5,3 palavras por segundo** (o ritmo dele, já com o 1,10x). O fecho
de anúncio tem 16 palavras: no mesmo ritmo dá 3,0s de fala, e com as duas pausas entre as três
frases, cerca de **3,6s**. Cada peça cresce **menos de um segundo**, não quatro. Todas seguem
dentro da régua de 20 a 45 segundos. Refeito em 24/08 a partir do `fim_Db37tHWCLMV.srt`; é
projeção pelo ritmo medido, não medição da fala nova, que ainda não existe.

---

## Onde está cada arquivo, medido em 24/08/2026

**Os `.mp4` desta pasta são download do Instagram, ~1,5 Mbps.** Servem para conferir métrica,
legenda e ponto de corte, nunca para editar: o master tem de 19 a 29 Mbps, e a perda aparece no
tecido do moletom e no halo do texto queimado.

**O master de cada um** (o mapeamento saiu de comparar frame a frame o miolo e o bloco de CTA,
não de adivinhar por data):

| Reel | Nicho na tela | Master | Duração | Bitrate |
|---|---|---|---|---|
| `Db37tHWCLMV` | 11 tarefas, geral | `~/Desktop/Rells para editar /Rells 03/Reel 03 - FINAL.mp4` | 22,60s | 18,9 Mbps |
| `DcLuQvwSZ7j` | 10 tarefas de **contador** | `.../Rells 5/Reel 05 - FINAL.mp4` | 33,44s | 29,5 Mbps |
| `DcPQ-X0gLBq` | 10 tarefas de **advogado** | `.../Rells 6/Reel 06 - FINAL.mp4` | 31,78s | 19,9 Mbps |
| `DcUnIodjCOr` | 10 tarefas de **psicólogo** | `.../Rells 7/Reel 07 - FINAL.mp4` | 29,47s | 20,0 Mbps |
| `DcSBxcaDDrL` | 10 tarefas de **médico** | `.../Rells 8/Reel 08 - FINAL.mp4` | 35,68s | 20,9 Mbps |
| `DcFQw6PjM2J` | geral, 16/08 | **não tem FINAL nessa pasta.** Re-renderiza pela composição `Reel02` do `~/Projetos/reels-ferramentas-ia` (`master02.mp4`, 26,8s, `CTA_DE = 728`) | 26,63s | — |

Atenção à grafia da pasta: `Rells para editar ` tem espaço no fim e dois L. Cada pasta guarda
também o bruto da câmera (`C00NN.MP4`, de 0,8 a 1,5 GB) e a legenda publicada.

O `Db37tHWCLMV` e o `DcFQw6PjM2J` são os dois que também existem em Remotion, e por isso
re-renderizam com o CTA novo em vez de exigir corte no editor. O recorte do CTA antigo do
Reel 03 já está extraído em `reels-ferramentas-ia/public/cta_r03.mp4`, com 2,90s.

## O que sai não é só a fala

O bloco final dos seis tem, além do áudio, **legenda queimada "me segue aqui" em amarelo, um
botão azul "Seguir" desenhado e o cursor**. Conferido em oito frames, nos quatro masters e nos
quatro publicados: é literalmente o mesmo trecho reaproveitado nos seis. Trocar o CTA é
substituir o bloco inteiro, senão a peça pede seguir na tela enquanto a fala pede clicar.

## O título de topo não está em master nenhum

"10 TAREFAS de CONTADOR e a IA certa para cada uma" aparece nos publicados e **não aparece no
`Reel 0N - FINAL.mp4`** correspondente, no mesmo instante do vídeo. Ou seja, ele entrou depois
do render, na publicação. É a mesma ressalva já registrada para o C4 no `CRIATIVOS.md`, e vale
para os cinco: quem editar a partir do master perde o título e precisa recriá-lo.

## "Usar publicação existente" e trocar o CTA não se acumulam

O `CRIATIVOS.md` manda subir pelo Gerenciador com "usar publicação existente", para o Reel
manter as curtidas e os comentários do orgânico. **Isso só vale para o Reel como ele está.** No
momento em que o CTA troca, o vídeo é outro e não carrega prova social nenhuma. São dois
caminhos, e é preciso escolher:

1. **Publicar a versão nova no orgânico primeiro**, deixar juntar engajamento por alguns dias e
   só então impulsionar essa publicação. Mantém o efeito de prova social, custa tempo.
2. **Subir direto como criativo no Gerenciador.** Roda hoje, sem curtida nenhuma embaixo.

O caso que o playbook traz (vídeo que já viralizou, CTA trocado, melhor criativo da oferta) não
diz qual dos dois eles usaram.
