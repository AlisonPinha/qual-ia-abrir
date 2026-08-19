# Plano de execução

Fila única do **Qual IA Usar?**, montada em 19/08/2026 cruzando três fontes: a auditoria do
quiz feita no motor, a transcrição do episódio #159 do Segredos da Escala e o
`01 - Projects/Qual IA Usar/Qual IA Usar - Plano Low Ticket.md` do vault.

**Como usar:** atacar de cima para baixo. Cada tarefa só sai da fila quando o critério de
pronto for verificado, não quando o código for escrito. Quem faz está explícito, porque quatro
delas dependem do Alison e não adianta o Claude ficar esperando.

**Estado em 19/08:** produto no ar, entrega funcionando com IA, zero tráfego real, zero venda.

---

## Fase 0: destravar a primeira venda

Nada aqui é opcional. Sem esta fase, vender é apostar que a entrega funciona.

| # | Tarefa | Quem | Depende | Critério de pronto |
|---|---|---|---|---|
| 0.1 | ~~**Compra de teste de R$ 67**~~ **feita em 19/08, por uma pessoa de fora** | Alison paga, Claude confere | nada | A venda entrou (R$ 64,51 líquidos no painel). **Achou o defeito que nenhum QA meu pegava:** a compradora respondeu no celular, abriu o e-mail no computador e refez as 23 etapas depois de ter pago |
| 0.1b | ~~**Acesso em outro aparelho**~~ **resolvido em 19/08** | Claude | 0.1 | Código de acesso que carrega as respostas, campo no `/mapa` e no `/plano`, leitura de `?c=` na URL e botão para guardar no WhatsApp com o link pronto |
| 0.2 | ~~**Recolar o Apps Script**~~ **feito 19/08 pelo Claude, no navegador** | Claude | nada | Versão 2 implantada na **mesma URL** (`AKfycbzY1PYcR4EC...`), então o `ANALITICO_URL` não mudou. A aba `diagnosticos` nasceu de novo com 21 colunas, incluindo `trilha`, `descreveu` e `utm`, e a `presentes` com as 8 dela. Conferido com POST real nos dois tipos |
| 0.3 | **Conferir o `Purchase` no Events Manager** | Claude | 0.1 | Uma venda, um `Purchase`, com o `content_name` da variante |

### O que a compra de teste ensinou

**A entrega da Cakto é uma URL fixa.** O campo chama "Link de acesso enviado ao e-mail" e
aceita texto puro: sem variável, sem parâmetro de pedido, e não existe redirect pós-compra nas
configurações do produto. Conferido no painel em 19/08. Ou seja, o `c=` que o link do checkout
carrega **morre na plataforma**, e qualquer solução que dependesse dela repassar dado estava
condenada. Foi por isso que o código de acesso nasceu autocontido.

**O transporte é o problema, não o armazenamento.** A pessoa vê o código na tela, mas copiar no
celular e colar no computador exige mandar para si mesma. Daí o botão "Guardar no WhatsApp",
que abre a conversa com a mensagem pronta e o link já com o código dentro: no outro aparelho é
um toque, sem digitar.

---

## Fase 1: o quiz, que é onde a conversão se decide

Ordem por impacto medido, não por esforço. Os itens 1.1 a 1.4 saíram da auditoria do motor;
1.5 e 1.6 saíram do playbook.

