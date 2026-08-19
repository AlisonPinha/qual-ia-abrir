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
| 0.2 | **Recolar o Apps Script** (`_docs/apps-script-captura.js`) | Alison cola, Claude confere | nada | A aba `diagnosticos` tem as colunas `trilha`, `descreveu` e `utm` no cabeçalho |
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
| 2.3 | **Tela pós-compra** com o upsell a R$ 130 (crédito de R$ 67 abatido) | Claude | 2.2 | Sai no fluxo real de quem compra, e o crédito bate |
| 2.4 | **CTA de ascensão dentro do `/mapa`** | Claude | 2.2 | Existe um caminho do produto de entrada para o upsell fora do checkout, porque 80% paga no Pix e não volta |
| 2.5 | **Recuperação por WhatsApp** | Claude no n8n | 0.1 | Mensagem sai para quem gerou cobrança e não pagou |
| 2.6 | **VSL do upsell** (decisão revista em 19/08: o Alison vai gravar) | Alison grava rosto e voz, Claude grava as telas | 2.2 | O roteiro de 1min45 já está escrito no vault. **Ordem obrigatória: a página existe antes da gravação das telas**, porque o bloco de 0:48 promete "você manda e recebe rodado" e é o único insubstituível do roteiro |
| 2.7 | **Cada um dos 7 dias vira ponto de ascensão** | Claude | 2.2 e existir um próximo produto | "Trate a entrega do seu produto como um funil de vendas pro próximo". Os quatro pontos deles, em ordem: WhatsApp, e-mail, banner e descrição de cada aula. Aqui cada dia é uma aula |
| 2.8 | **Formulário do presente na pós-compra** | Claude | 0.1 | "Você vai ganhar um presente, qual você quer?" O mais votado vira o próximo produto. É como eles descobrem o que vender depois, e resolve o problema de não sabermos o que vem depois do upsell |

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
| 4.3 | **Seção "as 9 ferramentas" da LP** vira tensão | Claude | nada | As 4 conhecidas ficam com nome, as outras viram categoria sem nome |
| 4.4 | **Auditoria das 9 seções** pela régua de Makepeace, como variante A/B | Claude | 3.3 | Roda como teste, nunca por decreto |
| 4.5 | **One Belief em todos os pontos de contato** | Claude | nada | A mesma frase no hero, no criativo, no e-mail e no upsell |
| 4.6 | **Uso pessoal: decidir com dado** | Claude | 0.2, 3.3 | A coluna `descreveu` diz quantos não se encaixaram nas 10 áreas e o que queriam. Só então se cria trilha |

---

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

Atualizado em 19/08/2026.
