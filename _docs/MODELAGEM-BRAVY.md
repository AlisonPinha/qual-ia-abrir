# Modelagem: os anúncios do Bravy School / @jp.asv

Escrito em 23/08/2026, depois de varrer a Biblioteca de Anúncios da Meta com a busca de frase
exata `"jp.asv"` no Brasil, ordenada por impressões. Complementa o `CRIATIVOS.md`, que continua
sendo o documento das 18 peças em vídeo e das constantes que nada aqui pode furar.

**A regra que autoriza este documento é do playbook**, seção "Do funil de VSL": *modelar a
**ordem** dos elementos de uma copy validada, não as palavras. Marcar cada trecho com um
comentário nomeando o elemento, e escrever o seu na mesma ordem.* É exatamente o que a tabela
de cada modelo abaixo faz. A outra é a linha de criativo: *curiosidade é igual a criatividade,
dez bibliotecas de anúncio abertas geram trinta ideias.*

---

## O que a biblioteca dele mostra, medido

**22 anúncios ativos**, todos da página **Bravy School**, todos em imagem estática, todas as
posições ligadas (Facebook, Instagram, Audience Network, Messenger, WhatsApp, Threads).

| Oferta | Anúncios | Destino |
|---|---|---|
| 57 Agentes de IA pro **Contador** | 18 | `bravy.com.br/57-agents-contador-v3` |
| 57 Agentes de IA pro **Advogado** | 4 | `bravy.com.br/57-agents-adv-v3` |

**Vinte e dois anúncios, cinco peças.** Todas assinadas no rodapé com `@JP.ASV · BRAVY SCHOOL`:
organograma de contabilidade (15), organograma de advocacia (3), "Não é um robô. É o escritório
inteiro" (2), "Enquanto você dormia" (1) e "R$ 67.926 por ano" (1). Preço na peça: R$ 97.

**O erro dele, e ele está medido pela própria Meta.** Em 19 de agosto subiram **10 anúncios com
o mesmo criativo e a mesma copy**. Seis deles carregam o selo **"Baixo volume de impressões,
menos de 100"**. Os que entregam são os de 3 de agosto. Duplicar peça idêntica dividiu leilão e
aprendizado, que é literalmente o *"não duplicar campanha à exaustão"* do playbook. Os dois
ângulos mais fortes dele ("Enquanto você dormia" e "R$ 67.926") têm **um anúncio cada**.

**O histórico, trocando o filtro para todos os anúncios:** seis cards inativos de nov/2023 a
jan/2024, da página **João Pedro Nascimento**, com disclaimer "Pago por **ASV DIGITAL LTDA ME**",
do evento "Hackeando o ClickUp". Cada card agrupa de 3 a 18 anúncios com o mesmo criativo.

**O recorte `jp.asv` não é a operação inteira.** Buscando por `bravy`, aparecem **~170 anúncios
ativos** e outros anunciantes do mesmo ecossistema, com campanhas desde maio de 2026, quase
todas apontando para `bravy.com.br/aula-claude-code`. Ou seja: a assinatura `@jp.asv` marca o
**fundo de funil** (oferta direta), e o volume da casa está na **aula gratuita**. Vale registrar
porque o nosso funil também é oferta direta, sem isca.

---

## Os seis modelos

Cada tabela lê a peça dele elemento a elemento e escreve o nosso na mesma ordem. As peças
geradas estão em `_private/criativos-imagem/`, por `gerar_modelo.py`.

### M1, o número que ancora → modela "R$ 67.926 por ano. Todo ano."

