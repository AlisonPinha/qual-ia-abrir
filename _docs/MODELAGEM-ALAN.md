# Modelagem: os anúncios do Alan Nicolas / Academia Lendária

Escrito em 23/08/2026, depois de varrer a Biblioteca de Anúncios da Meta com a busca de frase
exata `"academialendaria"` no Brasil, ordenada por impressões. Irmão do `MODELAGEM-BRAVY.md`,
e a referência mais próxima do que o playbook descreve.

**Por que esta biblioteca substitui a do Bravy como referência principal:** o Bravy deu
estrutura de peça, e as tabelas de lá continuam válidas. O Alan dá a **operação inteira**, e ela
bate com as linhas do playbook que as peças do Bravy contrariavam.

---

## O que está lá, medido

**52 cards, 82 anúncios, um anunciante: Alan Nicolas.** Oferta: **Desafio IAtize-se**, 28 e 29
de agosto, ao vivo, Lote 1, ingresso Silver. Público nomeado na copy: *"Copywriter, Gestor de
Tráfego ou Social Media"*. Mecanismo nomeado: **"Segundo Cérebro"**.

**Toda a campanha subiu nas últimas 16 horas.** 29 cards com 16h de vida e 23 com 15h, ou seja,
lançamento inteiro de uma vez. Só Facebook e Instagram, sem Advantage+ full como o Bravy.

**Quatro páginas de destino, dois domínios:**

| URL | Anúncios |
|---|---|
| `lp.academialendaria.ai/v1-c2/` | 19 |
| `desafio.academialendaria.ai/digital/` | 17 |
| `lp.academialendaria.ai/c2-v0/` | 11 |
| `desafio.academialendaria.ai/digital-v2/` | 5 |

Teste A/B de página com tráfego real, que o playbook diz que menos de 0,5% de quem escala faz.

**16 vídeos e 36 imagens.** Os 16 vídeos são **selfie falada**: câmera na mão, no jardim, na
varanda, no escritório, sem luz e sem tripé, de 36 segundos a 1min21. Um abre com legenda
amarela de story escrita *"Terminei meu relacionamento TÓXICO"*, gancho de fofoca para vender
IA.

**E as 36 imagens não são banner, elas imitam conteúdo:** print de tweet dele com selo azul e
@oalanicolas; portal de notícias com barra vermelha, hambúrguer, lupa, "#ATENÇÃO" e "BREAKING
NEWS"; texto puro sobre branco com **botão azul desenhado** dizendo "Clique em Saiba Mais" e
três setas amarelas; peças de marca com o rosto dele.

**Os ângulos, e todos atacam a mesma crença:**

- "VOCÊ MELHOROU O PROMPT. SUA CAPACIDADE DE ENTREGAR FICOU QUASE IGUAL."
- "VOCÊ APRENDEU A ESCALAR MULTIPLICANDO TRABALHO. Por isso volume novo dói igual."
- "SEU MODELO TEM UM TETO. ELE É EXATAMENTE O NÚMERO DE HORAS QUE VOCÊ AGUENTA."
- "VOCÊ NÃO TEM CHEFE. Mas o WhatsApp do cliente ainda decide quando você para."
- "VOCÊ FICOU MUITO BOM NO QUE FAZ. E VIROU O GARGALO DA PRÓPRIA ENTREGA."
- "Ter várias IAs não significa ter um sistema."
- "QUEM ESCALA SEM CONTRATAR MAIS GENTE NÃO TRABALHA MAIS."

Nenhuma fala de ferramenta, nenhuma promete dinheiro, nenhuma tem escassez dentro da peça.
Todas fecham na mesma âncora seca: *"Desafio IAtize-se. 28 e 29 de agosto · Ao vivo."*

---

## Bravy contra Alan, no que decide

| | JP / Bravy | Alan Nicolas |
|---|---|---|
| Formato | 100% imagem gráfica | 16 vídeos selfie + 36 imagens que imitam conteúdo |
| Rosto | nenhum | em quase tudo |
| Criativos distintos | 5 peças para 22 anúncios | dezenas, quase uma por anúncio |
| Ângulos | 2 (contador, advogado) | 7 ou mais sobre a mesma crença |
| Teste de página | 2 URLs, uma por vertical | 4 URLs, teste A/B real |
| Linhas do playbook que cumpre | 238 (imagem para testar) | 236, 239, 276, "cada criativo validado vira dez" |

---

## Os quatro modelos, elemento a elemento

