# ADR-0001: as regras decidem, a IA redige

- **Status:** aceito
- **Data:** 18/08/2026
- **Decisor:** Alison

## Contexto

O diagnóstico hoje roda inteiro no navegador: `motor.js` soma pesos das 14 respostas e
devolve as 3 ferramentas, com prompt e primeiro passo vindos fixos do `dados.json`.

Duas queixas motivaram a discussão: o resultado parece raso para quem pagou, e as
perguntas são as mesmas para todas as áreas. Surgiu a proposta de colocar um modelo de
linguagem no meio, aceitando aumento de custo.

## Decisão

Colocar IA no fluxo, mas **só na redação**:

- **O motor determinístico continua escolhendo as 3 ferramentas.** A IA não decide stack.
- **A IA escreve** o prompt sob medida para a tarefa, a área e o nível da pessoa, a
  justificativa de por que aquelas três, e o que não assinar no contexto dela.

Ordem de execução: primeiro a **ramificação do diagnóstico por área**, depois a IA.

## Por quê

**Por que a IA não escolhe as ferramentas.** O ativo do produto é autoridade: "eu testei e
sei o custo real". Um modelo pode citar preço errado, recomendar ferramenta fora do
catálogo de 9 ou inventar recurso. Alucinação de preço é o erro mais caro possível aqui, e
não há como auditar venda a venda. O motor atual é auditável e reprodutível: mesma resposta
gera o mesmo mapa, e dá para ajustar peso.

**Por que a IA escreve.** É onde ela ganha e onde o erro é barato: prompt ruim é chato,
prompt mentiroso sobre preço é reembolso.

**Por que a ramificação vem antes.** Hoje um médico e um social media respondem o mesmo
questionário. IA em cima de informação rasa produz texto bem escrito e genérico, que é pior
que template honesto, porque promete personalização e não entrega.

## Custo (medido em 18/08/2026)

Estimativa de ~2.500 tokens de entrada e ~2.000 de saída por mapa:

| Modelo | US$/mapa | ~R$/mapa | % de R$ 67 |
|---|---|---|---|
| Claude Opus 5 | 0,062 | 0,34 | 0,5% |
| Claude Sonnet 5 | 0,025 | 0,14 | 0,2% |
| Claude Haiku 4.5 | 0,012 | 0,07 | 0,1% |

Referência: a taxa da Cakto é R$ 3,16 por venda. Mesmo o modelo mais caro custa um décimo
do gateway, e o prompt caching corta ainda mais, porque o catálogo das ferramentas é
idêntico em toda chamada. **Custo não é critério nesta decisão.**

## Consequências

Passa a existir backend, o que o projeto não tinha:

- Function na Vercel (`/api/mapa`) para a chave da API nunca ir ao navegador.
- **Fallback obrigatório:** se a API falhar ou demorar, cai no texto fixo do `dados.json`.
  A entrega nunca pode quebrar porque um endpoint piscou.
- **Streaming:** o mapa determinístico aparece na hora e os textos da IA preenchem por
  cima. Sem isso, um produto pago parece travado por alguns segundos.
- **Rate limit no endpoint:** o `/mapa` é público, então `/api/mapa` sem proteção deixa
  qualquer um queimar a conta da Anthropic.

## Alternativas descartadas

- **IA escolhendo a stack:** descartada pelo risco de alucinação de preço e pela perda de
  reprodutibilidade.
- **Entregar PDF em vez da página:** descartada. O produto é operacional, o valor está em
  copiar o prompt e colar na ferramenta, e o `/mapa` já tem botão "Copiar prompt". PDF
  quebra esse gesto no celular, não atualiza e exigiria servidor gerando por comprador.