| # | Tarefa | Por quê | Quem | Critério de pronto |
|---|---|---|---|---|
| 1.1 | ~~**Loading + espelho das respostas**~~ **feito 19/08** | É o item que os três citam no episódio e o único do fluxo deles que não existe aqui. Dá função às 10 perguntas que hoje somem sem deixar rastro | Claude | A penúltima tela repete as respostas da pessoa e só então revela o teaser |
| 1.2 | ~~**`orcamento` decide de verdade**, com a opção "Nada, quero só o que é grátis"~~ **feito 19/08** | Hoje a faixa escolhida não muda nada, num produto que vende custo real. E o catálogo tem 4 ferramentas gratuitas que nunca são priorizadas | Claude | Duas pessoas com orçamentos opostos recebem stacks diferentes, medido no `testar_motor.mjs` |
| 1.3 | ~~**Endurecer o `onde`**~~ **feito 19/08** | Quem responde "no celular" recebe Lovable como "assina agora". O peso atual é de 1 ponto, insuficiente | Claude | Nenhuma combinação com celular devolve Lovable, Claude Code ou n8n na primeira camada |
| 1.4 | ~~**Pular o que não faz sentido para iniciante**~~ **feito 19/08** | Quem diz "nenhuma ferramenta" ainda recebe "já assinou alguma que não usou?". Sai junto com 1.1 e 1.5 porque as três mexem no contador "n de m", que hoje assume trilhas de tamanho fixo | Claude | As duas perguntas somem quando `quantas` = "Nenhuma ainda", sem o contador mentir |
| 1.5 | ~~**De 18 para 23 etapas**~~ **feito 19/08** | Seguiu a Frente 6 do plano do vault, não invenção: entrou a pergunta 10 (`custo_parado`) e as duas que faltavam em cada trilha, fechando as 5 do bloco ramificado. **Parou em 23, não em 30**, porque as 30 a 50 do playbook contam as duas mini VSLs, e o produto foi decidido sem vídeo | Claude | 23 etapas para quem usa IA, 20 para quem nunca usou, e nenhuma pergunta de enchimento |
| 1.6 | ~~**Reason why na abertura**~~ **feito 19/08**. A escassez foi descartada | O porquê está na primeira tela e some depois dela. **A escassez não entra:** o playbook pede escassez sob o botão, mas o projeto proíbe inventar escassez em produto digital sem limite real, e não existe limite real aqui. Entre o playbook e a regra do Alison, vale a regra | Claude | Reason why no ar, sem alterar a simplicidade da etapa 1 |
| 1.7 | ~~**`estilo` passa a valer**~~ **feito 19/08** | Quem diz "prefiro dominar uma a fundo" recebe três ferramentas igual | Claude | A composição muda entre as duas respostas |
| 1.8 | ~~**Botão acima da dobra, medido em aparelho**~~ **feito 19/08** | Estava a 582px da dobra no iPhone, 815px num Android pequeno e 415px no desktop. O que empurrava era o bloco do código de acesso, 200px no meio da venda | Claude | Aparece sem rolar em 390x844, 360x640 e 1280x900 |
| 1.9 | ~~**Revisão de clareza do questionário**~~ **feito 19/08** | Oito correções de texto, mais duas perguntas que viraram condicionais: quem nunca usou IA responde 14 em vez de 19 | Claude | Nenhuma pergunta fala de trabalho para quem escolheu vida pessoal, e nenhuma pergunta sem sentido para iniciante |

### O que o bloco do motor mudou, medido em 37.632 combinações

| Ferramenta | Antes | Depois | Por quê |
|---|---|---|---|
| Higgsfield | 14,2% | 8,2% | US$ 49/mês só entra em quem declarou orçamento para isso |
| Poppy AI | 5,1% | 1,3% | US$ 399/ano idem |
| Lovable | 7,0% | 3,4% | fora do celular e fora do bolso curto |
| n8n | 7,6% | 3,8% | mesma coisa |
| Claude Code | 7,7% | 6,1% | já saía no celular, agora sai também por teto |

**O efeito colateral, medido e assumido:** os mapas feitos só das quatro generalistas subiram de
49,4% para 63,3%. Investiguei se era falta de peso nas especialistas gratuitas e não é: Gamma
tem peso 7 em "montar apresentação", n8n tem 7 em "automatizar", Gemini Notebook tem 7 em "ler
material longo". O que mudou é que **parte da diferenciação anterior era falsa**, comprada
recomendando Higgsfield e Poppy AI para quem tinha declarado que não podia pagar. O caminho para
recuperar diferenciação sem mentir é o que este repo já concluiu antes: a ordem, o corte e o que
fazer dentro da ferramenta que a pessoa já tem.

**Também entrou:** quem responde "só o que é grátis" recebe a porta gratuita da ferramenta certa
("Começa hoje, de graça · depois, US$ 20/mês") em vez de uma data para assinar, e a stack nunca
volta com menos de três, porque o filtro do bolso podia esvaziar o ranking.

### O que o bloco de fluxo mudou

| | Antes | Depois |
|---|---|---|
| Etapas por pessoa | 19 | **23** (20 para quem nunca usou IA) |
| Perguntas | 16 | 19, sendo 5 por trilha |
| Breaks | 2 | 3 |
| Mapas só das 4 generalistas | 63,3% | **37,4%**, melhor que os 49,4% de antes de tudo |
| Gamma | 4,1% | 19,3% |
| n8n | 3,8% | 12,3% |
| ElevenLabs | 3,0% | 10,3% |

