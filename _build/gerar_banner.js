// Gera o banner do checkout da Cakto, desktop e mobile, a partir do dados.json.
//
// A peça segue a receita do corte do podcast da VTurb (Reel Dbvj9W6kW09), que é a única
// referência com número atrás: teste A/B só do banner, com a oferta empatando, e a
// conversão de checkout deles em 30 a 40%. Os seis elementos que eles dizem ser
// obrigatórios estão todos aqui, e cada um sai de um campo do dados.json:
//
//   1. preço visível no banner            oferta.preco, ancorado em oferta.de
//   2. mockup do produto, para verossimilhança   a tela real do /mapa, capturada aqui
//   3. promessa primária                  banner.promessa
//   4. a principal objeção quebrada       banner.objecao
//   5. acesso imediato                    banner.headline e banner.entrega
//   6. garantia                           banner.garantia (7 dias, que é a do produto,
//                                          não os 30 do mockup do vídeo)
//
// O mockup não é desenho: o script sobe as páginas geradas num servidor local, responde o
// quiz inteiro e fotografa o card da primeira ferramenta. Assim o que a pessoa vê no
// checkout é a tela que ela vai receber, e envelhece junto com o produto.
//
// O banner NÃO cita o mecanismo, de propósito: o mesmo arquivo sobe nos quatro produtos do
// teste de nome, e "Regra das 3 IAs" num checkout de "Método das 3 Abas" contradiria quem
// comprou. Mesma razão do diagnostico.crencaCurta.
//
// Uso:  cd ~/.claude/skills/playwright-skill && node run.js <caminho>/_build/gerar_banner.js
// Saída: _private/checkout/banner-desktop.png, banner-mobile.png e mockup.png
//
// Antes de rodar: python3 _build/gerar_mapa.py, que é quem escreve o _private/mapa.html.

import { createRequire } from 'node:module';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// O playwright não é dependência do projeto: ele vive na skill, que é de onde este script
// roda. O createRequire resolve a partir do cwd da skill, igual ao que o regressao.js faz.
const { chromium } = createRequire(path.join(process.cwd(), 'x.js'))('playwright');

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(AQUI, '..');
const PUBLICO = path.join(RAIZ, 'public');
const MAPA = path.join(RAIZ, '_private', 'mapa.html');
const SAIDA = path.join(RAIZ, '_private', 'checkout');
const PORTA = 8899;

const dados = JSON.parse(fs.readFileSync(path.join(AQUI, 'dados.json'), 'utf8'));
const { oferta, banner } = dados;

const TIPOS = {
  '.html': 'text/html; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.webp': 'image/webp', '.css': 'text/css', '.js': 'text/javascript',
};

// Servidor mínimo só para o mapa enxergar /logos: os logos entram por caminho absoluto,
// então file:// devolveria imagem quebrada e o mockup perderia justamente o que o torna
// reconhecível.
function servir() {
  return new Promise(resolve => {
    const s = http.createServer((req, res) => {
      const url = req.url.split('?')[0];
      const arquivo = url === '/_mapa' ? MAPA : path.join(PUBLICO, url);
      if (!arquivo.startsWith(PUBLICO) && arquivo !== MAPA) return res.writeHead(403).end();
      fs.readFile(arquivo, (erro, corpo) => {
        if (erro) return res.writeHead(404).end();
        res.writeHead(200, { 'Content-Type': TIPOS[path.extname(arquivo)] || 'application/octet-stream' });
        res.end(corpo);
      });
    });
    s.listen(PORTA, () => resolve(s));
  });
}

async function capturarMockup(browser) {
  const c = await browser.newContext({ viewport: { width: 1400, height: 860 }, deviceScaleFactor: 2 });
  const p = await c.newPage();
  await p.goto(`http://localhost:${PORTA}/_mapa`, { waitUntil: 'networkidle' });

  // Responde o quiz sempre pela primeira opção: qualquer stack serve de mockup, e a
  // primeira opção é a única escolha estável entre trilhas de tamanhos diferentes.
  for (let i = 0; i < 40; i++) {
    const passo = p.locator('#quiz .passo:not([hidden])');
    if (!(await passo.count())) break;
    const opcao = passo.locator('.opc').first();
    if (!(await opcao.isVisible().catch(() => false))) break;
    await opcao.click();
    await p.waitForTimeout(80);
  }
  await p.waitForTimeout(1500);

  const pular = p.locator('#oto-pular');
  if ((await pular.count()) && (await pular.isVisible().catch(() => false))) {
    await pular.click();
    await p.waitForTimeout(1200);
  }

  const card = p.locator('#res-stack > li').first();
  if (!(await card.count())) throw new Error('a stack não renderizou: o mockup ficaria vazio');
  const arquivo = path.join(SAIDA, 'mockup.png');
  await card.screenshot({ path: arquivo });
  await c.close();
  return arquivo;
}