Peças em `_private/criativos-imagem/`, por `gerar_alan.py`. Todas são produzíveis hoje, sem
gravar nada.

### A1, print de post → modela o tweet do "Segundo Cérebro"

| # | Elemento dele | O nosso |
|---|---|---|
| 1 | Avatar, nome, selo azul, @handle | a headshot, Alison Araújo, selo, `@alisonaraujo` |
| 2 | Pergunta hipotética que **descreve** o mecanismo sem nomear | "Imagine responder 16 perguntas sobre o seu trabalho e receber de volta as três IAs que você deve abrir, na ordem de assinar, com o primeiro prompt de cada uma já escrito." |
| 3 | Parágrafo que **nomeia** o mecanismo e diz o que ele destrava | "É isso que eu chamo de **Regra das 3 IAs**. O problema quase nunca é a IA. É abrir a errada para aquela tarefa." |
| 4 | Fecho curto de escopo | "São 12 no mapa. Você abre três." |
| 5 | Foto ancorada na base | **o cartão da entrega**, não um retrato. Ver abaixo |

**A ordem dele é a coisa toda:** descrever antes de nomear. Quando o nome do mecanismo aparece,
a pessoa já concordou com a descrição. O parágrafo 3 é a `crencaCurta` do `dados.json`, palavra
por palavra.

**A régua do layout não veio dele, veio de casa:** ADR-0002 do `carousel-generator`, o formato
`tweet`. Fundo branco puro, conteúdo no topo, imagem ancorada na base entre 33% e 46% da altura,
nenhuma moldura. A nossa está em 46%, o teto.

**O que não tem, de propósito:** barra de curtidas e respostas. Ela aumentaria o mimetismo e
seria prova social fabricada, que é o art. 37 do CDC e a primeira linha do "o que não fazer" do
plano no vault.

### A2, portal → modela o "#ATENÇÃO / BREAKING NEWS"

| # | Elemento dele | O nosso |
|---|---|---|
| 1 | Barra vermelha: hambúrguer, rótulo, lupa | igual na forma, rótulo "PARA QUEM USA IA" |
| 2 | Kicker gigante: "BREAKING NEWS" | **trocado**: "TER VÁRIAS IAs NÃO É TER UMA STACK." |
| 3 | Foto dele em contexto | a foto de palco, com tela e plateia |
| 4 | Manchete em bold | "Abrir quatro abas não é ter método. É ter quatro contas." |
| 5 | Linha fina explicativa | o que o diagnóstico faz: corta três, mantém três, diz a ordem |
| 6 | Linha do evento em bold | "Regra das 3 IAs · diagnóstico de 2 minutos" |

**O "BREAKING NEWS" saiu e essa é a única divergência deliberada.** Manter a forma de portal é
modelar formato; escrever "última hora" para vender curso é forjar notícia. O kicker virou a
tese, que é o que a peça de fato afirma.

### A4, matéria de portal → modela o "Especialista revela por que 90% dos empreendedores..."

A segunda peça de portal dele, e a mais mimética das duas. Enquanto o A2 usa um kicker em caixa
alta gigante, esta imita o **corpo de uma matéria**.

| # | Elemento dele | O nosso |
|---|---|---|
| 1 | Barra vermelha "#ATENÇÃO" | a mesma do A2, "PARA QUEM USA IA": as duas são a mesma família |
| 2 | Tag de editoria em mono, chapada de vermelho: "IATIZE-SE" | "QUAL IA USAR?" |
| 3 | **Manchete em terceira pessoa**: "Especialista revela por que 90% dos empreendedores do digital não usam nem 2% da capacidade da IA" | "Especialista revela o diagnóstico que ele usa para saber qual IA abrir em cada tarefa do dia." |
| 4 | Lead com o mecanismo nomeado: "não trava por falta de ferramenta, trava por falta de um sistema... o seu Segundo Cérebro" | "O problema quase nunca é a IA: é abrir a errada para aquela tarefa. Em 2 minutos, o mapa diz qual ferramenta resolve cada coisa da sua semana e entrega o prompt pronto de cada uma." |
| 5 | Foto em contexto, abaixo do lead | a de palco, em recorte próprio de 2700x1414 |
| 6 | Chamada com emoji de seta: "⬇️ **Toque no botão** para saber mais." | igual |

**A manchete em terceira pessoa é o que separa esta peça do A2.** "Especialista revela" é a
gramática do advertorial: quem afirma parece ser o veículo, não o anunciante. Funciona porque a
foto embaixo entrega quem é o especialista, e a promessa continua sendo só o que o produto faz.