As duas perguntas novas de cada trilha são sempre as mesmas dimensões, com as opções
escritas para a área: **o que precisa sair pronto** (é o que decide Gamma, ElevenLabs e
Higgsfield, e o quiz não perguntava em quase nenhuma trilha) e **o quanto aquilo se repete
igual** (é o que decide o n8n). Foi isso que devolveu a diferenciação perdida no bloco do
motor, sem inventar relevância: a pessoa é quem diz que precisa entregar apresentação.

**Regra que vale para a fase inteira:** rodar `node _build/testar_motor.mjs` antes e depois de
cada mudança de peso, e registrar o efeito na distribuição. Peso mexido às cegas é como o
mercado faz, e é justamente o que o episódio critica.

---

## Fase 2: o backend, que é onde está o lucro

O plano do vault é explícito: o front não existe para dar lucro, existe para comprar cliente
barato. Hoje não há para onde subir.

| # | Tarefa | Quem | Depende | Critério de pronto |
|---|---|---|---|---|
| 2.1 | ~~**Conteúdo da primeira semana** (os 7 dias)~~ **feito 19/08**, falta a revisão de voz do Alison | Claude estrutura, Alison revisa a voz | nada | Os sete dias saem do mesmo motor e não repetem o `/mapa` |
| 2.2 | ~~**Página `/plano`**, a entrega do upsell~~ **feito 19/08** | Claude | 2.1 | No ar em `/plano`, com os 4 blocos e o material rodando de verdade |
| 2.3 | ~~**Tela pós-compra** com o upsell a R$ 130~~ **feito 19/08** | Claude | 2.2 | Aparece uma vez, entre a identificação e o mapa, com a conta R$ 197 menos os R$ 67 já pagos. Produto na Cakto criado e conferido no checkout público |
| 2.4 | ~~**CTA de ascensão dentro do `/mapa`**~~ **feito 19/08** | Claude | 2.2 | Bloco fixo no fim da entrega, mesmo preço e mesmo link. Quem dispensou a tela pós-compra ainda encontra o caminho |
| 2.5 | **Recuperação por WhatsApp** | Claude no n8n | 0.1 | Mensagem sai para quem gerou cobrança e não pagou |
| 2.6 | **VSL do upsell** (decisão revista em 19/08: o Alison vai gravar) | Alison grava rosto e voz, Claude grava as telas | 2.2 | O roteiro de 1min45 já está escrito no vault. **Ordem obrigatória: a página existe antes da gravação das telas**, porque o bloco de 0:48 promete "você manda e recebe rodado" e é o único insubstituível do roteiro |
| 2.7 | **Cada um dos 7 dias vira ponto de ascensão** | Claude | 2.2 e existir um próximo produto | "Trate a entrega do seu produto como um funil de vendas pro próximo". Os quatro pontos deles, em ordem: WhatsApp, e-mail, banner e descrição de cada aula. Aqui cada dia é uma aula |
| 2.8 | ~~**Formulário do presente na pós-compra**~~ **feito 19/08** | Claude | 0.1 | Cinco opções e uma saída aberta, no fim do `/mapa`, gravando na aba `presentes`. Fica **depois** do CTA de ascensão de propósito: o voto não pode competir com a venda |
| 2.9 | ~~**Back redirect** no diagnóstico~~ **feito 19/08** | Claude | nada | O pop-up passou a existir no histórico, o voltar mostra uma vez o que a pessoa perde, e quem insiste sai. O do **checkout** não dá: a página é da Cakto |
| 2.10 | **O e-mail de acesso levar o upsell junto** | Alison edita na Cakto, Claude escreve | 2.3 | Hoje o e-mail manda só o link do mapa. É o ponto de ascensão que alcança quem pagou no Pix e nunca voltou ao checkout |

### O achado que destravou a página, e que vale para o produto inteiro

Os modos que pediam formato com marcador voltavam **vazios**, de forma reprodutível. O log da
function deu o diagnóstico: `stop_reason: max_tokens`, um bloco de conteúdo só e zero caractere
de texto. **O modelo estava gastando o orçamento inteiro raciocinando e parava antes de
escrever.** Com `thinking: { type: "disabled" }` os três modos passaram a responder em 10 a 14
segundos, contra 24 a 47 antes, e o mesmo remédio foi aplicado no `/api/mapa`, que caiu de 34 a
44 segundos para 27 a 33.

Junto entrou uma proteção nos dois: o parser aceita qualquer delta que traga texto, em vez de
exigir `text_delta`. Amarrar no tipo do bloco é o que fazia a resposta sair vazia em silêncio.

