# Qual IA Usar?

**No ar:** https://diagnostico.noahai.com.br (o `.vercel.app` responde 308 para ele)

Funil inteiro do **Qual IA Usar?**: a LP de venda em 4 variantes de nome, o diagnóstico de 23
etapas, a entrega paga em `/mapa` (R$ 67) e a entrega do upsell em `/plano` (R$ 130 para quem
já comprou, R$ 197 cheio). O diagnóstico devolve as 3 ferramentas de IA certas para o contexto
da pessoa, na ordem de assinar, com o prompt pronto de cada tarefa da área dela e a lista do
que cortar.

Nasceu do Reel `Db37tHWCLMV` (@aalisonaraujo, 10/08/2026), que fez 89.501 views.

**Em 18/08/2026 a página deixou de ser diretório e virou LP de venda.** Decisão do Alison:
nada de graça. Saíram da página a lista pública das 24 tarefas, os três desempates, os papéis
das cinco principais e a descrição de cada ferramenta. O resultado do diagnóstico é um teaser
com silhuetas, e o conteúdo do produto (nome das ferramentas, prompts, primeiro passo)
**não é enviado ao navegador**. O que ficou de ferramenta são as **4 conhecidas com nome e
logo** (prova emprestada) e as outras **9 por categoria, sem nome nem logo**, com a silhueta do
teaser: conferido em produção, zero dos nove nomes aparece no HTML visível. O que isso custou,
e ele sabia ao decidir: os ~10 mil caracteres que o Google indexava e a entrega prometida no
Reel ("salva essa lista").

Site estático, sem framework e sem dependência de runtime. Um passo de geração em Python
transforma os dados em HTML.

**Pendências e o mapa do funil concorrente:** `_docs/STATUS.md`.

## Estrutura

| Caminho | O que é |
|---|---|
| `_build/dados.json` | **Fonte única.** Ferramentas, tarefas, desempates, splits, números, FAQ, captura |
| `_build/gerar.py` | Gera `public/index.html` a partir do JSON e do CSS |
| `_build/gerar_mapa.py` | Gera `public/mapa/index.html` (entrega paga, mais a venda do upsell) e `_lib/motor.mjs` |
| `_build/gerar_plano.py` | Gera `public/plano/index.html`, a entrega do upsell |
| `_build/gerar_doc_quiz.py` | Gera `_docs/DIAGNOSTICO.md` a partir do `dados.json` |
| `_build/config.py` | As URLs de deploy, os checkouts e o pixel. **Um lugar só para cada URL** |
| `_build/sessao.js` | Memória do diagnóstico no navegador, origem do tráfego e envio anônimo |
| `_build/codigo.js` | O código de acesso: as respostas viram texto curto, para abrir em outro aparelho |
| `_build/espelho.js` | Repete as respostas na tela antes do resultado |
| `_build/regressao.js` | A bateria de ponta a ponta, rodada contra produção |
| `_build/questionario.py` | HTML dos passos e as regras de trilha, usados pelos dois geradores |
| `_build/motor.js` | Cálculo da stack, injetado nas duas páginas e reusado pela function |
| `_build/testar_motor.mjs` | Confere pesos, trilhas e cobertura do catálogo (`node`) |
| `_build/estilo.css` | Todo o CSS. Editar aqui, nunca no HTML gerado |
| `_build/og-fonte.html` | Página 1200x630 que vira a imagem de preview |
| `api/mapa.mjs` | Function da camada de redação por IA do mapa (ADR-0001) |
| `api/plano.mjs` | Function que escreve os 7 dias, as configurações e roda o material da pessoa |
| `_lib/motor.mjs` | **Gerado.** O motor do lado do servidor, para a function não confiar no navegador |
| `public/index.html` | **Gerado. Não editar à mão**, `gerar.py` sobrescreve |
| `public/logos/` | Ícones no mesmo squircle dos Reels |
| `public/og.png` | Preview de compartilhamento |

Os SVGs de logo saem dos paths de `~/Projetos/reels-ferramentas-ia/src/AppIcon.tsx`
(ChatGPT, Claude, Claude Code, Gemini, Perplexity, Higgsfield). Grok, Poppy e Lovable
são os PNGs usados nos próprios Reels.

## Editar