**É a peça de maior risco de reprovação da família.** Ela tem tag de editoria, manchete de
notícia e lead, ou seja, todos os sinais de matéria. Não usa nome de veículo nenhum e não afirma
fato sobre terceiro, mas a forma pesa na revisão. O Alan roda a dela agora.

**A foto tem recorte próprio.** O slot do A4 é 992x520 (1,91) contra 992x470 (2,11) do A2, então
`palco-alison-med.jpg` é um segundo corte, mais aberto à esquerda para o texto da tela não sair
cortado no meio da palavra. Ele entrega legível o que é um prompt, bem debaixo de uma manchete
sobre qual IA abrir.

### A3, texto sobre branco com botão desenhado → modela o "VOCÊ MELHOROU O PROMPT"

| # | Elemento dele | O nosso |
|---|---|---|
| 1 | Headline vermelha em caixa alta, centralizada, 3 linhas | "VOCÊ TROCOU DE IA TRÊS VEZES. O PROBLEMA NUNCA FOI A IA." |
| 2 | Sub em preto que dá a virada | "Era a tarefa que estava na ferramenta errada. Responde 16 perguntas e descobre quais três são as suas." |
| 3 | **Botão azul desenhado, inclinado**, "Clique em Saiba Mais" | igual |
| 4 | Três setas amarelas apontando para o CTA real | igual |

**É a peça mais crua e a mais desconfortável, e é de propósito.** Ela não tem design: parece
post de grupo de WhatsApp. É a leitura mais literal da linha 276 do playbook.

---

## Duas correções do Alison, em 23/08

### Preço e URL saíram das três peças

As peças traziam "Diagnóstico de 2 minutos · R$ 67 · diagnostico.noahai.com.br". **O Alison
mandou tirar e é ele quem está certo:** essa linha é o carimbo que denuncia a peça como anúncio,
e não fazer isso é a única função destes três formatos.

**O modelo confirma.** Nenhuma peça do Alan traz preço ou URL na arte. Todas fecham numa âncora
seca, "Desafio IAtize-se. 28 e 29 de agosto · Ao vivo", e o CTA real é o botão do próprio
anúncio, fora da imagem. O A2 seguiu esse padrão e ficou com "Regra das 3 IAs · diagnóstico de 2
minutos", que é mecanismo mais âncora, sem número. O A1 e o A3 ficaram sem linha nenhuma.

### O A1 mostra a entrega, não o rosto

A pergunta do Alison foi: *não seria melhor uma imagem de impacto, para o lead bater o olho e
entender que é a solução dela?* Sim, e isso fecha o furo que já estava anotado no
`MODELAGEM-BRAVY.md`: **nenhuma peça mostrava o produto**, contra o "prova vence promessa,
demonstração vence depoimento" do playbook.

A imagem anexada ao post deixou de ser retrato e virou **o cartão da entrega**: as 12 do catálogo
em grade, três apontadas com selo 1, 2 e 3, e a legenda "1ª assina agora · 2ª nos próximos 30
dias · 3ª só quando escalar", que são os rótulos reais do `dados.json`. Dentro de um print de
post isso é natural: é o formato em que as pessoas printam resultado.

**As oito escondidas continuam escondidas.** Só as quatro que a LP nomeia entram com logo, em
quadrado branco; as outras oito são cadeado sobre tile escuro. E das três apontadas, duas são
cadeado e uma é conhecida, o que diz na imagem o que a copy do M3 diz em texto: nem sempre são
as famosas.

**O cartão usa o dark e o gradiente da LP**, ao contrário do resto da peça. Não é incoerência: o
tweet imita o X e a imagem anexada é do produto, então ela veste o produto. Quem clica encontra
a mesma paleta na página.

---

## O mecanismo, mapeado no código em 23/08

**Eu tinha entendido errado, e o Alison corrigiu.** Escrevi as peças em cima do rótulo
("Regra das 3 IAs") e virei o número em argumento. O número é a **saída** do motor, não a
promessa. O mecanismo é **casar cada tarefa com a IA certa de abrir**.

**Onde isso está escrito, e não é interpretação minha:**

