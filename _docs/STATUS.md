# Status e pendências

## Próxima sessão começa aqui

**Tarefa: deixar o diagnóstico certeiro e a entrega densa.** São duas frentes, nesta ordem,
e a segunda depende da primeira.

### Frente 1: ramificação do diagnóstico por área

Hoje um médico e um social media respondem exatamente as mesmas 14 perguntas
(`area, tempo_ia, quantas, gasto, tarefa, generica, parada, refaz, horas, nivel, prazo,
estilo, orcamento, onde`). Por isso o resultado parece raso: ele não podia ser fundo, porque
a entrada é genérica.

O que fazer: depois da pergunta `area`, abrir trilhas com perguntas próprias de cada área,
sobre as tarefas reais daquela profissão. Manter o tronco comum onde a pergunta vale para
todos (orçamento, nível, onde usa) e ramificar onde não vale.

Cuidados:
- **Não alongar por alongar.** A operação de referência roda 30 a 50 etapas, mas cada passo
  precisa ser um micro-sim, não enchimento.
- O `motor.js` soma pesos por resposta: perguntas novas precisam de pesos nas 9 ferramentas.
- O `sessao.js` invalida a memória se o questionário mudar (compara os `pids`), então quem
  respondeu antes vai refazer. É o comportamento correto, só não estranhar.
- As 4 LPs são geradas do mesmo `dados.json`: mudança de pergunta vale para todas de uma vez
  e **não** quebra o teste de nome.

### Frente 2: IA redigindo prompt e justificativa

Decisão registrada no **ADR-0001** (`_docs/adrs/`): **as regras decidem, a IA redige.** O
motor determinístico continua escolhendo as 3 ferramentas; a IA escreve o prompt sob medida,
a justificativa e o que não assinar.

O que construir:
- Function na Vercel (`/api/mapa`), com a chave da API fora do navegador.
- **Fallback obrigatório** para o texto fixo do `dados.json` se a API falhar ou demorar.
- **Streaming:** mapa determinístico na hora, textos da IA por cima.
- **Rate limit**, porque o `/mapa` é público.

Custo medido: menos de R$ 0,35 por mapa no modelo mais caro, contra R$ 3,16 de taxa da Cakto
por venda. Custo não é critério aqui, qualidade é.

### Ainda pendente e não bloqueia nenhuma das duas

**A compra de teste de R$ 67.** É o que decide se dá para entregar o mapa pronto em outro
aparelho: se a Cakto repassar parâmetros na URL de entrega, o `/mapa?d=<respostas>` monta
tudo sem a pessoa refazer nada. Se não repassar, o comportamento atual continua (memória
local por 30 dias no mesmo aparelho, e refazer o quiz dentro do `/mapa` em outro).

Use o checkout da `abas`, `regra` ou `stack`, que nunca receberam venda.

### O estado de hoje, para não ter que descobrir de novo

| Variante | Produto na Cakto | LP | Checkout |
|---|---|---|---|
| controle | Qual IA Usar? | `/` | `https://pay.cakto.com.br/3fxqxg5_1049811` |
| abas | Método das 3 Abas | `/abas` | `https://pay.cakto.com.br/32hjw7j_1049893` |
| regra | Regra das 3 IAs | `/regra` | `https://pay.cakto.com.br/8t2cigd_1049903` |
| stack | Stack Mínima | `/stack` | `https://pay.cakto.com.br/3dtj6z8_1049909` |

Domínio: **`https://diagnostico.noahai.com.br`** (o `.vercel.app` responde 308 para ele).
Os 4 produtos são idênticos, exceto nome e página de vendas.

**Onde ler o resultado do teste de nome:** planilha "Qual IA Usar? — Diagnósticos e Leads",
aba `diagnosticos`, coluna `origem` (`site`, `abas`, `regra`, `stack`). Tem 6 linhas de teste
que podem ser apagadas: as com origem `teste` e as do "Teste do Claude".

### Tracking, ligado em 18/08

Pixel do Meta **827402089420392**, o mesmo nos quatro. Um pixel só aprende junto;
quatro pixels separados fragmentariam o aprendizado e não somariam.

| Onde | Evento | Dispara quando |
|---|---|---|
| LP | `PageView` | a página carrega |
| LP | `ViewContent` | o pop-up do diagnóstico abre |
| LP | `InitiateCheckout` | clique em qualquer link do `pay.cakto.com.br` |
| Cakto | `Purchase` | a Cakto dispara, **só no pagamento aprovado** |