| # | Elemento dele | O nosso |
|---|---|---|
| 1 | Eyebrow de enquadramento: "O QUE VOCÊ JÁ PAGA HOJE" | igual, palavra por palavra: o enquadramento serve aos dois |
| 2 | Setup em corpo pequeno: "Um advogado contratado custa" | "Três IAs que você assinou só pra testar custam" |
| 3 | **Número gigante em cor**: R$ 67.926 | **R$ 3.600** (`dados.json` → `conta.linhas[2]`) |
| 4 | Fecho da frase: "por ano. Todo ano." | igual: a repetição é o que transforma número em dor |
| 5 | Caixa com borda lateral, dizendo o que o número esconde | "Na semana cheia você abre uma. As outras duas cobram no mesmo dia, todo mês, e não fazem falta." |
| 6 | Três micro-stats: R$ 5.660 / 41h / 27.530 | **66** tarefas mapeadas / **12** ferramentas no mapa / **2 min** de diagnóstico. **Corrigido em 24/08:** eram "R$ 479 por mês das cortadas / 91,4% dos casos", números mortos desde a saída da Poppy AI. O `gerar_modelo.py` já produzia os novos; esta linha é que estava atrás |
| 7 | Fonte citada no rodapé: "salario.com.br, 2026" | **cortado pelo Alison em 23/08.** Ver "A linha de fonte" abaixo |
| 8 | Botão "Saiba mais" | pill "descobrir a minha stack" |

**Por que este é o melhor dos seis para nós:** é o único em que o nosso lastro é mais forte que
o dele. Ele cita uma média de mercado de terceiro; nós citamos preço que foi conferido um a um,
com câmbio datado. A citação de fonte era o elemento 7, e ela saiu por decisão do Alison em 23/08.

**Ele responde ao corpo C1** do `CRIATIVOS.md` (a conta que continua saindo), e cobre o mesmo
argumento da I1 num layout que dá muito mais espaço ao número.

### M2, o mapa da cobertura → modela o organograma "EXCLUSIVO PARA ESCRITÓRIOS DE X"

| # | Elemento dele | O nosso |
|---|---|---|
| 1 | Faixa de qualificação de público: "EXCLUSIVO PARA ESCRITÓRIOS DE CONTABILIDADE" | "EXCLUSIVO PARA QUEM VIVE DE CONTEÚDO" (e por área) |
| 2 | Promessa de escopo com começo e fim: "do onboarding ao balancete" | "separa as seis tarefas que comem a sua semana e devolve as três IAs que dão conta delas" |
| 3 | **Nó raiz nomeado: "Claude"** | **"Regra das 3 IAs"**, que é o nosso mecanismo único nomeado. Ver playbook, seção "Mecanismo único" |
| 4 | Grade de 6 blocos com o jargão do público | as **6 opções reais** da pergunta de tarefa daquela área, tiradas do `dados.json` |
| 5 | Assinatura discreta no rodapé | nota de fecho: cada tarefa cai em uma das três, o mapa diz qual e em que ordem |

**A diferença que não pode ser apagada:** o organograma dele mostra o que o produto **faz** (57
agentes trabalhando). O nosso mostra o que o diagnóstico **cobre**, e a nota de rodapé diz que a
ordem sai do mapa, não do desenho. Desenhar papel fixo por tarefa seria anunciar entrega que o
motor não faz, que é a mesma correção já registrada no `gerar_v3.py`.

**Esta é a alavanca de escala de criativo, e é o que ele faz melhor.** Um layout, dez públicos:
o quiz já ramifica em 10 áreas, e três estão prontas (`conteudo`, `negocio`, `vendas`). Trocar a
área **não é oxigenar gancho, é criativo novo**, porque no Andromeda é o criativo que define o
público entregue. Ele prova isso com contador e advogado no mesmo esqueleto.

### M3, o reflexo da mesma aba → modela "Enquanto você dormia"

| # | Elemento dele | O nosso |
|---|---|---|
| 1 | Eyebrow temporal: "NOTIFICAÇÕES · ESTA MADRUGADA" | "O SEU DIA · ONTEM" |
| 2 | Headline de estado: "ENQUANTO VOCÊ DORMIA" | "QUATRO TAREFAS. A MESMA ABA." |
| 3 | Subheadline que completa o quadro | "e cada uma delas tinha uma IA melhor" |
| 4 | 4 cards de notificação com ícone, resultado e horário | 4 tarefas do dia, o que voltou errado em cada uma e a hora, **com o mesmo logo nas quatro** |
| 5 | Linha de reforço: "mais 49 agentes prontos" | faixa: "Não é a ferramenta que é fraca · é o reflexo" |
| 6 | Botão "QUERO TESTAR" | pill "descobrir a minha stack" |