| Fonte | O que diz |
|---|---|
| `dados.json` → `diagnostico.crenca` | "Escolher a IA certa **para cada tarefa** é a chave para a IA finalmente devolver resposta útil" |
| `dados.json` → `oferta.entregaveis[2]` | "Os prompts perfeitos: **um para cada tarefa da sua área**, com o tutorial de cada ferramenta" |
| `dados.json` → `oferta.promessa` | "você sabe quais ferramentas precisa, em que ordem começar e **o prompt exato para usar cada uma**" |
| `api/mapa.mjs`, bloco `[[PORQUE1]]` | "**que tarefa dessa pessoa** a ferramenta resolve... não é 'use o Claude', é o que fazer dentro dele" |
| `api/mapa.mjs`, bloco `[[PROMPT1]]` | "escrito **para a tarefa e a área da pessoa**... específico o bastante para não servir a outra pessoa" |
| `_docs/DIAGNOSTICO.md` | o quiz tem **uma pergunta de tarefa por área**, e são elas que votam com o peso mais alto |

**O que o motor de fato faz** (`_build/motor.js`): soma os pesos de cada resposta por
ferramenta, corta o que não cabe no orçamento e o que não roda no celular, e devolve o **top 3
do ranking** mais 3 cortadas. Cada uma recebe um momento (agora, 30 dias, quando escalar).

**Então o "3" é verdade, mas é consequência.** Ele é quantas ferramentas cobrem as tarefas
daquela pessoa dentro do orçamento dela, não a promessa. Liderar a copy pelo três é vender a
embalagem; liderar pela tarefa é vender o mecanismo.

**O que mudou nas peças por causa disso:**

| Peça | Antes | Depois |
|---|---|---|
| A1, parágrafo 1 | "receber de volta as três IAs que você deve abrir" | "listar as tarefas que comem a sua semana e receber, para cada uma, a IA certa de abrir" |
| A1, parágrafo 2 | "É isso que eu chamo de Regra das 3 IAs" | "É abrir a errada para aquela tarefa, e concluir que a ferramenta é fraca quando o pedido é que estava vago" |
| A1, parágrafo 3 | "São 12 no mapa. Você abre três." | "Não é 'usa ChatGPT'. É qual abrir em cada momento do seu dia." |
| A1, cartão | grade de 12 com três numeradas | **tarefa → ferramenta**, cinco linhas, com o rodapé "as suas saem do que você responde" |
| A2, kicker | "NÃO É TER UMA STACK" | "NÃO É SABER QUAL ABRIR" |
| A2, linha fina | "corta três, mantém três" | "mapeia as tarefas da sua semana e devolve, para cada uma, a ferramenta certa" |