`ViewContent` e `InitiateCheckout` levam `content_name` com o nome da variante, e
o `PageView` se separa pela URL. É assim que o teste de nome se lê no Events
Manager sem depender da planilha.

**O que estava errado e foi corrigido:** a Cakto vem de fábrica com "Disparar
evento Purchase ao gerar um pix" e o mesmo para boleto **ligados**. Pix gerado não
é Pix pago: em low ticket com 80% de Pix isso infla Purchase, mente o ROAS para
cima e ensina o algoritmo a comprar quem gera cobrança e some. Desligado nos
quatro produtos.

**Fica pendente:** os gatilhos equivalentes de **PicPay e Nubank** continuam
ligados (`fbPicpayPurchaseTrigger`, `fbNubankPurchaseTrigger`) porque a interface
da Cakto não expõe esses dois toggles, só Pix e boleto. Como é igual nos quatro
produtos, não distorce a comparação entre variantes, apenas infla um pouco o total
se alguém pagar por PicPay.

**Ainda não feito, de propósito:** CAPI (o campo de token existe em cada pixel, na
engrenagem da linha), domínio verificado, e GA4. CAPI sem dedup por `event_id`
conta a mesma venda duas vezes. Entra depois que a compra de teste confirmar que o
`Purchase` do browser chega limpo.

O `/mapa` **não** recebeu pixel: é página de entrega pós-compra, e `PageView` de
comprador ali só sujaria o público.

### Domínio próprio, ligado em 18/08

`diagnostico.noahai.com.br`, apontado no projeto `qual-ia-abrir` da Vercel. O
domínio raiz `noahai.com.br` já era do Alison e o DNS já estava na Vercel, então
não houve compra nem espera de propagação.

**Por que subdomínio e não caminho:** `noahai.com.br/diagnostico` obrigaria o site
principal a rotear o produto, acoplando dois projetos que deployam separado.

**Por que `diagnostico` e não `stack` ou `qual`:** é a única palavra que não
favorece nenhuma das quatro variantes. Subdomínio com o nome de uma delas daria
vantagem de marca a essa variante e o teste passaria a medir nome mais domínio.

**Domínio verificado no Business Manager** da Nutra Seu Marketing, por registro
TXT de DNS (`facebook-domain-verification=...`, criado via `vercel dns add`).
Verificar o raiz cobre o subdomínio, e não exigiu tocar no site principal. A rota
por metatag foi descartada: ela teria que ir no HTML de `noahai.com.br`, que é
outro projeto.

**Sobre o pixel:** ele vive no portfólio **Nutra Seu Marketing** (não no NOAH.AI),
com o nome `Pixel - 001 - FESTIVAL HIT`, criado em 05/03/2024 e sem atividade há
mais de 90 dias. Foi reaproveitado de propósito pelo Alison por já ter vendido. A
conta de anúncios com acesso a ele é a `CA - 001 - INFO` (828815582355498). A
correspondência avançada automática está **desativada** e vale ligar.

### A fila depois dos checkouts

| # | Tarefa | Depende de | Quem |
|---|---|---|---|
| 1 | ~~**3 produtos na Cakto** e os links em `config.py`~~ **feito em 18/08** | nada | Claude conduz no browser |
| 2 | **Compra de teste de R$ 67** em si mesmo | item 1 | Alison paga, Claude confere a entrega e se a Cakto repassa parâmetros na URL |
| 3 | **Unificar a marca** do logo, hoje "qual ia abrir" contra "Qual IA Usar?" no checkout | nada | Claude, 3 minutos |
| 4 | **Custo do Higgsfield** | conferir no site da ferramenta | Alison confere, Claude atualiza `dados.json` |
| 5 | **Conteúdo dos 7 dias** do upsell de R$ 197 | método do Alison | os dois: Claude estrutura, Alison revisa a voz |
| 6 | **Página `/plano`** da entrega do upsell | item 5 | Claude, ~2h |
| 7 | **Ramificação do diagnóstico** por área, com perguntas próprias em cada trilha | nada | Claude, uma sessão inteira |
| 8 | **Recuperação por WhatsApp** (+20% de faturamento na operação de referência) | item 1 (webhook) | Claude no n8n |
| 9 | ~~**domínio próprio**~~ **feito em 18/08**; falta **Web Analytics** da Vercel | painel da Vercel | Alison |
| 10 | **CAPI, domínio verificado e GA4** | item 2 (ver o Purchase chegar) | Claude |

