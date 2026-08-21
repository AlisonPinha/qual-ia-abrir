# Plano de execução

Fila única do **Qual IA Usar?**, montada em 19/08/2026 cruzando três fontes: a auditoria do
quiz feita no motor, a transcrição do episódio #159 do Segredos da Escala e o
`01 - Projects/Qual IA Usar/Qual IA Usar - Plano Low Ticket.md` do vault.

**Como usar:** atacar de cima para baixo. Cada tarefa só sai da fila quando o critério de
pronto for verificado, não quando o código for escrito. Quem faz está explícito, porque quatro
delas dependem do Alison e não adianta o Claude ficar esperando.

**Estado em 20/08:** produto no ar, entrega funcionando com IA, uma venda de teste feita e
conferida, **zero tráfego real**. A pilha que só depende do Claude está vazia: o que sobra
espera decisão do Alison, gravação, verba ou tráfego rodando.

---

## Fase 0: destravar a primeira venda

Nada aqui é opcional. Sem esta fase, vender é apostar que a entrega funciona.

| # | Tarefa | Quem | Depende | Critério de pronto |
|---|---|---|---|---|
| 0.1 | ~~**Compra de teste de R$ 67**~~ **feita em 19/08, por uma pessoa de fora** | Alison paga, Claude confere | nada | A venda entrou (R$ 64,51 líquidos no painel). **Achou o defeito que nenhum QA meu pegava:** a compradora respondeu no celular, abriu o e-mail no computador e refez as 23 etapas depois de ter pago |
| 0.1b | ~~**Acesso em outro aparelho**~~ **resolvido em 19/08** | Claude | 0.1 | Código de acesso que carrega as respostas, campo no `/mapa` e no `/plano`, leitura de `?c=` na URL e botão para guardar no WhatsApp com o link pronto |
| 0.1c | ~~**Acesso ligado ao pagamento**~~ **homologado com compra real em 20/08** | Claude | 0.1 | Pedido `82QBXtc`, R$ 67: `sck` + UTM chegaram à Cakto; `purchase_approved` gravou pedido ativo no Neon; e-mail abriu `/acesso`; claim e e-mail + telefone em janela anônima emitiram sessão; `/mapa` correspondeu ao diagnóstico. Webhook do `Purchase` respondeu `200`/`ok`; em 21/08 o Meta mostrou **Compra · Ativo · API de Conversões · 1**, com `order_id`. Falta, com autorização do Alison no momento da ação, reembolsar e provar a revogação real |
| 0.1d | ~~**Impedir compra sem diagnóstico**~~ **feito em 20/08** | Claude | nada | O CTA de preço abre/retoma o quiz enquanto não existe `sck`; depois do resultado, o mesmo checkout leva UTM + código + claim. `InitiateCheckout` só dispara quando a Cakto realmente abre. Regressão cobre os dois lados |
| 0.1e | ~~**Limpeza de copy do caminho**~~ **feito em 20/08** | Claude | nada | Marca do controle unificada, crase corrigida, data e ressalva cambial vindas do mesmo dado e fallback automático de `/acesso` explicado na tela |
| 0.2 | ~~**Recolar o Apps Script**~~ **feito 19/08; ampliado em 21/08** | Claude | nada | Versão 8 implantada na **mesma URL** (`AKfycbzY1PYcR4EC...`), então o `ANALITICO_URL` não mudou. Além das abas anteriores, `vendas` recebe uma linha por pedido, sem PII nem `sck`, com upsert de compra/reembolso/chargeback e UTMs. Tentativa sem segredo respondeu `negado`; compra `82QBXtc` entrou uma vez e o reenvio atualizou a mesma linha. A coluna financeira explicita que registra o valor base informado pela Cakto |
| 0.3 | ~~**Conferir o `Purchase` no Events Manager**~~ **conferido e resolvido em 19/08** | Claude | 0.1 | Reprovou: a venda paga não gerou `Purchase` nenhum, porque o Pix é pago fora do navegador. Resolvido no mesmo dia pelo 4.1, que é o webhook da Cakto mandando o evento do servidor |

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
| 1.5 | ~~**De 18 para 23 etapas**~~ **feito 19/08** | Seguiu a Frente 6 do plano do vault, não invenção: entrou a pergunta 10 (`custo_parado`) e as duas que faltavam em cada trilha, fechando as 5 do bloco ramificado. **Parou em 23, não em 30**, porque as 30 a 50 do playbook contam as duas mini VSLs, e o produto foi decidido sem vídeo | Claude | 23 etapas para quem usa IA e nenhuma pergunta de enchimento. **Medido de novo em 19/08 à noite: quem nunca usou IA vê 18 etapas, não 20**, porque as condicionais que somem viraram cinco com a 1.9 |
| 1.6 | ~~**Reason why na abertura**~~ **feito 19/08**. A escassez foi descartada | O porquê está na primeira tela e some depois dela. **A escassez não entra:** o playbook pede escassez sob o botão, mas o projeto proíbe inventar escassez em produto digital sem limite real, e não existe limite real aqui. Entre o playbook e a regra do Alison, vale a regra | Claude | Reason why no ar, sem alterar a simplicidade da etapa 1 |
| 1.7 | ~~**`estilo` passa a valer**~~ **feito 19/08** | Quem diz "prefiro dominar uma a fundo" recebe três ferramentas igual | Claude | A composição muda entre as duas respostas |
| 1.8 | ~~**Botão acima da dobra, medido em aparelho**~~ **feito 19/08** | Estava a 582px da dobra no iPhone, 815px num Android pequeno e 415px no desktop. O que empurrava era o bloco do código de acesso, 200px no meio da venda | Claude | Aparece sem rolar em 390x844, 360x640 e 1280x900 |
| 1.10 | ~~**O teaser deixou de anunciar custo**~~ **feito 20/08** | O card mostrava "Assina agora · US$ 20/mês" nas três linhas, e a soma aparecia logo antes do preço: mediana de US$ 40/mês, medida nas 587.776 combinações, contra um produto de R$ 67 pago uma vez. O olho compara os dois, e o de cima é maior. Achado do Alison, olhando a tela | Claude | O card passou a mostrar a **vitória** no lugar do preço, e o custo mudou de lugar: some do card e aparece na linha do corte, onde joga a favor. 23 de 23 no QA da LP e 5 de 5 no do `/mapa` |
| 1.9 | ~~**Revisão de clareza do questionário**~~ **feito 19/08** | Oito correções de texto, mais duas perguntas que viraram condicionais: quem nunca usou IA responde 14 em vez de 19 | Claude | Nenhuma pergunta fala de trabalho para quem escolheu vida pessoal, e nenhuma pergunta sem sentido para iniciante |