**Medido na página:** 7 dias escritos em 13s, 3 configurações em 14s, o material da pessoa
voltando rodado em 5s, console limpo.

**Não ligar o upsell no funil antes de 2.2 existir.** Vender e não entregar é reembolso e
queima a autoridade, que é o ativo do produto.

### O cabeçalho da planilha só nasce com a aba

O script escreve o cabeçalho **uma vez, quando a aba é criada**, então recolar o código não
conserta aba que já existe. E não dava para só acrescentar as três colunas no fim: o cabeçalho
antigo tinha `tarefa`, que virou pergunta de trilha, e a ordem do `appendRow` mudou junto, então
o dado novo entraria embaixo do rótulo errado.

A saída foi **arquivar**: `diagnosticos` virou `diagnosticos ate 19-08` (67 linhas preservadas) e
`leads` virou `leads ate 19-08` (4 linhas). As duas abas novas nasceram certas no primeiro envio.
Nada se perdeu, e a coluna `bruto` das linhas antigas continua com o JSON inteiro.

### A venda dentro da entrega, decidida em 19/08

**O crédito é de quem comprou, não da tela.** O texto antigo do `dados.json` dizia "fora desta
tela o pacote sai por R$ 197 cheio", o que criaria duas verdades de preço no mesmo produto e
seria escassez inventada, proibida aqui. A regra que valeu: **quem pagou os R$ 67 tem o
abatimento sempre**, na tela pós-compra e no lembrete do fim do mapa. Os R$ 197 são o preço de
quem chega direto no pacote, e é isso que a página diz.

**Por que dentro do `/mapa` e não numa página nova.** A entrega da Cakto é uma URL fixa,
conferida em 19/08: não existe redirect pós-compra. Uma página `/obrigado` obrigaria a trocar o
link de entrega dos quatro produtos e deixaria de fora quem já comprou. Dentro do `/mapa` a
oferta sai no fluxo real, sem tocar na plataforma de pagamento.

**A entrega nunca fica atrás da venda.** O botão de abrir o mapa tem o mesmo peso visual do de
comprar, e clicar em comprar também libera o mapa, porque o checkout abre em outra aba. A tela
aparece uma vez (`qia:oto` no navegador) e o mapa abre direto em toda visita seguinte.

**O produto na Cakto:** `Sua primeira semana pronta`, R$ 130,00, entrega em
`https://diagnostico.noahai.com.br/plano`, checkout `https://pay.cakto.com.br/j79id6y_1051180`.
Conferido campo a campo contra o "Qual IA Usar?": pixel 827402089420392, os dois gatilhos de
`Purchase` ao gerar Pix e boleto **desligados** (nascem ligados), PicPay fora, Pix em primeiro,
produtor "Noah.ai" e categoria igual à do front.

**O `/mapa` continua sem pixel**, por decisão anterior: `InitiateCheckout` do upsell não é
medido no navegador, e a venda aparece pelo `Purchase` que a Cakto dispara. Reabrir isso é
decisão do Alison, não minha.

---

## Fase 3: tráfego e o teste de nome

| # | Tarefa | Quem | Depende | Critério de pronto |
|---|---|---|---|---|
| 3.1 | **Segunda conta de anúncio** | Alison | nada | Existe, porque o protocolo do episódio pede duas no mínimo: conta ruim mata oferta boa |
| 3.2 | **Criativos a partir dos Reels medidos** | Alison grava, Claude corta | nada | 6 corpos x 3 ganchos, saídos do banco que já viralizou |
| 3.3 | **Rodar o teste seco de nome** (R$ 200 a 300) | Alison | 3.1, 3.2, Fase 1 | Uma variante vence por conversão, não por CPC |
| 3.4 | **Ler a origem do tráfego** na planilha e no Events Manager | Claude | 0.2, 3.3 | Sabemos de onde veio cada diagnóstico e cada venda |

---

## Fase 4: o que só faz sentido com tráfego rodando