**Não ligar o upsell no funil antes do item 5.** Vender e não conseguir entregar é
reembolso e reclamação, e queima a autoridade que é o ativo do produto.



Atualizado em 18/08/2026, depois do deploy que deu checkout próprio a cada variante.

## O que a página é hoje

LP de venda do **Qual IA Usar? (R$ 67, ancorado em R$ 147)**, modelada na LP do meuassessor.com. Nove seções:

1. **Hero** com mockup de iPhone rodando uma conversa de WhatsApp (o produto trabalhando)
2. **Faixa** de argumentos de compra
3. **Problema** em 4 sintomas
4. **Casos de uso**: 4 cards com pedido em áudio e resposta oculta, mais 6 chips
5. **Diagnóstico** (o pop-up), chamada com os 3 passos
6. **Escopo**: as 9 ferramentas, só logo e nome
7. **Órbita** radial das categorias
8. **A conta do erro**: US$ 240 / 399 / 700+ por ano contra R$ 67 uma vez
9. **Oferta** com preço, 5 entregáveis e garantia, depois FAQ e fecho

Decisão do Alison em 18/08: **nada de graça**. Saíram a lista pública das 24 tarefas, os
desempates, os papéis das cinco principais, as descrições das ferramentas e o bloco de captura
gratuita. O resultado do diagnóstico é teaser com silhuetas.

## O que entrou em 18/08 (aplicação do playbook de low ticket)

Derivado de dois podcasts do VTurb (Tiago Filemon sobre funil de VSL, e a mesa de Davi
Meurer, Kauê Puglies e Slender sobre low ticket). O plano completo está no vault, em
`01 - Projects/Qual IA Usar/Qual IA Usar - Plano Low Ticket.md`.

| Mudança | Por quê |
|---|---|
| Oferta cortada de 8 para 5 entregáveis | promessa boa demais pelo preço derruba conversão em low ticket, e "Atualizações inclusas" era o produto do upsell dado de graça no front |
| Preço de R$ 47 para R$ 67, âncora de R$ 97 para R$ 147 | decisão do Alison; a âncora subiu junto porque 47 contra 97 dava só 31% de desconto |
| Diagnóstico de 5 para 16 passos (14 perguntas + 2 breaks) | cada clique é um micro-sim; a operação de referência roda 30 a 50 etapas |
| Mecanismo nomeado "Regra das 3 IAs" | critério FHC (fácil, hype, curioso); o nome do produto segue "Qual IA Usar?" até o teste seco decidir |
| CTA "Receber meu diagnóstico personalizado" | nunca "iniciar quiz"; posicionar como conteúdo de valor |
| Entrega paga em `/mapa` | mesmo diagnóstico sem paywall: custo real, primeiro passo e prompt de cada ferramenta |
| Memória do diagnóstico | o comprador não refaz o quiz dentro do `/mapa`, no mesmo aparelho |
| Analytics anônimo | saber qual perfil responde, sem nome nem WhatsApp |
| Checkout Cakto | Pix a 0% + R$ 2,49 contra 8,99% da Kiwify: R$ 5,35 a mais por venda no bolso, com 80% de Pix |

## Arquitetura depois desta sessão

```
_build/config.py       constantes de deploy (as 4 URLs e o preço), lidas pelos dois geradores
_build/motor.js        cálculo da stack, injetado nas duas páginas (nunca divergem)
_build/sessao.js       memória no navegador + envio anônimo
_build/gerar.py        → public/index.html   (venda, com paywall)
_build/gerar_mapa.py   → public/mapa/index.html (entrega paga, sem paywall)
```

Build: `python3 _build/gerar.py && python3 _build/gerar_mapa.py && vercel deploy --prod --yes`

## Pendências, em ordem de bloqueio