const b64 = arquivo => fs.readFileSync(arquivo).toString('base64');
const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// Duas peças, um HTML. O que muda entre desktop e mobile é o eixo: deitado, o mockup fica
// ao lado do texto; em pé, ele vira o topo. A ordem de leitura é a mesma nos dois, porque a
// receita é uma ordem, não uma diagramação.
function html(mockup, deitado) {
  const L = deitado
    ? { largura: 820, altura: 300, h1: 29, promessa: 15, preco: 50, objecao: 13.5 }
    : { largura: 540, altura: 606, h1: 29, promessa: 15.5, preco: 52, objecao: 13.5 };

  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: ${L.largura}px; height: ${L.altura}px; overflow: hidden;
    font-family: Poppins, system-ui, sans-serif; color: #fff;
    background: #0c0a10;
    display: flex; flex-direction: column;
  }
  /* A luz roxa é a mesma da LP: quem vem de lá tem que reconhecer o produto no checkout. */
  .luz {
    position: absolute; inset: 0; pointer-events: none;
    background:
      radial-gradient(60% 90% at 12% 0%, rgba(193, 131, 251, .20), transparent 65%),
      radial-gradient(50% 80% at 95% 100%, rgba(226, 123, 183, .16), transparent 60%);
  }
  .corpo {
    position: relative; flex: 1; min-height: 0;
    display: flex; flex-direction: ${deitado ? 'row' : 'column'}; align-items: stretch;
  }

  .visual {
    position: relative; flex: none;
    ${deitado ? 'width: 296px; padding: 18px 0 16px 24px;' : 'height: 272px; padding: 16px 26px 0;'}
    display: flex; flex-direction: column; gap: 10px; align-items: center;
  }
  .janela {
    width: 100%; flex: 1; min-height: 0; border-radius: 11px; overflow: hidden;
    background: #14111c; border: 1px solid rgba(255, 255, 255, .10);
    box-shadow: 0 16px 40px rgba(0, 0, 0, .55);
    display: flex; flex-direction: column;
  }
  .barra {
    height: 19px; flex: none; display: flex; align-items: center; gap: 5px;
    padding: 0 9px; background: #1c1826; border-bottom: 1px solid rgba(255, 255, 255, .07);
  }
  .barra i { width: 6px; height: 6px; border-radius: 50%; background: rgba(255, 255, 255, .22); }
  .janela img { width: 100%; flex: 1; min-height: 0; object-fit: cover; object-position: top center; display: block; }
  .selo {
    flex: none; display: flex; align-items: center; gap: 6px;
    padding: 6px 12px; border-radius: 999px;
    background: rgba(12, 10, 16, .94); border: 1px solid rgba(193, 131, 251, .55);
    font-size: 11.5px; font-weight: 600; white-space: nowrap;
  }
  .selo svg { width: 13px; height: 13px; flex: none; }

  .texto {
    flex: 1; min-width: 0; min-height: 0;
    display: flex; flex-direction: column; justify-content: center;
    gap: ${deitado ? '9px' : '11px'};
    padding: ${deitado ? '18px 26px' : '14px 28px 18px'};
    ${deitado ? '' : 'text-align: center; align-items: center;'}
  }
  h1 {
    font-size: ${L.h1}px; font-weight: 800; line-height: 1.1; letter-spacing: -.02em;
    text-transform: uppercase;
  }
  h1 b {
    font-weight: 800;
    background: linear-gradient(92deg, #c183fb, #e27bb7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .promessa { font-size: ${L.promessa}px; line-height: 1.4; color: rgba(255, 255, 255, .82); }
  .objecao {
    display: inline-flex; align-items: center; gap: 7px; align-self: ${deitado ? 'flex-start' : 'center'};
    padding: 6px 13px; border-radius: 8px; max-width: 100%;
    background: rgba(193, 131, 251, .12); border: 1px solid rgba(193, 131, 251, .40);
    font-size: ${L.objecao}px; font-weight: 600; color: #e9d5ff;
  }
  .objecao svg { width: 14px; height: 14px; flex: none; }

  .preco { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; ${deitado ? '' : 'justify-content: center;'} }
  .preco .de { font-size: 15px; color: rgba(255, 255, 255, .42); text-decoration: line-through; }
  .preco .apenas { font-size: 10.5px; font-weight: 700; letter-spacing: .12em; color: rgba(255, 255, 255, .55); }
  .preco .valor {
    font-size: ${L.preco}px; font-weight: 800; line-height: 1; letter-spacing: -.03em;
    background: linear-gradient(92deg, #c183fb, #e27bb7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .preco .valor small { font-size: .5em; font-weight: 700; }
  .reforcos { display: flex; gap: 13px; flex-wrap: wrap; font-size: 12px; color: rgba(255, 255, 255, .58); ${deitado ? '' : 'justify-content: center;'} }
  .reforcos span { display: flex; align-items: center; gap: 5px; }
  .reforcos i { width: 3px; height: 3px; border-radius: 50%; background: #c183fb; flex: none; }

  .entrega {
    flex: none; display: flex; align-items: center; justify-content: center; gap: 8px;
    padding: 10px 18px; font-size: ${deitado ? 13 : 13.5}px; font-weight: 600; line-height: 1.3;
    color: #0c0a10; background: linear-gradient(92deg, #c183fb, #e27bb7); text-align: center;
  }
  .entrega svg { width: 15px; height: 15px; flex: none; }
</style></head>
<body>
  <div class="corpo">
    <div class="luz"></div>
    <div class="visual">
      <div class="janela">
        <div class="barra"><i></i><i></i><i></i></div>
        <img src="data:image/png;base64,${b64(mockup)}" alt="">
      </div>
      <div class="selo">
        <svg viewBox="0 0 24 24" fill="none" stroke="#c183fb" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
        ${esc(banner.garantia)}
      </div>
    </div>

    <div class="texto">
      <h1>${esc(banner.headline).replace(/^(ACESSO IMEDIATO)/, '<b>$1</b>')}</h1>
      <p class="promessa">${esc(banner.promessa)}</p>
      <span class="objecao">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
        ${esc(banner.objecao)}
      </span>
      <div class="preco">
        <span class="de">De R$ ${esc(oferta.de)}</span>
        <span class="apenas">POR APENAS</span>
        <span class="valor"><small>R$</small> ${esc(oferta.preco)}</span>
      </div>
      <div class="reforcos">${banner.reforcos.map(r => `<span><i></i>${esc(r)}</span>`).join('')}</div>
    </div>
  </div>

  <div class="entrega">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>
    ${esc(banner.entrega)}
  </div>
</body></html>`;
}

async function renderizar(browser, mockup, deitado, arquivo) {
  const largura = deitado ? 820 : 540;
  const altura = deitado ? 300 : 606;
  const c = await browser.newContext({ viewport: { width: largura, height: altura }, deviceScaleFactor: 2 });
  const p = await c.newPage();
  await p.setContent(html(mockup, deitado), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.screenshot({ path: arquivo });
  await c.close();
  return `${largura * 2}x${altura * 2}`;
}

(async () => {
  if (!fs.existsSync(MAPA)) throw new Error('rode python3 _build/gerar_mapa.py antes: falta o _private/mapa.html');
  fs.mkdirSync(SAIDA, { recursive: true });

  const servidor = await servir();
  const browser = await chromium.launch({ headless: true });
  try {
    const mockup = await capturarMockup(browser);
    console.log('mockup capturado do /mapa real:', path.relative(RAIZ, mockup));

    for (const [deitado, nome] of [[true, 'banner-desktop.png'], [false, 'banner-mobile.png']]) {
      const arquivo = path.join(SAIDA, nome);
      const tamanho = await renderizar(browser, mockup, deitado, arquivo);
      const kb = (fs.statSync(arquivo).size / 1024).toFixed(0);
      console.log(`gerado: _private/checkout/${nome}  ${tamanho}px  ${kb} KB`);
    }
    console.log(`preço R$ ${oferta.preco} ancorado em R$ ${oferta.de}, garantia de ${banner.garantia}`);
    console.log('sobe em Produtos > o produto > Checkout > ... > Personalizar, componente Imagem no topo');
  } finally {
    await browser.close();
    servidor.close();
  }
})();