### O custo saiu do card e virou a conta, em 20/08

**O que estava na tela, e por que assusta.** Os três cards do teaser mostravam o momento e o
preço de cada ferramenta. Medido nas 587.776 combinações: a stack pede **US$ 40/mês na
mediana** (cerca de R$ 216), US$ 60 no p90 e até US$ 102 no pior caso. Em 27,1% das
combinações ela não pede nada agora, porque a pessoa respondeu que só quer o que é grátis;
nos outros 73%, uma conta recorrente de três dígitos em real aparecia imediatamente antes de
um preço de R$ 67 pago uma vez.

**O playbook não trata disso**, e isso foi conferido nas duas fontes. O que ele tem e encosta
são os três testes A/B deles, e todos apontam para o mesmo lado: fechar o loop na última etapa
converteu **menos**, prolongar a primeira etapa converteu **menos** em dois nichos, e deixar o
quiz mais bonito piorou. A régua que sai disso é que informação a mais antes do checkout é
candidata a piorar, e o preço das ferramentas é informação a mais.

**A primeira ideia foi descartada por medição, não por gosto.** A tentativa era rastrear a
"vitória" a partir do peso: mostrar a resposta da pessoa que fez aquela ferramenta entrar. O
motor sabe isso, mas a stack é decidida por **soma** de respostas, não por uma. Com o critério
apertado (peso 7, e só em pergunta de tarefa) a cobertura das três é de **7,7%**; com critério
frouxo, ela cobre 95% mas devolve lixo do tipo "No celular" e "Quase nunca abro". Descartado.