**Reescrita em 23/08, e o motivo importa.** A primeira versão mostrava as quatro conhecidas
cobrando R$ 388,89 e liderava pelo custo. O Alison cortou: *"não está muito congruente com o
produto"*, e estava certo por dois motivos verificáveis. Primeiro, na LP o dinheiro serve para
**justificar os R$ 67**, não para vender o resultado: a seção se chama "A conta que ninguém faz"
e remata em "cortar uma única assinatura errada já paga o mapa no primeiro mês". Segundo, a peça
fazia exatamente o que o produto decidiu não fazer, e está comentado no `gerar.py`: *"no card,
somado, ele é a conta que a pessoa vai pagar todo mês, e assusta antes do preço"*.

**O formato ficou, o assunto mudou.** A notificação é o que faz a peça não parecer anúncio, então
ela permanece. O conteúdo virou o **problema 2 da LP**: *"Abre sempre a mesma. Ter cinco
instaladas não muda nada se o reflexo é abrir a mesma para tudo, inclusive para o que ela faz
pior."* As quatro linhas são tarefas com o que voltou errado, e **o mesmo logo aparece nas
quatro**: a repetição é o argumento, não descuido de arte. A faixa desarma a leitura fácil antes
que ela aconteça: "Não é a ferramenta que é fraca, é o reflexo".

**A inversão obrigatória.** Na peça dele as notificações são o **produto trabalhando**; o nosso
produto não roda sozinho e copiar isso seria prometer entrega que não existe. Então o formato
(notificação nativa do celular, que é o que faz o anúncio não parecer anúncio) fica, e o
conteúdo vira **o problema**, não a entrega. É o C1 contado por outro caminho.

**Só as quatro conhecidas aparecem**, com logo e preço de tabela real. As outras oito continuam
invisíveis, porque são o que a pessoa compra.

### M4, quem ainda não usa IA → modela "Não é um robô. É o escritório inteiro."

| # | Elemento dele | O nosso |
|---|---|---|
| 1 | Eyebrow de categoria + logo no canto | "PRA QUEM COMEÇOU AGORA" + NOAHAI |
| 2 | **Headline de negação em duas linhas**, a segunda em cor | "NÃO É APRENDER IA." / "É SABER QUAL ABRIR.", a segunda no gradiente |
| 3 | Linha de escopo | "São 12 no mapa. Você abre três, e o primeiro prompt de cada uma já vem escrito pra você colar." |
| 4 | Lista do que roda, item a item | os três passos numerados: qual abrir, em que ordem, o que digitar |
| 5 | Pills de fato (8 de 57 agentes · todo dia · R$ 97) | 14 perguntas · 2 minutos · R$ 67 |
| 6 | Botão | pill "descobrir a minha stack" |

**Por que esta peça precisava existir.** O M1 fala com quem já paga IA e desconfia que paga
demais. O M3 fala com quem tem quatro assinaturas rodando. O M2 fala com quem já tem as seis
tarefas da profissão mapeadas. **Nenhum dos três fala com quem nunca abriu uma IA**, e essa
pessoa está no quiz: a pergunta `tempo_ia` tem a opção "Comecei agora" e a trilha dela é de
**14 perguntas**, não 19.

**A dor dela é outra e a peça respeita isso.** Quem começou agora não tem conta para cortar nem
tarefa para automatizar, tem paralisia de escolha. Por isso o argumento não é dinheiro, é o
"não é aprender, é saber qual abrir", que é o mecanismo dito na linguagem de quem está do lado
de fora. Os três passos são o que o produto entrega mesmo: `dados.json` → `diagnostico.comeco`
traz o primeiro movimento e o primeiro prompt literal de cada ferramenta.

**O que ela não faz:** não promete trilha gratuita. As quatro conhecidas têm plano grátis no
catálogo, mas "nenhuma trilha gratuita nas recomendações" é decisão registrada do Alison, e um
anúncio dizendo "não precisa assinar nada" contradiria um produto que entrega ordem de assinar.

