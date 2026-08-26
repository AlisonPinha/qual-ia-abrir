# Viabilidade do tráfego pago

**O que este doc é:** a conta que decide se a oferta fecha, e o critério numérico que a rodada
v2 tem que devolver em 29/08 para a próxima sessão ter destino em vez de opinião.

Medições de 26/08/2026 às 17h34, pela Graph API e pela planilha
`Qual IA Usar? — Diagnósticos e Leads`. Nada aqui é estimativa de mercado.

---

## 1. O que está medido

### O topo do funil está sadio

| | v1 (`120249018613980685`) | v2 (`120249034223980685`) |
|---|---|---|
| tempo no ar | 11h30 | 5h54 |
| gasto | R$ 14,32 | R$ 50,19 |
| impressões | 89 | 6.784 |
| CPM | **R$ 159,76** | **R$ 7,40** |
| cliques no link | **0** | 188 |
| CTR | 0% | 2,77% |
| CPC | — | R$ 0,24 |
| landing page views | 0 | 162 |

A correção de otimização (`PURCHASE` → `LANDING_PAGE_VIEWS`) resolveu o que se propunha a
resolver, e isso está provado, não suposto: o conjunto `A | imita conteudo` voltou
`learning_stage_info: SUCCESS`, contra os três conjuntos travados em `LEARNING, conversions: 0`
na v1. 86% dos cliques viram landing page view, então a página carrega e o clique não é acidental.

### O funil quebra numa etapa só

```
impressões           6.784
cliques no link        188    2,77% das impressões
landing page views     162   86,17% dos cliques
abriu o quiz             1    0,62% dos LPV      <- aqui
concluiu o diagnóstico   0
checkout iniciado        0
venda                    0
```

**IC95% da abertura do quiz: [0,11%; 3,41%].** Esse intervalo prova que a taxa é menor que 3,4%
e absolutamente nada além disso. Ele separa "LP travada" de "LP boa", **não** separa "LP travada"
de "tráfego frio de Reels convertendo mal porém dentro do normal".

### Quantas pessoas reais já passaram pelo quiz: três

| Quando | Concluiu | Respondidas | De onde veio |
|---|---|---|---|
| 23/08 08:37 | **sim** | 19/19 | Instagram orgânico, link da bio |
| 25/08 08:59 | **sim** | 19/19 | Instagram DM, recuperação (`ein0vg`) |
| 26/08 15:01 | não | 17/19 | DM, carrossel dinheiro |
| 26/08 16:14 | não | **0/19** | **anúncio A4**, parou na primeira tela |

**A aba `diagnosticos` mente e não pode ser lida como amostra.** Ela tem 117 linhas, todas de
19 e 20/08, e três coisas provam que é a bateria de QA da construção do quiz: 113 das 117
escolheram a mesma área, 100 deram a mesma resposta na mesma pergunta, e 55 dos 116 intervalos
entre linhas consecutivas são menores que 10 segundos. Mesma armadilha das 13 linhas de 25/08
na aba `abandonos`, uma por peça de anúncio em intervalos de segundos: aquilo foi QA de link.

### Vendas: uma no total

Confirmado pelo Alison no painel da Cakto em 26/08. A aba `vendas` da planilha tem uma linha
só, de 20/08 21h03, R$ 66,01, marcada `compra_controlada_20260820_chrome` / `homologacao`.

**Consequência dura: não existe taxa de conversão final medível neste projeto.** Nenhuma casa
decimal. Qualquer CPA calculado a partir do contador de `Purchase` do pixel é aritmética sobre
número que não existe: dos 7 Purchase, **5 são falsos e permanentes**, todos saíram de `SERVER`
(o `/api/cakto`), nenhum do navegador. Ver `reference_pixel_eventos_fantasma`.

---

## 2. A conta que decide

Como não há taxa de conversão final para estimar CPA, a pergunta se inverte: **quanto a conta
precisa entregar para empatar.**

Com front + upsell (R$ 67 + R$ 130 = R$ 197) e LPV a R$ 0,31, o breakeven é **0,157% dos LPV
virando venda**. Cruzando com a taxa de abertura do quiz:

| Se a abertura do quiz for | quanto de quem abre precisa comprar |
|---|---|
| **0,62% (hoje)** | **25,4%** |
| 1,24% | 12,7% |
| 2% | 7,9% |
| 3% | 5,2% |
| 5% | 3,1% |

**É o problema inteiro numa linha.** Com a taxa de hoje, um quarto de todo mundo que abre o
quiz precisa comprar para a conta empatar, e isso não acontece em low ticket. Com 3% de
abertura, a exigência cai para 5,2%, que é um número normal.

**Não é a oferta que está no caminho, é a taxa de abertura.** Ela é a variável que decide se a
conta é impossível ou banal, e é exatamente a que a `/materia` pretende mexer.

### A assimetria, que define o que a verba consegue comprar

| | LPV necessários | custo |
|---|---|---|
| Provar que **não** fecha conta (régua front + upsell) | 1.907 | R$ 591 |
| **A rodada v2 entrega** | **1.595** | já pago |
| Provar que **não** fecha conta (régua só front, R$ 67) | 648 | R$ 201 |
| Provar que **fecha** (10 vendas) | 10.000 a 36.500 | R$ 3.200 a R$ 11.300 |

Três leituras, e as três importam:

1. **A v2 chega perto de conseguir condenar a oferta e não chega nem perto de aprová-la.** Zero
   vendas em 1.595 visitas põe o CPA acima de R$ 165, ainda abaixo dos R$ 197 de breakeven. A
   rodada termina sem veredito, tendo gasto quase tudo que há.
2. **Se a régua fosse só o front, bastariam 648 visitas para condenar**, e esse número já passou.
   É o backend que compra a paciência, exatamente como o playbook diz. Só que o upsell de R$ 130
   também nunca vendeu: a viabilidade está sendo sustentada por um número que ainda é hipótese.
3. **Nada disso diz que a oferta é ruim.** Diz que R$ 444 não decide essa pergunta.

### Onde o playbook está sendo cumprido e onde não

O critério de morte do playbook é **R$ 500 por oferta testada**, e o gasto acumulado é
**R$ 64,51** (v1 + v2), ou seja **12,9% de uma oferta, de sete previstas**. O corte que ele
descreve ("se depois de criativos novos e variações continua empatando, joga fora") pressupõe
variações rodadas, e rodaram 9 criativos por 6 horas numa configuração refeita no meio.

**A oferta não está morta. Ela está não-testada.** Nunca uma pessoa de tráfego pago chegou ao
checkout, em toda a história do projeto.

Desvios do playbook que continuam de pé, todos decisão do Alison: uma conta de anúncio em vez de
duas, só CBO em vez de ABO e CBO, 9 criativos em vez de 18 (6 corpos x 3 ganchos), e sem bidcap
enquanto não houver CPA medido.

**Tensão real dentro do playbook, e ela não se resolve por autoridade:** a `/materia` tem lastro
na linha 276 ("layout que imita o tipo de conteúdo que o público consome converte mais"), na 236
("formato orgânico ganha sempre"), na 123 ("posicionar a oferta como conteúdo de valor") e na 303
("otimizar sempre pela boca do funil"). Mas o mesmo playbook traz um teste A/B medido em **dois
nichos** dizendo que **prolongar a primeira etapa converteu menos**, e que "sofisticar a etapa 1,
incluindo mostrar mais informação antes do primeiro clique, é candidato a piorar". A matéria é
literalmente mais informação antes do primeiro clique. O item a favor é uma frase sem teste
descrito; o item contra é um teste replicado.

---

## 3. O destino: o que fazer quando a v2 fechar em 29/08

**A v2 não vai entregar um veredito sobre a oferta. Ela vai entregar uma taxa de abertura de
quiz confiável.** Qualquer coisa além disso, com essa verba, é leitura de ruído. A rodada fecha
com ~1.595 LPV, o que aperta o IC de [0,11%; 3,41%] para uma faixa decidível.

Ler pela planilha, aba `abandonos`, por `utm_content`, e não pelo contador do pixel.

