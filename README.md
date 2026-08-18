# Qual IA Usar?

**No ar:** https://qual-ia-abrir.vercel.app

Landing page de venda do produto **Qual IA Usar? (R$ 47)**: diagnóstico de 5 perguntas que
devolve as 3 ferramentas de IA certas para o contexto da pessoa, na ordem de assinar, com o
prompt pronto de cada tarefa da área dela, tutoriais, plano de 7 dias e a lista do que cortar.

Nasceu do Reel `Db37tHWCLMV` (@aalisonaraujo, 10/08/2026), que fez 89.501 views.

**Em 18/08/2026 a página deixou de ser diretório e virou LP de venda.** Decisão do Alison:
nada de graça. Saíram da página a lista pública das 24 tarefas, os três desempates, os papéis
das cinco principais e a descrição de cada ferramenta. O resultado do diagnóstico é um teaser
com silhuetas, e o conteúdo do produto (nome das ferramentas, prompts, primeiro passo)
**não é enviado ao navegador**. O que ficou de ferramenta é só logo e nome, como escopo. O que isso custou, e ele sabia ao decidir: os ~10 mil caracteres
que o Google indexava e a entrega prometida no Reel ("salva essa lista").

Site estático, sem framework e sem dependência de runtime. Um passo de geração em Python
transforma os dados em HTML.

**Pendências e o mapa do funil concorrente:** `_docs/STATUS.md`.

## Estrutura

| Caminho | O que é |
|---|---|
| `_build/dados.json` | **Fonte única.** Ferramentas, tarefas, desempates, splits, números, FAQ, captura |
| `_build/gerar.py` | Gera `public/index.html` a partir do JSON e do CSS |
| `_build/estilo.css` | Todo o CSS. Editar aqui, nunca no HTML gerado |
| `_build/og-fonte.html` | Página 1200x630 que vira a imagem de preview |
| `public/index.html` | **Gerado. Não editar à mão**, `gerar.py` sobrescreve |
| `public/logos/` | Ícones no mesmo squircle dos Reels |
| `public/og.png` | Preview de compartilhamento |

Os SVGs de logo saem dos paths de `~/Projetos/reels-ferramentas-ia/src/AppIcon.tsx`
(ChatGPT, Claude, Claude Code, Gemini, Perplexity, Higgsfield). Grok, Poppy e Lovable
são os PNGs usados nos próprios Reels.

## Editar

```bash
# 1. mexer em _build/dados.json
# 2. gerar
python3 _build/gerar.py
# 3. publicar
vercel deploy --prod --yes
```

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
isso é texto real, mais o schema `Product` + `Offer` (R$ 47, BRL) e `FAQPage`. O quiz é a exceção
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

- **Medição desligada.** Ative "Web Analytics" no painel do projeto na Vercel e
  descomente a última linha de `gerar.py` (bloco `<!-- Medição ... -->`). Sem o toggle
  o script responde 404 e suja o console. A contagem básica de acessos já aparece no
  dashboard da Vercel mesmo sem isso.
- **Domínio próprio.** Hoje é `.vercel.app`. Um domínio pessoal dá mais confiança no
  direct.
- **Sem preço de ferramenta**, de propósito: nada foi verificado e preço de IA muda
  todo mês. Para incluir grátis/pago, conferir uma por uma antes.

## QA

`/private/tmp/.../scratchpad/qa-site.js` (efêmero) cobria 21 checagens: logos carregando,
links https com `rel="noopener"`, busca com e sem acento, filtro, estado vazio, ausência
de 404, console limpo, claro e escuro. Rodar contra a URL de produção com
`ALVO=https://qual-ia-abrir.vercel.app/`.

## Diagnóstico "Qual IA Usar?"

O quiz abre em **pop-up**, num `<dialog>` nativo (backdrop, Esc para fechar e prisão de foco vêm
do navegador, sem biblioteca). A seção `#diagnostico` ficou como chamada, com os 3 passos e o
botão; qualquer elemento com a classe `abre-diag` abre o modal, e o `href="#diagnostico"` segue
como destino se o JS não carregar.

São 5 perguntas (área, tarefa dominante, nível, orçamento, dispositivo). O motor soma pesos por
ferramenta e devolve 3 recomendações com a ordem de compra, o primeiro passo e um prompt pronto
de cada uma, mais o bloco "o que não assinar agora".

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
no topo de `gerar.py` (Web App do Apps Script gravando na planilha). Enquanto estiver vazia,
sai no lugar o convite pelo direct: formulário sem destino engole lead em silêncio, e o
`gerar.py` avisa isso no fim de cada execução.

## Medição

`Web Analytics` precisa do toggle no painel da Vercel. Com ele ligado, descomente a última
linha de `gerar.py`. Sem o toggle o script responde 404. Enquanto isso a página não mede
nada: o Reel de agosto levou 89 mil pessoas e não sobrou um único dado de acesso.

## Checkout

`CHECKOUT_URL` no topo de `gerar.py` liga os dois botões de compra (a seção `#oferta` e o fim do
diagnóstico). Vazia, ambos caem na lista de espera pelo direct e o build avisa. Preço e ancoragem
ficam em `dados.json` → `oferta.preco` e `oferta.de`, e alimentam também o schema `Offer`.