```bash
# 1. mexer em _build/dados.json
# 2. gerar as 4 variantes do teste de nome, as duas entregas e a doc do quiz
for v in "" abas regra stack; do python3 _build/gerar.py $v; done
python3 _build/gerar_mapa.py && python3 _build/gerar_plano.py && python3 _build/gerar_doc_quiz.py
# 3. conferir o motor (pesos, trilhas, cobertura do catálogo)
node _build/testar_motor.mjs
# 4. antes de publicar mudança grande, a bateria de ponta a ponta
cd ~/.claude/skills/playwright-skill && node run.js ~/Projetos/qual-ia-abrir/_build/regressao.js
# 5. publicar
vercel deploy --prod --yes
```

## O diagnóstico ramifica por área

Depois da pergunta `area`, cada área tem perguntas próprias sobre as tarefas daquela
profissão. No `dados.json`, a pergunta de trilha tem um quarto item, que é a regra que a
liga:

```json
["t_tarefa", "No trabalho técnico, onde o tempo vai embora?", [...], {"area": [4]}]
```

Sem esse item, a pergunta é do tronco e vale para todo mundo. Todas as trilhas precisam ter
o mesmo número de perguntas, senão `questionario.py` derruba o build: o contador "n de m"
mentiria para quem estivesse na trilha menor.

### A saída de quem não se encaixou

`diagnostico.aberta` no `dados.json` é `{pid: rótulo do campo}`. Nesses passos, a última
opção abre um campo de uma linha em vez de avançar, para ninguém ter que escolher a tarefa
de outra pessoa só para o quiz deixar passar. O texto não vota no motor (peso vazio), vai
para a redação como descrição delimitada e para a planilha na coluna `descreveu`, que é
onde se descobre qual opção está faltando no quiz.

### A régua de peso, que não é arbitrária

As perguntas do tronco dão de 7 a 9 pontos de vantagem às generalistas antes de a trilha
começar. Por isso, numa pergunta de trilha:

- **7** quando aquela ferramenta É a resposta da tarefa perguntada
- **3** quando ela só ajuda
- **nada** quando a pergunta não diz qual ferramenta serve (ela continua no quiz como
  micro-sim e alimenta a redação da IA, mas não vota)

Peso 4 numa pergunta só não chega ao pódio: o ElevenLabs entrou assim e aparecia em 0% das
stacks. Quem pega isso é `node _build/testar_motor.mjs`, que falha quando alguma ferramenta
do catálogo fica impossível de sair.

## A venda dentro da entrega

O `/mapa` não é só entrega: é onde o upsell é vendido, porque a entrega da Cakto é uma URL fixa
sem redirect pós-compra, e 80% paga no Pix e não volta ao checkout.

- **Tela pós-compra:** aparece uma vez, entre a identificação e o mapa, com a conta R$ 197 menos
  os R$ 67 já pagos. Some para sempre depois da primeira vez (`qia:oto` no navegador).
- **CTA de ascensão:** bloco fixo no fim da entrega, mesmo preço e mesmo link.
- **O presente:** uma pergunta no fim do mapa. O mais votado vira o próximo produto, e o voto
  vai para a aba `presentes` da planilha.

O crédito é de quem comprou, não da tela: quem pagou os R$ 67 tem o abatimento sempre que
voltar. Nada de "só nesta página", que seria escassez inventada.

Sem `CHECKOUT_UPSELL` no `config.py`, as duas peças de venda somem e a entrega segue inteira.

## A camada de IA (`/api/mapa`)

As regras decidem, a IA redige (ADR-0001). O motor escolhe as 3 ferramentas, e a function
escreve a abertura, o porquê de cada uma, o prompt sob medida e o corte.

- **Liga com a chave:** `vercel env add ANTHROPIC_API_KEY` (production e preview).
- **Desliga:** remove a variável. A página volta ao texto fixo do `dados.json` sozinha,
  sem deploy e sem erro na tela.
- O navegador manda só índices de resposta. Nenhum texto dele entra no prompt.
- O texto fica guardado no aparelho: reabrir o mapa não gasta chamada nova.

## O paywall, e por que ele fica no servidor

O teaser do diagnóstico mostra: quantas ferramentas foram identificadas, o momento de compra de
cada uma ("assina agora", "em 30 dias", "quando escalar") e o custo **curto** (`acesso.curto`,
por exemplo "US$ 20/mês"). Nunca o nome, a descrição, o primeiro passo ou o prompt.