### M5, a demonstração da interface → modela "Não é um robô. É o escritório inteiro."

**Não foi gerado, e o motivo é bom.** A estrutura dele é: eyebrow de categoria, headline de duas
linhas (nega o que a pessoa imagina, afirma o que é, segunda linha em cor), mock do produto
rodando com status, lista de itens com check, linha de "e tem mais", pills de fato e CTA.

O `gerar_v3.py` **já executa essa mesma estrutura** no eixo caos x ordem, com os três blocos do
mapa e os selos "por profissão · 2 minutos · R$ 67". Refazer seria criar uma terceira família de
layout para o mesmo argumento. O que o v3 ainda não tem e vale trazer da peça dele é a **headline
de negação**: "Não é lista de ferramenta. É a ordem de abrir." Isso é uma linha de texto no v3,
não uma peça nova.

### M6, a segmentação por vertical → o modelo estrutural, não visual

Ele mantém **um esqueleto e troca o vocabulário**: mesmo layout, mesma promessa, mesma
descrição, só muda a profissão no título e o jargão nos blocos. Foi assim que ele fez 22
anúncios com 5 peças, e é assim que a Meta enxerga públicos diferentes sem gravar nada.

Nós temos 10 áreas no quiz contra as 2 dele. O M2 já está parametrizado por área: acrescentar
uma é acrescentar uma entrada no dicionário `AREAS`, com as opções reais daquela pergunta.

---

## O que não se copia dele

1. **Dez cópias do mesmo criativo.** Está medido: seis com menos de 100 impressões. Peça nova é
   argumento novo, não duplicata.
2. **"Em 5 minutos. Sem contratar, sem treinar, sem retrabalho."** É promessa de substituir
   trabalho. As constantes do `CRIATIVOS.md` proíbem promessa de resultado, e o nosso produto
   entrega decisão, não execução.
3. **A paleta creme e terracota dele.** O que se copia é o princípio, não a cor: o criativo dele
   veste a marca dele, então o nosso veste a nossa. Ver a seção abaixo.
4. **Nomear a ferramenta no nó raiz do organograma.** Ele pode escrever "Claude" porque vende
   Claude. No nosso caso o nó raiz é o mecanismo, senão o anúncio entrega de graça o que o
   diagnóstico cobra para decidir.
5. **O disclaimer "Pago por".** É de anúncio de questões sociais e eleições, herdado das
   campanhas de 2023 dele. Não tem função aqui.

---

## A linha de fonte, cortada em 23/08