| Se a taxa de abertura vier | Leitura | O que fazer |
|---|---|---|
| **acima de ~3%** | o descasamento de promessa era o gargalo e o CPA entra em faixa jogável (5,2% de quem abre comprando) | recarregar a conta e testar de verdade com a `/materia`, com a régua de conversão final |
| **entre 1% e 3%** | zona cinzenta: melhora sem resolver | subir a v3 com a `/materia`, medindo só a abertura outra vez, antes de gastar com venda |
| **abaixo de 1%** | não é a oferta nem o criativo: o funil tem fundo demais para o ticket | encurtar o caminho até o dinheiro, não comprar mais tráfego para o mesmo caminho. Olhar sério para a DM, que é de onde saíram as 3 respostas reais |

### O que NÃO fazer, com o motivo medido

**Não trocar o evento de otimização para `InitiateCheckout` nem para `Purchase`.** É a v1 de
novo, um degrau acima de onde ela morreu. O histórico do pixel não entra na conta do
aprendizado: o `learning_stage_info` conta as conversões que *aquele conjunto* gerou na janela
de 7 dias, e a prova é a própria v1 (pixel com 7 Purchase de histórico, conjuntos com
`conversions: 0`).

| Evento | 28 dias | por semana | contra os 50 exigidos |
|---|---|---|---|
| PageView / LPV | 468 | 117,0 | **passa** |
| ViewContent (abre o quiz) | 146 | 36,5 | abaixo |
| InitiateCheckout | 46 | 11,5 | abaixo |
| Purchase | 7 | 1,8 | abaixo |

Encadeando o que está medido, otimizar por `InitiateCheckout` daria **2,8 eventos na rodada
inteira** contra 50 por semana por conjunto, a **R$ 158,73 cada**. E o custo por `ViewContent`
hoje é de **R$ 50,00**: só fica viável depois que a taxa de abertura subir, não antes. É a ordem
inversa da que a intuição sugere.

**Também não vale a v3 nascer sem o pixel na `/materia`.** Ver a seção 4.

---

## 4. Pendência de código que a v3 exige, feita em 26/08 e não publicada

**A `/materia` tinha GA4 e não tinha o pixel da Meta.** Como `landing_page_view` da Meta é o
PageView do pixel disparado no destino, apontar anúncio para lá com o conjunto otimizando
`LANDING_PAGE_VIEWS` devolveria `conversions: 0`, que é o mesmo defeito determinístico que matou
a v1 com `PURCHASE`. **A alteração de destino não é só trocar o link: ela exige o pixel na
matéria antes.**

Corrigido no gerador (`_build/gerar_materia.py`), com a mesma guarda de host das LPs e só
`PageView` (`ViewContent` na LP significa "abriu o quiz", e reusar o nome misturaria duas etapas
do funil no mesmo evento). **Não publicado:** a decisão de 26/08 foi não mexer em nada da
campanha até 29/08.

**A ponte de UTM já funciona e não precisa de trabalho:** a `/materia` propaga
`utm_source/medium/campaign/content/term/fbclid` para o `/` nos dois CTAs, então a leitura por
`utm_content` sobrevive ao salto.

**Bug de rastreio que continua aberto:** o `LINK` do `subir_campanhas.py` fixa
`utm_campaign=stack` mas o path é `/`, que é a variante **controle**. O teste de nome não está
rodando, e quem ler a coluna depois vai creditar ao nome "stack" um tráfego que viu "Qual IA
Usar?". Não contamina a leitura por `utm_content`. Decisão do Alison em 26/08: fica para depois.

---

## 5. Verba

| | |
|---|---|
| folga do `spend_cap` | **R$ 444,08** (teto real, conta pré-paga) |
| v2 a R$ 150/dia até 29/08 00h | ~R$ 300 mais o resto de 26/08 |
| sobra para a v3 | praticamente nada |

**A v3 exige recarga da conta, ou encurtar a v2.** E a janela de aprendizado da Meta é de 7
dias: R$ 444 a R$ 150/dia compra 3, então nenhum conjunto completa a janela nesta rodada.
