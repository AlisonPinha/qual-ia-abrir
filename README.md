# Qual IA abrir

Entregável do Reel `Db37tHWCLMV` (@aalisonaraujo): 24 tarefas do dia a dia com a
ferramenta de IA certa para cada uma, o porquê da escolha e o link de todas.

Página estática de arquivo único. Sem build, sem dependência.

- `public/index.html` — a página inteira (HTML + CSS + JS inline)
- `public/logos/` — ícones das ferramentas, mesmo estilo squircle dos Reels.
  Os SVGs são gerados a partir dos paths de `reels-ferramentas-ia/src/AppIcon.tsx`;
  Grok, Poppy e Lovable são os PNGs usados nos próprios Reels.
- `public/og.png` — preview de compartilhamento, gerado de `_build/og-fonte.html`
  via Playwright em 1200x630.

## Editar a lista

Tudo vive nas constantes `F` (ferramentas, com link) e `DADOS` (tarefas) no
`<script>` do fim do `index.html`. Mexeu, `vercel --prod` e está no ar.

## Regerar a OG

```bash
cd ~/.claude/skills/playwright-skill
node run.js "const b=await chromium.launch();const p=await(await b.newContext({viewport:{width:1200,height:630}})).newPage();await p.goto('file:///Users/alisonaraujo/Projetos/qual-ia-abrir/_build/og-fonte.html');await p.waitForTimeout(600);await p.screenshot({path:'/Users/alisonaraujo/Projetos/qual-ia-abrir/public/og.png'});await b.close()"
```

Atenção: `og-fonte.html` referencia `logos/` por caminho relativo. Se movê-lo,
corrigir os caminhos ou os logos somem da imagem.