| # | Tarefa | Quem | Depende | Critério de pronto |
|---|---|---|---|---|
| 4.1 | **CAPI com dedup por `event_id`** | Claude | 0.3 | Uma venda conta uma vez, browser e servidor |
| 4.2 | **GA4** | Claude | 4.1 | No ar |
| 4.3 | ~~**Seção das ferramentas vira tensão**~~ **feito 19/08** | Claude | nada | As 4 conhecidas com nome e logo, as outras 9 por categoria, com a silhueta do teaser. Conferido em produção: **zero** dos 9 nomes no HTML visível |
| 4.4 | **Auditoria das 9 seções** pela régua de Makepeace, como variante A/B | Claude | 3.3 | Roda como teste, nunca por decreto |
| 4.5 | **One Belief em todos os pontos de contato** | Claude | nada | A mesma frase no hero, no criativo, no e-mail e no upsell |
| 4.6 | ~~**Uso pessoal: decidir com dado**~~ **antecipado em 19/08, por decisão do Alison** | Claude | nada | A trilha de vida pessoal entrou antes do dado, porque a LP passou a prometer uso pessoal e o quiz não atendia. A coluna `descreveu` continua sendo o canal para saber o que falta dentro dela |
| 4.7 | **World wide** | Claude | 3.3 | Duplicar o funil, filtrar português e excluir o Brasil. O playbook estima meia hora de trabalho e ROI alto nos primeiros dias. Só depois de o funil provar que converte aqui |

---

## A memória parcial na LP, que o back redirect obrigou

A retenção do voltar diz "sair agora não apaga nada". Isso era falso: a LP só salvava as
respostas **no fim** do quiz, e não lia nada ao reabrir. Quem fechava no meio perdia tudo.

Agora a LP salva a cada clique e retoma na primeira pergunta sem resposta, e quem já tinha
terminado cai direto no resultado ao reabrir. O `/mapa` já fazia isso desde a primeira venda;
a LP, não.

**A regra que fica:** promessa na tela é requisito de produto. Se a frase diz que nada se
perde, o código tem que garantir, senão é a mesma família da prova social inventada.

## Prova social, e a regra que vale aqui

O bloco `prova` existe no `dados.json` com a lista **vazia de propósito**, e a seção só é
renderizada quando houver depoimento dentro. A regra, que não se reabre:

**Depoimento só entra quando for real, dito pela pessoa, com print guardado.** Escrever
depoimento nosso, ainda que "para trocar pelo verdadeiro depois", é publicidade enganosa pelo
CDC (art. 37, §1º), fere as regras de anúncio do Meta e é a primeira linha da lista "o que não
fazer" do playbook. Pedido em cenário ilustrativo, do jeito que a seção de casos faz, **não é
depoimento**: ninguém afirma que alguém disse aquilo, e por isso ele é permitido.

**O que existe de prova real hoje, sem depender de aluno:** a demonstração da IA escrevendo o
mapa ao vivo (o playbook considera mais forte que depoimento), os Reels medidos e a compradora
de 19/08, que segundo o Alison gostou. É dela que sai a primeira frase verdadeira.

**Como colar quando chegar:** `prova.depoimentos` recebe pares `["Quem é", "a frase"]`, e o
build faz o resto. Nome da ferramenta não entra na frase, para não furar o paywall.

## Dívidas e riscos conhecidos

| Item | Estado | Nota |
|---|---|---|
| **Chave da Anthropic** | descartável | Foi colada no chat. Trocar quando o Alison pedir, com redeploy |
| **`oferta_cta` morta** | `gerar.py` 239-246 | Pré-existente. Por isso os dois botões saem com texto idêntico |
| **`.gitignore` sem `.env`** | preventivo | Hoje não existe `.env` no projeto, então não há exposição |
| **Preview sem `ANTHROPIC_API_KEY`** | por design | A CLI exige repositório Git conectado; preview cai no fallback de texto fixo |
| **`fbNubankPurchaseTrigger`** | inócuo | Não existe método Nubank na Cakto desde que o PicPay saiu |

---

## O que não se reabre sem o Alison pedir

- Nada de graça: a lista pública das 24 tarefas saiu e o resultado é teaser com silhueta
- Nenhuma trilha gratuita nas recomendações
- ~~Sem VSL e sem aula gravada~~ **revisto em 19/08: o Alison vai gravar a VSL.** O playbook
  pede vídeo sempre, e é o vídeo que camufla a venda, então a decisão nova segue o playbook.
  A entrega continua saindo por software: o vídeo vende, não entrega
- O CTA continua abrindo o quiz, e não desviando para o preço. Fica como teste A/B da Fase 4,
  porque o episódio traz dois testes em que prolongar a etapa 1 converteu menos
- O nome do produto não muda sem o teste seco

Atualizado em 19/08/2026, depois da sessão que ligou a venda dentro da entrega.