Três regras que existem por motivo, não por gosto:

1. **`gerar.py` não coloca `passo` nem o prompt no objeto `MOTOR`.** Se colocar, o produto pago
   sai inteiro no "ver código-fonte" da página.
2. **O custo curto existe porque o completo vazava a ferramenta.** "US$ 20/mês no Plus" e
   "no Google AI Pro" identificam ChatGPT e Gemini para qualquer pessoa do ramo.
3. **A descrição (`oq`) não entra no teaser nem na página.** "Engole PDF, vídeo e podcast
   inteiro" identifica o Gemini na hora para quem já viu o Reel. O campo segue no `dados.json`
   porque é conteúdo do produto, só não é renderizado.

## Por que existe um passo de geração

A primeira versão montava a lista por JavaScript no navegador. Resultado: o robô do
Google, o gerador de preview do WhatsApp e leitores de tela recebiam a página vazia,
porque nenhum deles executa o script. Medido com um leitor externo: ele não conseguia
citar uma ferramenta sequer.

Agora `gerar.py` escreve as 24 tarefas direto no HTML e o JavaScript só liga a busca e
o filtro sobre o que já está lá. Hoje o que precisa estar no HTML é a oferta: promessa, entregáveis, preço, garantias e FAQ. Tudo
isso é texto real, mais o schema `Product` + `Offer` (R$ 67, BRL) e `FAQPage`. O quiz é a exceção
deliberada: vive num `dialog` e depende de JS para calcular.

Regra que decorre disso: qualquer conteúdo novo entra no HTML gerado, nunca só no JS.

## Regerar a imagem de preview

```bash
cd ~/.claude/skills/playwright-skill
node run.js "const b=await chromium.launch();const p=await(await b.newContext({viewport:{width:1200,height:630}})).newPage();await p.goto('file:///Users/alisonaraujo/Projetos/qual-ia-abrir/_build/og-fonte.html');await p.waitForTimeout(600);await p.screenshot({path:'/Users/alisonaraujo/Projetos/qual-ia-abrir/public/og.png'});await b.close()"
```

`og-fonte.html` referencia `logos/` por caminho relativo e vive em `_build/`, que não
tem essa pasta. Ele funciona porque o Playwright carrega por `file://` e sobe um nível;
se mover o arquivo, conferir se os logos ainda aparecem na imagem.

## Pendências

A fila com quem faz e critério de pronto é o `_docs/PLANO-EXECUCAO.md`, e o estado do que está
no ar é o `_docs/STATUS.md`. Em 20/08/2026, o que sobrou **não depende de código**: de que
número sai o WhatsApp, criar o cupom e o produto de R$ 47 no painel da Cakto, gravar a VSL,
revisar a voz dos 7 dias, trocar a chave da Anthropic, e o que só o tráfego resolve.

Três itens que este arquivo listava e já estão resolvidos, para ninguém refazer: o **Web
Analytics** está ligado (o script responde 200 em produção), o **domínio próprio** é
`diagnostico.noahai.com.br` desde 18/08, e **todos os custos de ferramenta foram conferidos no
site oficial em 19/08**, o Higgsfield inclusive.

## QA

A bateria que vale é `_build/regressao.js`, rodada contra produção pela `playwright-skill`
(29 de 29 em 20/08). Ela custa 1 chamada ao `/api/mapa` e 3 ao `/api/plano`, e o limite por IP
permite cerca de 2 rodadas por hora. O protocolo completo, com o que fazer quando o teste
reprova, está em `_docs/CICLO.md`.

Duas armadilhas de medição que já custaram rodadas: `hidden` não esconde elemento cujo CSS
declara `display`, então o QA mede `offsetParent`; e o GA4 descarta Chrome headless como bot,
então validar tag pede user agent de aparelho real.

## Diagnóstico "Qual IA Usar?"

O quiz abre em **pop-up**, num `<dialog>` nativo (backdrop, Esc para fechar e prisão de foco vêm
do navegador, sem biblioteca). A seção `#diagnostico` ficou como chamada, com os 3 passos e o
botão; qualquer elemento com a classe `abre-diag` abre o modal, e o `href="#diagnostico"` segue
como destino se o JS não carregar.

