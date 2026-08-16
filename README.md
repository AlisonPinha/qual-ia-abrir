# Qual IA abrir

**No ar:** https://qual-ia-abrir.vercel.app

Entregável do Reel `Db37tHWCLMV` (@aalisonaraujo, 10/08/2026): 24 tarefas do dia a dia
com a ferramenta de IA certa para cada uma, o porquê da escolha e o link de todas.
Busca instantânea e filtro por ferramenta.

Site estático, sem framework e sem dependência de runtime. Um passo de geração em
Python transforma os dados em HTML.

## Estrutura

| Caminho | O que é |
|---|---|
| `_build/dados.json` | **Fonte única.** Ferramentas (logo, link, descrição), tarefas, desempates |
| `_build/gerar.py` | Gera `public/index.html` a partir do JSON e do CSS |
| `_build/estilo.css` | Todo o CSS. Editar aqui, nunca no HTML gerado |
| `_build/og-fonte.html` | Página 1200x630 que vira a imagem de preview |
| `public/index.html` | **Gerado. Não editar à mão**, `gerar.py` sobrescreve |
| `public/logos/` | Ícones no mesmo squircle dos Reels |
| `public/og.png` | Preview de compartilhamento |

Os SVGs de logo saem dos paths de `~/Projetos/reels-ferramentas-ia/src/AppIcon.tsx`
(ChatGPT, Claude, Claude Code, Gemini, Perplexity, Higgsfield). Grok, Poppy e Lovable
são os PNGs usados nos próprios Reels.

## Editar a lista

```bash
# 1. mexer em _build/dados.json
# 2. gerar
python3 _build/gerar.py
# 3. publicar
vercel deploy --prod --yes
```

## Por que existe um passo de geração

A primeira versão montava a lista por JavaScript no navegador. Resultado: o robô do
Google, o gerador de preview do WhatsApp e leitores de tela recebiam a página vazia,
porque nenhum deles executa o script. Medido com um leitor externo: ele não conseguia
citar uma ferramenta sequer.

Agora `gerar.py` escreve as 24 tarefas direto no HTML e o JavaScript só liga a busca e
o filtro sobre o que já está lá. **Com JS desligado: 24 tarefas, 9 cards, 4.606
caracteres de texto legível.** Antes: zero.

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