**As linhas do cartão saem do `dados.json`, não de invenção:** o `oq` das quatro que a LP
nomeia e o `escopo.sem_nome` das oito que ela esconde, que já é escrito por tarefa ("a que lê o
processo inteiro e responde sobre ele", "a que narra com a sua voz").

**Fica devendo a mesma correção:** o `M2` e o `M4` do `MODELAGEM-BRAVY.md` ainda lideram pelo
número. O nó raiz do M2 é "Regra das 3 IAs" e o M4 abre com "as três do seu caso".

---

## A paleta: aqui a régua da LP não vale

**As peças do Bravy (M1 a M4) vestem a marca. Estas imitam conteúdo, e por isso não vestem.**
Um print de tweet roxo não parece um tweet, parece banner, e aí o formato perde a única coisa
que ele tem. A continuidade com a LP passa a ser feita pelo **rosto e pelo nome**, não pela cor.

Isso não é exceção arbitrária: é a consequência de escolher a linha 276. O layout imita o
conteúdo que o público consome, então ele veste o app imitado, não a marca.

---

## Riscos que estas peças carregam, e você precisa saber antes de subir

1. **O botão azul do A3 imita elemento de interface da plataforma.** A Meta reprova esse tipo de
   peça com alguma frequência. O Alan está rodando com ela agora, então passou para ele, mas
   contar com isso é aposta, não regra.
2. **O A2 tem forma de veículo de imprensa.** Está sem "BREAKING NEWS" e sem nome de veículo
   nenhum, e a manchete é a nossa tese assinada pelo nosso rosto, mas o formato por si já pesa
   na revisão.
3. ~~A foto de palco do A2 depende de você.~~ **Resolvida em 23/08:** está em
   `palco-alison.jpg`, e o A2 usa `palco-alison-crop.jpg`, recortado em 2500x1185 para bater com
   a proporção do slot sem o CSS ter de cortar. Em plano aberto o rosto saía pequeno demais para
   o formato; o recorte fecha na tela, no gesto e na primeira fila da plateia. **A tela ao fundo
   entrega de graça um reforço de tema:** ela está legível dizendo o que é um prompt.
4. **O `@alisonaraujo` do A1 é suposição.** Está numa constante no topo do `gerar_alan.py`.
   Conferir antes de subir: handle errado numa peça que imita print é o que mata a peça.
5. **O A1 usa selo de verificado.** Se a conta não é verificada no X, o selo é adorno falso.
   Ou confirma que é, ou tira: é uma linha do `SELO` no gerador.

---

## Como gerar

```bash
cd _private/criativos-imagem
~/Projetos/carousel-generator/venv/bin/python gerar_alan.py A1 A2 A3 A4
```

Saída em PNG 1080x1350. `NOME`, `ARROBA` e `SITE` são constantes no topo do arquivo.

---

## Conformidade com o playbook, auditada em 23/08

Passei as dez peças pelas regras do playbook, uma a uma. **Sete cumprem, três não**, e duas das
que não cumprem são decisão consciente.

### O que cumprem

| Regra | Como |
|---|---|
| **One Belief** (linha 86): "é o elemento central de tudo, todos os criativos" | as dez carregam a crença depois das correções. Oito delas fazem também o "**justificar o fracasso dela**" que a seção pede: "concluir que a ferramenta é fraca quando o pedido é que estava vago" (A1), "não é a ferramenta que é fraca, é o reflexo" (M3), "o problema nem é o quanto sai" (M1) |
| **Variação de formato é a maior alavanca** (235) | sete formatos distintos entre as duas famílias |
| **Imagem para testar, vídeo para escalar** (238) | é exatamente o papel declarado delas |
| **Isolar uma variável** (273) | três conjuntos separados, e nenhum entra no da triagem I1 a I6 |
| **Medir por conversão final** (274) | `utm_content` por peça, leitura na planilha |
| **Não prometer demais** (regras de oferta) | nenhuma promete resultado financeiro nem "viver de IA" |
| **Nunca entregar o quadrado inteiro** | as oito escondidas seguem como cadeado e categoria |

### O que não cumprem

**1. Formato orgânico (236) e criativo dinâmico (239).** As seis peças M são gráficas e estáticas,
e o playbook é categórico: "todos os criativos campeões vieram de formato orgânico". As quatro A
resolvem parcialmente (imitam conteúdo), mas nenhuma das dez é vídeo. **Decisão consciente:** elas
são triagem, e o que converter vira vídeo.

**2. Seis corpos x três ganchos (263).** Temos os corpos, cerca de sete argumentos distintos, mas
**um gancho por corpo**. O protocolo pede três. Em imagem o gancho é a headline, então cumprir
isso é gerar mais duas variantes de manchete por peça, com o resto pixel-idêntico.

**3. O CTA do criativo casando palavra por palavra com a primeira tela (121).** As seis peças M
trazem "descobrir a minha stack", que é o texto exato do botão da LP. **As quatro peças A não
trazem CTA nenhum na arte**, porque o preço e a URL saíram e porque nenhuma peça do Alan tem.
A regra não morre por isso: ela pode ser cumprida no **texto primário do anúncio**, que fica fora
da imagem. É lá que "descobrir a minha stack" deve aparecer nas quatro peças A.

### O achado que não é sobre as peças

**O nome do mecanismo não nomeia o mecanismo.** O playbook define mecanismo único como "pegar algo
que o mercado já conhece e **renomear**", e o nível 3 de sofisticação é "promessa + mecanismo
estendido". O nosso nome, **"Regra das 3 IAs"**, nomeia a **saída** do motor, não o que ele faz.
Foi exatamente por isso que a copy escorregou para o número: o rótulo puxa para lá.

Um nome que nomeasse o mecanismo apontaria para a tarefa, não para a contagem. Isso não é ajuste
de peça, é decisão de produto: o nome está no `dados.json`, na LP e no quiz. Fica registrado aqui
porque a auditoria o encontrou, não porque eu vá mexer nele.

---

## O que este documento não resolve

- **Os 16 vídeos selfie são o principal e não estão aqui.** É o formato que o playbook chama de
  campeão, é o que a sua conta já mede em 6,4x a mediana e é o que só você pode gravar. Os
  roteiros existem: são os seis corpos do `CRIATIVOS.md`.
- **A diversidade de ângulo dele não foi replicada.** Ele tem sete atacando a mesma crença; nós
  temos três peças. Os outros ângulos já estão escritos em C1 a C6.
- **Ele roda quatro páginas de destino e nós temos uma.** As quatro variantes de nome existem no
  projeto, mas o teste de nome está fora desta rodada por decisão registrada.