São **19 perguntas em 23 etapas** (14 perguntas para quem nunca usou IA), com 5 delas vindo da
trilha da área que a pessoa escolheu entre as 10. O motor soma pesos por ferramenta e devolve 3
recomendações com a ordem de compra, o primeiro passo e um prompt pronto de cada uma, mais o
bloco "o que não assinar agora". O quiz por dentro está em `_docs/DIAGNOSTICO.md`, gerado do
`dados.json`.

**Atenção ao mexer no CSS do modal:** `display: flex` só pode entrar sob `.modal[open]`. Solto na
regra `.modal`, ele sobrescreve o `display: none` nativo do dialog fechado e o formulário aparece
solto na página antes do JS carregar.

Regras que o motor aplica e que valem manter:

- **Nenhuma trilha gratuita.** Toda recomendação pressupõe investimento. A faixa de orçamento
  define quantas assinaturas entram já e quais ficam para depois, nunca se a pessoa vai pagar.
- **No celular o Claude Code sai da lista.** É terminal, não chat.
- **Claude Code e Claude caem no mesmo momento de compra**, porque são a mesma assinatura.
- **Custo aparece em dólar** com a data da conferência (`diagnostico.aviso_custo`). O campo
  `verificado: false` faz o `gerar.py` avisar no build qual valor ainda precisa ser conferido.

`diagnostico.cabem`, `.celular` e `.perfil` existem para o motor **não depender da ordem** das
perguntas nem das opções. Reordenar no JSON não quebra a lógica; antes quebrava em silêncio.

Editar tudo em `dados.json` → `diagnostico`, nunca no HTML.

## Captura de e-mail

O bloco "Fica sabendo antes" só renderiza o formulário quando `CAPTURA_URL` está preenchida
no `_build/config.py` (Web App do Apps Script gravando na planilha). Enquanto estiver vazia,
sai no lugar o convite pelo direct: formulário sem destino engole lead em silêncio, e o
`gerar.py` avisa isso no fim de cada execução.

**Ela continua vazia de propósito**, e isso não quer dizer que não exista captura. Desde 20/08,
quem confirma que vai embora **com o diagnóstico pronto** recebe o pedido de nome e WhatsApp na
segunda tela da saída, em troca do código de acesso, e o lead sai pelo mesmo Web App do envio
anônimo com `tipo: "lead"`. O passo de contato **dentro** do quiz segue desligado, que é o que
o playbook mede como pior: queda de 1% a 2% por etapa acrescentada, em dois nichos.

## Medição

Três camadas, e cada uma existe por um motivo:

| Camada | O que só ela dá |
|---|---|
| **Web Analytics** da Vercel | visita e referrer. Ligado; o script responde 200. A quebra por UTM é paga no plano Hobby |
| **Pixel do Meta** `827402089420392` | `PageView`, `ViewContent` e `InitiateCheckout` pelo navegador, e o `Purchase` **pelo servidor**, via `/api/cakto`. Só na LP: página de entrega não recebe pixel |
| **GA4** `G-J1383RJMK8` | a quebra por UTM sem pagar. Quatro eventos, com a variante do teste de nome junto |

Mais a planilha do Apps Script, que grava o diagnóstico anônimo, o lead da saída, o abandono
por pergunta e o voto do presente.

## Checkout

`CHECKOUT_URL` no `_build/config.py` liga os dois botões de compra (a seção `#oferta` e o fim do
diagnóstico). Vazia, ambos caem na lista de espera pelo direct e o build avisa. Preço e ancoragem
ficam em `dados.json` → `oferta.preco` e `oferta.de`, e alimentam também o schema `Offer`.

**O preço da página e o do painel da Cakto são diferentes de propósito.** A LP anuncia R$ 67 e o
produto está cadastrado a **R$ 66,01**, porque a taxa de serviço de R$ 0,99 é cobrada do
comprador em todo meio, inclusive Pix, e não tem como desligar. O total do checkout fecha nos
R$ 67 anunciados, e o líquido cai R$ 0,99. O mesmo vale para o upsell: R$ 129,01 para fechar
R$ 130. Mexer em um sem mexer no outro quebra a promessa da página.

Os cinco produtos são idênticos em preço e em método padrão (Pix). Variante do teste de nome que
compara preço diferente não mede nome, mede preço.
