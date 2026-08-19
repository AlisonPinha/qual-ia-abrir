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
| 0.1 | **Compra de teste de R$ 67** no checkout da `stack` | Alison paga, Claude confere | nada | O e-mail de acesso chegou, o link abre o `/mapa`, e o mapa sai escrito pela IA em outro aparelho |
| 0.2 | **Recolar o Apps Script** (`_docs/apps-script-captura.js`) | Alison cola, Claude confere | nada | A aba `diagnosticos` tem as colunas `trilha`, `descreveu` e `utm` no cabeçalho |
| 0.3 | **Conferir o `Purchase` no Events Manager** | Claude | 0.1 | Uma venda, um `Purchase`, com o `content_name` da variante |

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
| 1.5 | **De 18 para ~30 etapas** | O funil campeão deles tinha 37; o piso citado é 30. Com 1.1 feito, faltam duas perguntas por trilha e mais um break | Claude | 30 etapas por pessoa, sem pergunta de enchimento: toda nova ou vota, ou aparece no espelho |
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

**Regra que vale para a fase inteira:** rodar `node _build/testar_motor.mjs` antes e depois de
cada mudança de peso, e registrar o efeito na distribuição. Peso mexido às cegas é como o
mercado faz, e é justamente o que o episódio critica.

---

## Fase 2: o backend, que é onde está o lucro

O plano do vault é explícito: o front não existe para dar lucro, existe para comprar cliente
barato. Hoje não há para onde subir.

| # | Tarefa | Quem | Depende | Critério de pronto |
|---|---|---|---|---|
| 2.1 | **Conteúdo da primeira semana** (os 7 dias) | Claude estrutura, Alison revisa a voz | nada | Os sete dias existem, saem do mesmo motor e não repetem o que o `/mapa` já entrega |
| 2.2 | **Página `/plano`**, a entrega do upsell | Claude | 2.1 | A página existe, entrega os 4 blocos e roda no material que a pessoa cola |
| 2.3 | **Tela pós-compra** com o upsell a R$ 130 (crédito de R$ 67 abatido) | Claude | 2.2 | Sai no fluxo real de quem compra, e o crédito bate |
| 2.4 | **CTA de ascensão dentro do `/mapa`** | Claude | 2.2 | Existe um caminho do produto de entrada para o upsell fora do checkout, porque 80% paga no Pix e não volta |
| 2.5 | **Recuperação por WhatsApp** | Claude no n8n | 0.1 | Mensagem sai para quem gerou cobrança e não pagou |

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
- Sem VSL e sem aula gravada: o upsell sai por software
- O CTA continua abrindo o quiz, e não desviando para o preço. Fica como teste A/B da Fase 4,
  porque o episódio traz dois testes em que prolongar a etapa 1 converteu menos
- O nome do produto não muda sem o teste seco

Atualizado em 19/08/2026.