| # | Pendência | Onde | Impacto |
|---|---|---|---|
| 1 | ~~**`ANALITICO_URL` vazia**~~ preenchida em 18/08 | `_build/config.py` | Falta conferir na planilha se as linhas estão chegando |
| 2 | **Produto do upsell não existe** | fora do repo | O bloco `upsell` do `dados.json` promete plano de 7 dias e prompts preenchidos. **Não ligar o upsell no funil antes de o conteúdo existir** |
| 3 | **Compra de teste** | Cakto | Nunca foi feita. Agora que a entrega por e-mail aponta para o `/mapa`, é a única forma de confirmar que o e-mail chega e se a Cakto repassa parâmetros na URL (de que depende o cruzamento em outro aparelho) |
| 4 | **Custo do Higgsfield** | `dados.json` → `diagnostico.acesso` | Único não conferido, e agora aparece **dentro do produto pago** |
| 5 | **`CAPTURA_URL` vazia** | `_build/config.py` | O passo de nome e WhatsApp não aparece. Menos urgente que o item 1, porque o anônimo já responde as perguntas de produto |
| 6 | **Web Analytics** | painel da Vercel | Precisa do toggle; sem ele o script comentado dá 404 |
| 7 | **Ramificação do diagnóstico** | motor JS | Perguntas diferentes por área. É o que falta para a personalização ser real, e a maior mudança estrutural restante |
| 8 | **Seção de autoridade** | seção `#prova` | Decisão do Alison sobre quais credenciais vão para o ar |
| 9 | ~~**Domínio próprio**~~ resolvido em 18/08 | Vercel | `diagnostico.noahai.com.br`, verificado no Meta |

## Código morto conhecido (não tocar sem motivo)

`gerar.py`, linhas 239 a 246: a variável `oferta_cta` é montada e nunca usada no HTML. Por
isso os dois botões de compra da página saem com o mesmo texto, os dois vindos de
`botao_compra`. Já era assim antes desta sessão.

## O funil do meuassessor, mapeado em 18/08

Serve de referência para os próximos passos:

- **Todos os CTAs da LP** apontam para a âncora de preço, nenhum sai da página. Só o botão do preço vai para o checkout.
- **Checkout em 4 passos:** dados (nome, WhatsApp, e-mail, senha) → plano → pagamento → ativação. Gravam o cliente **antes** de mostrar o preço.
- **Planos:** mensal R$ 59,90 e anual R$ 358,80 (12x de R$ 29,90). O "R$ 29,90" da LP é o anual parcelado.
- **Beacon próprio de funil:** `POST /api/assinar/funil-visita-site`, 1x por sessão, `sendBeacon` com fallback. Não dependem só de Pixel.
- **Etapa gravada a cada passo** (`/api/assinar/sessao/etapa`) e **retomada de sessão** (`/api/assinar/sessao/{token}` devolve `{etapa, metodo}`).
- **Cupom pela URL** (`?cupom=X`) grava por 7 dias no `localStorage` e decora todos os links do checkout com cupom, `fbclid` e as 5 UTMs.
- **Gateways:** EFI/Gerencianet e Asaas para PIX, Hotmart no estorno.
- **Dedup de evento:** `analytics_event_id` do servidor usado no Pixel e na CAPI.

## Bug que aconteceu duas vezes nesta sessão

Recortar o template por `t.index(inicio) ... t.index(fim)` apagou tudo que estava no meio.
Aconteceu ao reescrever o rodapé: levou junto o `<dialog>` do diagnóstico **e a seção de
oferta inteira** (preço, entregáveis, botão de compra). Passou porque a bateria de QA
verificava layout, contraste e console, e bloco ausente não gera erro.

**Antes de cortar por índice:** listar os ids que devem sobreviver no intervalo.
**Depois de gerar:** rodar o inventário de peças e o fluxo do pop-up, não só o de layout.

## Comparativo de checkout, medido em 18/08/2026

Custo por venda de R$ 67, no mix de 80% Pix e 20% cartão que é a regra em low ticket:

| Plataforma | Pix | Cartão | Custo médio | Efetivo |
|---|---|---|---|---|
| **Cakto** (escolhida) | 0% | 4,99% | **R$ 3,16** | 4,7% |
| Eduzz | 4,90% | 4,90% | R$ 5,77 | 8,6% |
| Kirvano | 7,49% | 7,49% | R$ 7,02 | 10,5% |
| Ticto | 6,99% | 6,99% | R$ 7,17 | 10,7% |
| Hotmart | 9,9% | 9,9% | R$ 7,63 | 11,4% |
| Kiwify | 8,99% | 8,99% | R$ 8,51 | 12,7% |

Todas cobram R$ 2,49 fixo, menos Kirvano (R$ 2,00) e Hotmart (R$ 1,00). Taxas conferidas nas
centrais de ajuda oficiais. A recomendação anterior deste arquivo (Kiwify, com números que
não batiam) estava errada e foi substituída.

**Ressalva:** a Cakto é a mais nova da lista e tem reclamações de bloqueio de conta no
Reclame Aqui. O índice de solução não foi verificado, o site bloqueia leitura automatizada.

## Próximo passo sugerido

Ligar `ANALITICO_URL` e fazer uma compra de teste. O produto está vendendo sem medir nada.