As peças nasciam com uma linha de rodapé acima do CTA citando a origem dos números ("preços
conferidos em 19/08/2026 no site de cada ferramenta, dólar a R$ 5,18"), espelhando o
"salario.com.br, 2026" da peça dele. **O Alison mandou tirar de todas, e saiu.** O bloco inteiro
foi removido do gerador, junto com o filete que o separava do CTA.

**O que muda na prática:** o M1 e o M3 seguem afirmando valores em dinheiro, e agora a
verificação desses valores mora só na LP, que tem o aviso de custo e a data do câmbio no
`dados.json`. Os números continuam conferidos e continuam verdadeiros; o que saiu foi a citação
dentro da peça, não o lastro.

**No M2 a mesma linha carregava outra coisa** (23 tarefas, 12 ferramentas, R$ 67, 7 dias de
garantia) e caiu junto. O preço e a duração continuam ditos nas peças que os têm em selo (M4).

---

## A paleta: a da LP, não a do Reel

**Estas peças foram geradas primeiro em `#CCF912` sobre `#101114` e isso estava errado.** O
Alison apontou na hora. A correção está feita e o motivo fica registrado para não voltar:

| | Régua do vídeo orgânico | Régua destas peças |
|---|---|---|
| Fundo | `#151515` | `#0c0a10` (`--dark` da LP) |
| Destaque | `#CCF912` | `linear-gradient(96deg, #c183fb, #e27bb7)` (`--grad` da LP) |
| Card | não se aplica | `#14111c` (`--dark-2`) |
| Texto sobre o destaque | preto | `#14111c`, o mesmo do `.btn-p` |
| Apoio | branco | `#9ca3af` (`--cinza-claro`) e `#f5f0eb` (`--claro`) |

**De onde veio o erro:** as constantes do `CRIATIVOS.md` cravam "cor de destaque `#CCF912`", e o
`gerar_v3.py` seguiu a mesma linha. Só que aquela régua é dado do **orgânico**: o verde-limão saiu
dos dois Reels campeões medidos, gravados no mural de onda, com legenda queimada. Ela vale para o
Reel e continua valendo.

**Anúncio pago é outro caso, e a diferença é funcional.** O criativo pago existe para produzir um
clique que cai na LP. Quem clica precisa reconhecer a página como a continuação do anúncio, e uma
peça verde-limão desembocando numa página roxo e rosa quebra essa continuidade no segundo mais
caro do funil. O JP faz exatamente o que estou dizendo: o laranja e o preto dos criativos dele são
os mesmos da página que recebe o clique.

**Consequência prática:** a linha do `CRIATIVOS.md` sobre `#CCF912` precisa ser lida como régua de
vídeo orgânico, não como constante universal. As peças de imagem para tráfego pago vestem a LP.
O `gerar_v3.py` ainda está em `#CCF912` e fica devendo a mesma correção.

---

## Como isto entra na fila sem quebrar o que já está de pé

**A triagem I1 a I6 continua como está.** Ela isola **uma** variável (a headline, sobre um fundo
pixel-idêntico) e é a única leitura limpa de ângulo que temos. Enfiar layout novo no meio dela
destrói as duas leituras.

**Os M sobem em conjunto próprio, ao lado dela.** Eles não testam headline, testam **formato**,
que o playbook chama de maior alavanca ("mesma copy, formato diferente: de 10 vendas para R$ 400
mil"). Três peças em conjunto separado não é a duplicação exaustiva que ele fez, é lateralização
por criativo, que é o que o próprio playbook recomenda.

**Ordem sugerida para a primeira rodada dos M:** M1 primeiro (é o de lastro mais forte),
M2-conteudo junto (é o teste de público, não de ângulo) e M3 na sequência. Se M2-conteudo
converter, as outras nove áreas saem no mesmo dia, sem câmera.

**A UTM, que não é opcional.** Mesmo padrão do `CRIATIVOS.md`, trocando só o `utm_content`:

```
https://diagnostico.noahai.com.br/?utm_source=ig&utm_medium=paid&utm_campaign=stack&utm_content=M1
```

Códigos: `M1`, `M2-conteudo`, `M2-negocio`, `M2-vendas`, `M3`. Não se misturam com `I1` a `I6`
nem com `C1G1` em diante, então as três leituras ficam separadas na planilha.

**O que decide continua sendo venda, não CTR.** O playbook mostra headline com 60% de interação
convertendo menos que uma de 50%. CTR aqui é critério de fila.

---

## Como gerar

```bash
cd _private/criativos-imagem
~/Projetos/carousel-generator/venv/bin/python gerar_modelo.py M1 M2-conteudo M2-negocio M2-vendas M3
```

O venv do `carousel-generator` é usado porque é onde o Playwright está instalado. Saída em PNG
1080x1350 na mesma pasta. Para uma área nova, acrescentar a entrada em `AREAS` com o público, a
frase de escopo e as seis opções reais daquela pergunta do `dados.json`.

---

## O que este documento não resolve

- **Nada aqui foi ao ar.** O funil segue com zero visita real, e o gargalo continua sendo
  tráfego, não peça.
- **O logo das quatro conhecidas no M3 é decisão do Alison.** Elas já aparecem nomeadas na LP,
  então não fura paywall, mas usar marca de terceiro em anúncio é escolha dele, não minha.
- **Os dias das cobranças no M3 são ilustrativos.** Os valores não: são os preços de tabela do
  `dados.json`, com a fonte no rodapé da peça.
- **M5 não existe como peça.** A recomendação é levar a headline de negação para o `gerar_v3.py`.