**O que entrou:** uma frase de vitória por ferramenta, no `dados.json` em `acesso[n].vitoria`.
Ela não nomeia nem descreve a ferramenta: diz o resultado que a pessoa leva ("material pronto
para a reunião", "a tarefa repetida sem você"). O paywall continua igual, porque nome, `oq`,
`passo` e prompt seguem fora do teaser.

**O custo não sumiu, mudou de lado.** A linha do corte deixou de ser nota de rodapé e passou a
carregar a conta: as três cortadas somam **R$ 479/mês na mediana** (p10 R$ 427, p90 R$ 531), e
em **91,4%** das combinações o corte custa mais que a stack inteira. A frase "cortar a mais
cara já paga o mapa no primeiro mês" é verdadeira em **587.766 das 587.776** combinações, e nas
**10** restantes o código não a escreve: a guarda `maiorCorte >= MOTOR.preco` troca por um texto
sem promessa. Promessa na tela é requisito de código, e aqui ela é verificada por número.

**Tudo passou a ser em real**, a pedido do Alison, com o câmbio de R$ 5,1832 e o euro a
R$ 6,0535, guardados em `diagnostico.cambio` com a data. Não sobrou **nenhum** "US$" nem "€" no
produto: nem na LP, nem no `/mapa`, nem na `/plano`, nem nos comentários do motor. A conta do
erro foi junto: US$ 240/399/700+ por ano viraram R$ 1.244, R$ 2.068 e R$ 3.600+.

**Por que não converter só o lado da economia**, que teria sido mais fácil: comparar R$ 479 com
US$ 40 na mesma tela faz a diferença parecer 12x quando ela é 2,3x. Escolher a moeda para o
número parecer maior é da mesma família da escassez inventada.

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
| Etapas por pessoa | 19 | **23** (18 para quem nunca usou IA, medido em 19/08) |
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
| 2.5 | **Recuperação por WhatsApp** | Claude no n8n | **decisão do Alison sobre o número** | Infra levantada em 19/08 e a metade da Cakto existe. O que trava é de que número sai a mensagem. Ver "O que o 2.5 precisa" abaixo |
| 2.6 | **VSL do upsell** (decisão revista em 19/08: o Alison vai gravar) | Alison grava rosto e voz, Claude grava as telas | 2.2 | O roteiro de 1min45 já está escrito no vault. **Ordem obrigatória: a página existe antes da gravação das telas**, porque o bloco de 0:48 promete "você manda e recebe rodado" e é o único insubstituível do roteiro |
| 2.7 | **Cada um dos 7 dias vira ponto de ascensão** | Claude | 2.2 e existir um próximo produto | "Trate a entrega do seu produto como um funil de vendas pro próximo". Os quatro pontos deles, em ordem: WhatsApp, e-mail, banner e descrição de cada aula. Aqui cada dia é uma aula |
| 2.8 | ~~**Formulário do presente na pós-compra**~~ **feito 19/08** | Claude | 0.1 | Cinco opções e uma saída aberta, no fim do `/mapa`, gravando na aba `presentes`. Fica **depois** do CTA de ascensão de propósito: o voto não pode competir com a venda |
| 2.9 | ~~**Back redirect** no diagnóstico~~ **feito 19/08** | Claude | nada | O pop-up passou a existir no histórico, o voltar mostra uma vez o que a pessoa perde, e quem insiste sai. O do **checkout** não dá: a página é da Cakto |
| 2.11 | ~~**Saber onde a pessoa abandona o quiz**~~ **feito 19/08** | Claude | nada | `sendBeacon` no `visibilitychange` e no `pagehide`, uma linha por pessoa na aba `abandonos`, com o pid onde parou, o enunciado, a posição, quantas respondeu, a área e a UTM. Quem termina fica na mesma linha com `concluiu=sim`, então numerador e denominador ficam juntos. Ligado na LP, no `/mapa` e no `/plano`. **16 de 16 no QA local** e **25 de 25 na regressão** em produção. Apps Script na versão 4, mesma URL |
| 2.12 | **A entrega chegar no WhatsApp** | Claude | **decisão do Alison sobre o número** | Ver "A entrega no WhatsApp" abaixo. A parte 1 e a 2 não dependem de ninguém; a 3, que é a preferida dele, trava no mesmo número do 2.5 |
| 2.10 | **O e-mail de acesso levar o upsell junto** | Alison, se quiser a marcação de origem | 2.3 | **A premissa estava errada, conferido em 19/08.** Ver "O e-mail já leva o upsell" abaixo: não existe corpo de e-mail para escrever, e o link já cai numa página que abre com a oferta. Sobra só marcar a origem do link |

### A entrega no WhatsApp, pedida em 20/08

**A queixa:** a entrega está complexa. Ela é simples para quem compra e abre no mesmo
aparelho (um toque no link do e-mail e o mapa aparece), e complexa nos outros dois caminhos:
aparelho diferente, que cai no quiz de novo, e quem não abre o e-mail, que não recebe nada.
A raiz é estrutural: as respostas moram no navegador, então o mapa só se monta onde a pessoa
respondeu.

**O playbook não tem entrega por WhatsApp.** Ele usa o WhatsApp num lugar só, e é
recuperação de cobrança gerada e não paga, medida em +20%. A entrega da operação de
referência é e-mail com link mais banner na área de membros. Ou seja, isto é ideia nossa,
sem número medido por trás.

| # | O que é | Depende de | Estado |
|---|---|---|---|
| 1 | ~~**Mostrar o código no clique de compra**~~ **feito 20/08** | nada | No ar. O bloco se muda para 14px abaixo do botão que a pessoa clicou, nos dois botões, e diz que o checkout abriu |
| 2 | ~~**"Mandar o meu mapa no WhatsApp" dentro do `/mapa`**~~ **feito 20/08** | nada | No ar. Vão as três na ordem com o custo, o que não assinar e o link com o código. 537 caracteres. O prompt e o passo a passo ficam fora: não cabem e são o que ela vem buscar na página |
| 3 | **O webhook mandar a mensagem quando o Pix cair.** Some o e-mail do caminho. O `/api/cakto` já recebe nome e celular | **o número** | **preferência do Alison.** Trava no mesmo ponto do 2.5 |

**O risco do `teste1` aqui não é ban.** Entrega pós-compra não é disparo frio: a pessoa
acabou de pagar e está esperando. O risco concreto é outro: aquele número está amarrado ao
Clinic.io por webhook, então a resposta do comprador cai no fluxo da clínica. As três saídas
são chip novo com instância própria (o certo), reconectar a `cs-bot-nsm` da agência, ou
aceitar o cruzamento com o Clinic.io.

**O que a documentação da Cakto disse, apurado em 20/08:**
- o payload do `purchase_approved` traz `id`, `refId`, `status`, `baseAmount`, `checkoutUrl`,
  `offer_type`, `customer`, `product` e `offer`;
- **`baseAmount` não estava na lista do `valor()`** e virou correção no mesmo dia: a próxima
  venda real poderia ser descartada em silêncio;
- **`checkoutUrl` é a peça que decide o desenho.** Se ele vier com os parâmetros da URL, o
  `?c=` do código chega no webhook e a mensagem leva o link que abre o mapa pronto em
  qualquer aparelho. Se não vier, o link só monta o mapa no aparelho onde ela respondeu.
  Dá para conferir sem esperar venda nova: a compra de 19/08 saiu pelo link da LP, então os
  parâmetros dela devem estar em Minhas Vendas → detalhes.

**Onde a mensagem roda:** direto no `/api/cakto`, com um `fetch` para a Evolution. Sem n8n no
meio, que seria um salto a mais para cair sem ninguém ver. A chave entra por
`vercel env add EVOLUTION_API_KEY production`, digitada no prompt da CLI.

**O acesso deixou de depender disso em 20/08.** O e-mail continua com um link fixo, mas ele
leva a `/acesso`: o servidor só abre `/mapa` ou `/plano` depois de encontrar compra aprovada.
A mensagem personalizada no WhatsApp continua melhor para conveniência, não para segurança.

### O e-mail já leva o upsell, e não existe e-mail para escrever

Conferido no painel em 19/08. A Cakto **não deixa editar o corpo do e-mail**: ela manda um
"Pagamento Confirmado" próprio, e a única coisa que o produtor controla é o campo "Link de
acesso enviado ao e-mail", hoje com `https://diagnostico.noahai.com.br/acesso` nos cinco
produtos. Não há editor,
template nem variável.

**E o item está resolvido.** `/acesso` cria a sessão e leva ao produto comprado. No Mapa, a
tela pós-compra do upsell (2.3) continua aparecendo antes da entrega. Então a frase "o e-mail
manda só o link do mapa" descrevia o problema errado: o caminho autenticado também chega à
oferta.

**O que sobra é só medição opcional:** o link de entrega não carrega origem. Para separar a
venda de upsell vinda do e-mail, `/acesso` teria que preservar `utm_source=email_cakto` no
redirecionamento. Segurança e entrega não dependem disso.

### O `Purchase` não existe, e isso trava o tráfego pago

Conferido em 19/08 pela UI do Events Manager e pela Graph API, que dão a mesma resposta.
**Nos últimos 14 dias o pixel 827402089420392 recebeu:**

| Evento | Quantidade | Integração |
|---|---|---|
| PageView | 115 | navegador |
| ViewContent | 83 | navegador |
| InitiateCheckout | 22 | navegador |
| `pix_gerado` | 1 | navegador |
| **Purchase** | **0** | nenhuma |

A venda de 19/08 entrou na Cakto (R$ 64,51 líquidos, um pedido) e **não chegou ao Meta**.

**Por que.** O Pix é pago fora do navegador: a pessoa sai do checkout, paga no app do banco e
nunca volta à página. Evento de navegador não tem como disparar aí. Quem resolveria é a API de
Conversões, que envia do servidor, e **o token dela está preenchido** no produto (conferido no
painel, em Configurações → Pixels de conversão → engrenagem do Facebook). Mesmo assim, os
quatro eventos que chegaram vieram todos como **navegador**: nenhum evento de servidor entrou
neste pixel. Ou o token não está sendo usado pela Cakto para o `purchase_approved`, ou ele não
vale mais. Não dá para distinguir os dois sem uma compra nova.

**O que isso significa na prática.** Sem `Purchase`, uma campanha otimizada para compra não tem
o que aprender, e o ROAS aparece zerado no gerenciador. **Isto deixa de ser tarefa da Fase 4 e
vira pré-requisito do 3.3**, o teste seco de nome: sem o evento, o teste mede clique, não venda,
e o playbook manda medir pela conversão final.

**A saída que não depende da Cakto acertar, e que já é o item 4.1:** o webhook
`purchase_approved` da Cakto chama um endpoint nosso, que manda o `Purchase` para a Graph API
com `event_id` para deduplicar. **É o mesmo webhook que o 2.5 precisa**, então os dois se
resolvem com uma configuração só.

**O que os toggles desligados fizeram, e o que não fizeram.** Eles impediram o `Purchase` falso
ao gerar Pix, que era o certo, e no lugar dele a Cakto passou a mandar o evento próprio
`pix_gerado`. O que ninguém ligou foi o `Purchase` de quando o Pix é **pago**.

### O `Purchase` passou a existir, pelo servidor

Feito na mesma noite, porque sem o evento o teste seco de nome mediria clique em vez de venda.
O caminho é `Cakto → /api/cakto → Graph API`, e ele não depende de a Cakto acertar a CAPI dela.

**O que o endpoint faz.** Valida o `secret` do payload (comparação de tempo constante), monta
um `Purchase` por pedido com `currency`, `value`, `content_name` (é ele que separa as quatro
variantes do teste de nome dentro do mesmo pixel) e `order_id`, manda o comprador com hash
SHA-256 depois de normalizar (minúsculas, telefone só com dígitos e com o 55 na frente) e usa
o **id do pedido como `event_id`**, que é o que impede a mesma venda de contar duas vezes num
reenvio. Responde 200 sempre que o segredo confere, inclusive quando o Meta recusa: devolver
erro faria a Cakto reenviar o mesmo problema, e quem tem que gritar é o log.

**Quatro coisas que só se descobrem fazendo, e que valem para a próxima integração:**

| O que parecia | O que é |
|---|---|
| O token da API de Conversões preenchido no produto significa que a CAPI dela funciona | Não significa nada: os quatro eventos do pixel chegaram como **navegador**, nenhum como servidor |
| O `data` do webhook é um objeto | No disparo **Agrupado** é uma **lista** de pedidos, e as datas vêm em camelCase (`paidAt`), não em snake_case |
| A chave secreta é a que você digita | A Cakto **descarta** e gera um UUID próprio ao salvar. O endpoint recusou o primeiro teste com 401 por causa disso, e o certo é copiar o valor dela depois de salvar |
| O botão "Testar" do painel é inofensivo | Ele manda um `purchase_approved` de verdade. Sem guarda, um clique vira venda de mentira no pixel para sempre. O endpoint ignora o id e o e-mail do exemplo do painel |

**A venda de 19/08 foi recuperada à mão.** O webhook só dispara em evento novo, então a única
venda que existe ficaria de fora para sempre. A API de Conversões aceita evento com até 7 dias,
e ela era do mesmo dia: o `Purchase` foi enviado com os dados reais do painel (pedido `6XF4ljB`,
R$ 67, `Método das 3 Abas`, pago às 11h58), e o Meta aceitou. **Duas coisas que esse dado já
diz:** a venda saiu da variante **abas**, e veio **sem UTM nenhuma**, o que bate com não existir
tráfego pago.

**O relatório demora, e isso quase virou diagnóstico errado.** Depois de meia hora, nem a visão
geral do dataset nem o `/stats` da Graph API mostravam o `Purchase`, e a leitura fácil seria
"não chegou". Era atraso: cerca de uma hora depois, o `/stats` passou a trazer **`Purchase: 1`**,
que é a venda de 19/08 recuperada. **Quem responde na hora é Eventos de teste → canal Site**,
que mostrou as compras de teste como `Compra · Processado · Servidor`, uma delas marcada pelo
próprio Meta como **`Desduplicado`**, prova de que o `event_id` faz o trabalho dele. A regra que
fica: para evento de servidor, conferir pela aba de teste na hora e pelo relatório só no dia
seguinte.

**Provado com compra nova em 20/08:** o `purchase_approved` do pedido `82QBXtc` chegou com os
campos esperados, gravou o direito no Neon e produziu resposta `200`/`ok` depois de o Meta
aceitar o payload. Em 21/08 a visualização no relatório agregado apareceu como **Compra ·
Ativo · API de Conversões · 1**, com `order_id` entre os parâmetros.

**Conferido que nada falso entrou:** o pixel continua com zero `Purchase` depois de todos os
testes, porque os de curl foram com `test_event_code` e o do painel caiu na guarda.

### O que o 2.5 precisa, levantado em 19/08 antes de escrever workflow

**A metade da Cakto existe, e é melhor do que o plano supunha.** Conferido na conta, em
Integrações → Webhooks, com os eventos que o painel oferece:

| Evento | Serve para |
|---|---|
| `Pix gerado`, `Boleto gerado`, `PicPay gerado` | cobrança criada e não paga, que é exatamente o gatilho do 2.5 |
| `Abandono de Checkout` | quem preencheu os dados e nem chegou a gerar cobrança, e vem com nome, e-mail e celular |
| `Compra aprovada` | é o que falta para o `Purchase` do 0.3 |

O formulário aceita URL, filtro por produto, chave secreta e mostra o modelo do payload. O
payload do pagamento único traz `customer.name`, `customer.email` e `customer.phone`, mais
`amount`, `id` do pedido e `product`. **Nenhum webhook está criado**: a conta tem zero.

**A metade do WhatsApp existe pela metade.** A Evolution (`api.nsmvps.com.br`, v2.3.7) está no
ar com sete instâncias, cinco conectadas. O problema é de qual número sai a mensagem:

| Instância | Estado | Serve? |
|---|---|---|
| `teste1`, perfil "Alison Araujo" | conectada | é o **número pessoal** dele, e já está amarrada ao Clinic.io por webhook |
| `cs-bot-nsm`, perfil "Nutra Seu Marketing" | **desconectada** | seria o número da agência, não do produto |
| as outras cinco | conectadas | são de clientes: Dra. Luciana, Clínica Solis, Kelly, Pedro |

**Nenhuma é do produto.** O n8n está de pé e com a fundação pronta para reusar: dedup de
webhook, idempotência por side-effect, janela comercial 08-20 e reversão com aviso.

**O que trava, e é decisão do Alison, não minha:** disparo frio para quem não respondeu é o
padrão que faz o WhatsApp banir número, e no `teste1` o número em risco é o pessoal dele, o
mesmo que ele usa para tudo, inclusive para o Clinic.io. O caminho certo é chip novo com
instância própria. **Não montei o workflow**, como combinado: falta a decisão do número.

### O funil do quiz, ligado em 19/08

**Não é do playbook**, e isso foi conferido na fonte: ele não pede medição por etapa, e onde
fala de métrica diz o contrário, "medindo pela conversão final, nunca por métrica
intermediária", no contexto de teste A/B. A aba `abandonos` serve para **diagnóstico do
quiz** (as 19 perguntas seguram ou derrubam?), não para decidir teste, e é assim que ela
tem que ser lida.

**O desenho, e o porquê de cada peça:**

| Decisão | Por quê |
|---|---|
| `visibilitychange` + `pagehide`, não `beforeunload` | no celular, trocar de app ou bloquear a tela não passa por `beforeunload`, e é assim que a maioria sai |
| `sendBeacon`, com `fetch keepalive` de reserva | é o único envio que o navegador promete entregar com a aba fechando |
| Uma linha por pessoa, com upsert por `sid`+`origem` | sem isso, quem troca de aba cinco vezes vira cinco linhas. A chave leva a origem junto porque a mesma pessoa passa pelo quiz do site e depois pelo do `/mapa`, e os dois abandonos são coisas diferentes |
| Quem conclui entra na mesma aba | denominador e numerador juntos: a taxa sai de uma aba só, sem cruzar com `diagnosticos` |
| A linha de quem concluiu fica congelada | achado no teste com POST real: sem isso, refazer o quiz reescrevia a linha para "parou na pergunta 1" com "concluiu sim" ao lado |
| Quem não abriu o quiz não gera linha | quem só leu a página não abandonou quiz nenhum, e entraria como denominador falso |

**O que o QA pegou, e de quem era o defeito.** Duas das falhas eram do teste: esconder a aba
com `bringToFront` não deixa a página `hidden` no Chromium visível, e o `route` do Playwright
enxerga o `sendBeacon` no `pagehide` mas não entrega o corpo. A prova de que o beacon sai de
verdade é o evento de `request`, não o payload. A terceira falha era do produto, e é a linha
congelada acima.

**Ordem obrigatória, e vale para toda mudança de payload:** o Apps Script vai primeiro. O
`doPost` manda todo tipo desconhecido para `gravarLead`, então publicar o front antes faria
cada beacon virar linha na aba `leads`.

**E isso aconteceu, com o meu próprio teste.** Na primeira rodada do QA, um contexto do
navegador ficou sem a interceptação e um beacon real saiu para o Apps Script, que ainda era a
versão 2 e não conhecia o tipo `funil`: virou uma linha vazia na aba `leads`, com o JSON no
`bruto`. Achada na revisão do fim da sessão e apagada. **A lição vale para qualquer teste que
toque endpoint de produção:** interceptar em UM contexto não basta, tem que ser em todos, e
conferir depois se vazou é parte do teste.

**Risco conhecido:** conta gratuita do Apps Script tem 90 minutos de execução por dia. Cada
sinal gasta cerca de um segundo, o que dá umas 5.000 gravações diárias. Com tráfego pago
grande, o teto aparece, e aí a saída é gravar em outro lugar, não cortar a medição.

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
| 3.1 | ~~**Segunda conta de anúncio**~~ **confirmada pelo Alison em 20/08** | Alison | nada | As duas contas exigidas pelo protocolo já existem; não é mais pendência nem bloqueio para o teste |
| 3.2 | **Criativos a partir dos Reels medidos.** Os **18 roteiros estão prontos** em [CRIATIVOS.md](CRIATIVOS.md), escritos em 20/08 contra a Frente 8 do playbook: gancho literal (7s, é o que o teste compara), corpo em beats (a voz é dele) e o CTA casando palavra por palavra com o botão da LP. **Falta gravar** | Alison grava, Claude corta | nada | 6 corpos x 3 ganchos, saídos do banco que já viralizou. **C4 não precisa de gravação**: é o Reel de 98.288 views com o CTA trocado, que é o caso que o playbook traz como melhor criativo de uma oferta inteira. **C5 está bloqueado** até o Alison dar quanto pagou e por quantos meses na ferramenta que não usava: valor plausível ali seria prova inventada |
| 3.3 | **Rodar o teste seco de nome** (R$ 200 a 300) | Alison | 3.1, 3.2, Fase 1 | Uma variante vence por conversão, não por CPC |
| 3.4 | **Ler a origem do tráfego** na planilha e no Events Manager — infraestrutura pronta em 21/08 | Claude | 0.2, 3.3 | A aba `vendas` já cruza pedido, variante e UTM; a compra controlada provou a leitura. Continua aberta até o teste de tráfego dizer de onde vieram diagnósticos e vendas reais da campanha |

---

## Fase 4: o que só faz sentido com tráfego rodando

| # | Tarefa | Quem | Depende | Critério de pronto |
|---|---|---|---|---|
| 4.1 | ~~**CAPI com dedup por `event_id`**~~ **feito 19/08** | Claude | 0.3 | `/api/cakto` recebe o `purchase_approved`, valida o segredo e manda o `Purchase` para a Graph API com o id do pedido como `event_id`. **29 de 29 no QA**, e a cadeia inteira conferida em produção: a Cakto entrega no endpoint (200, 258ms) e o Meta responde `events_received: 1`. Antecipado da Fase 4 porque sem ele o 3.3 mede clique, não venda |
| 4.2 | ~~**GA4**~~ **feito 20/08** | Claude | nada | Propriedade `Qual IA Usar` (`G-J1383RJMK8`) dentro da conta FESTIVAL HIT SALVADOR, fuso Bahia, moeda em real. Quatro eventos com a variante junto. Conferido no Tempo real, em produção: `abriu_diagnostico`, `concluiu_diagnostico` e `iniciou_checkout` chegaram, mais os três automáticos |
| 4.3 | ~~**Seção das ferramentas vira tensão**~~ **feito 19/08** | Claude | nada | As 4 conhecidas com nome e logo, as outras 9 por categoria, com a silhueta do teaser. Conferido em produção: **zero** dos 9 nomes no HTML visível |
| 4.4 | **Auditoria das 9 seções** pela régua de Makepeace, como variante A/B | Claude | 3.3 | Roda como teste, nunca por decreto. **A ordem dos testes é do playbook:** headline primeiro (maior retorno, menor esforço), depois imagem, copy do botão e por fim layout, sempre uma variável por vez e medindo pela conversão final |
| 4.5 | ~~**One Belief**~~ **feito 19/08 no que é meu** | Claude | nada | A crença abre o hero das 4 LPs (com o mecanismo de cada variante), a tela pós-compra e as duas entregas (sem mecanismo, porque servem as 4). **Falta o criativo e o e-mail**, que dependem do Alison |
| 4.6 | ~~**Uso pessoal: decidir com dado**~~ **antecipado em 19/08, por decisão do Alison** | Claude | nada | A trilha de vida pessoal entrou antes do dado, porque a LP passou a prometer uso pessoal e o quiz não atendia. A coluna `descreveu` continua sendo o canal para saber o que falta dentro dela |
| 4.8 | ~~**Captura de contato**~~ **entrou em 20/08, na SAÍDA e não no quiz** | Claude | nada | **O playbook joga contra, e isso foi conferido em 19/08.** Ele não pede nome (o "com o nome dela" era erro da nossa nota) e mede que **prolongar a primeira etapa converteu menos em dois nichos**, com queda de 1% a 2% por etapa. O contato que a operação de referência usa vem de quem gerou cobrança, não do quiz. Se um dia entrar, entra **depois do resultado** e como variante A/B. **Foi o que aconteceu:** o pedido de nome e WhatsApp mora na segunda tela da saída, só para quem já viu o resultado e confirmou que está indo embora. O quiz não ganhou etapa nenhuma, e a `CAPTURA_URL` continua vazia |
| 4.9 | ~~**Desconto pela URL**~~ **removido em 20/08 por decisão do Alison** | Claude | nada | Não fazia sentido antes de existir uma estratégia de desconto. Saíram armazenamento local, aviso visual e propagação ao checkout. A origem passou a aceitar somente UTMs, `fbclid` e `gclid` |
| 4.10 | **Downsell de R$ 47** | Claude | o produto criado na Cakto | A escada do playbook (anual → desconto → mensal → primeiro mês por R$ 1) é de assinatura, e o produto é pagamento único. O equivalente aqui é um degrau abaixo do upsell. **Decidido em 20/08:** entrega **só os 7 dias**, sem o material rodado e sem a configuração das 3, por **R$ 47**, para quem recusa o upsell na tela pós-compra. A fronteira do playbook fica de pé, porque o upsell é o que roda no material dela. **Começado e revertido no mesmo dia, por escolha de prioridade:** o desenho está aqui embaixo |
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

## O downsell, desenhado em 20/08 e ainda não construído

**Decisões tomadas:** entrega só os 7 dias, por R$ 47, para quem clica em pular o upsell.

**Como construir, quando voltar:**
1. `CHECKOUT_DOWNSELL` e `PRECO_DOWNSELL` no `config.py`, vazios desligando a tela, como as
   outras constantes de deploy.
2. `python3 _build/gerar_plano.py semana` → `public/semana/index.html`, com os blocos do
   material, da configuração e da revisão omitidos **no gerador**, do mesmo jeito que o
   paywall da LP: o que não é do produto não chega ao navegador. O JS da variante também para
   de chamar `pedir("config")`, então custa uma chamada de modelo por acesso em vez de duas.
3. A tela do downsell no `#oto-pular` do `/mapa`, que hoje só abre o mapa.
4. Produto na Cakto a R$ 47, com entrega apontando para `/semana`.

**A ressalva que continua valendo:** o upsell de R$ 130 nunca foi oferecido a ninguém de
verdade. Construir o degrau de baixo antes de medir o de cima é otimizar no escuro.

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
- **O Canva não entra no catálogo**, decidido em 20/08 quando a auditoria do ecossistema o
  levantou como categoria ausente. Não voltar a propor em auditoria futura

Atualizado em 20/08/2026, depois da revisão do caminho do lead: checkout travado até existir
diagnóstico, descontos por URL removidos e ajuste do WhatsApp marcado para 21/08.
