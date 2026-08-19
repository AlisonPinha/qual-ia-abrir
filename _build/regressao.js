// Regressão do Qual IA Usar. Roda a bateria inteira contra produção e devolve um relatório.
//
// Uso: cd ~/.claude/skills/playwright-skill && node run.js _build/regressao.js
//
// Cobre: quiz da LP, teaser em silhueta, código de acesso, botão do WhatsApp, checkout com
// UTM, voltar com limpeza de trilha, tela pós-compra do upsell, entrega do /mapa com IA,
// CTA de ascensão, formulário do presente, acesso por código em outro aparelho, memória
// parcial e a /plano inteira, incluindo o material rodado.
//
// Custo por rodada: 1 chamada ao /api/mapa e 3 ao /api/plano. Os limites por IP são 6 e
// 6/6/5 por hora, então dá para rodar umas duas vezes seguidas, não mais.
const { chromium } = require('playwright');

const BASE = 'https://diagnostico.noahai.com.br';
const CHECKOUT_UPSELL = 'pay.cakto.com.br/j79id6y_1051180';
const r = [];
const ok = (nome, passou, obs = '') => r.push({ nome, passou, obs });

async function esperar(page, fn, limite = 150000) {
  const t0 = Date.now();
  while (Date.now() - t0 < limite) {
    if (await page.evaluate(fn)) return ((Date.now() - t0) / 1000).toFixed(0);
    await page.waitForTimeout(500);
  }
  return null;
}

async function responderTudo(page, escopo) {
  let n = 0;
  for (let i = 0; i < 40; i++) {
    const passo = page.locator(`${escopo} .passo:not([hidden])`);
    if (!(await passo.count())) break;
    const o = passo.locator('.opc').first();
    if (!(await o.isVisible().catch(() => false))) break;
    await o.click(); n++;
    await page.waitForTimeout(80);
  }
  return n;
}

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 15 });
  const erros = [];

  // ---------- 1. LP: quiz, teaser, código, checkout ----------
  const c1 = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const p1 = await c1.newPage();
  p1.on('pageerror', e => erros.push('LP: ' + e.message));
  await p1.goto(BASE + '/?utm_source=regressao', { waitUntil: 'domcontentloaded' });
  await p1.locator('.abre-diag').first().click();
  await p1.waitForTimeout(400);
  const cliques = await responderTudo(p1, '#modal');
  await p1.waitForTimeout(900);
  const lp = await p1.evaluate(() => ({
    titulo: document.getElementById('res-titulo')?.textContent?.trim(),
    codigo: document.getElementById('res-codigo-valor')?.textContent || '',
    zap: document.getElementById('res-codigo-zap')?.href || '',
    checkout: document.querySelector('a[href*="pay.cakto"]')?.href || '',
    silhueta: document.querySelectorAll('#res-stack .oculto').length,
  }));
  ok('LP: quiz completa', cliques >= 18, `${cliques} cliques`);
  ok('LP: resultado aparece', /stack/i.test(lp.titulo || ''), lp.titulo);
  ok('LP: teaser em silhueta', lp.silhueta === 3, `${lp.silhueta} cards ocultos`);
  ok('LP: código gerado', /^[0-9A-Z-]{8,}$/.test(lp.codigo), lp.codigo);
  ok('LP: botão do WhatsApp com link', /wa\.me/.test(lp.zap) && /mapa\?c=/.test(decodeURIComponent(lp.zap)));
  ok('LP: checkout leva UTM e código', /utm_source=regressao/.test(lp.checkout) && /[?&]c=/.test(lp.checkout));

  // ---------- 2. voltar e limpeza de trilha ----------
  const c2 = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const p2 = await c2.newPage();
  p2.on('pageerror', e => erros.push('voltar: ' + e.message));
  await p2.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  await p2.locator('.abre-diag').first().click();
  await p2.waitForTimeout(400);
  const escondidoNoInicio = await p2.evaluate(() => document.getElementById('quiz-voltar')?.hidden);
  for (let i = 0; i < 3; i++) { await p2.locator('#modal .passo:not([hidden]) .opc').first().click(); await p2.waitForTimeout(110); }
  for (let i = 0; i < 3; i++) { await p2.locator('#quiz-voltar').click(); await p2.waitForTimeout(130); }
  const voltouAoInicio = await p2.evaluate(() => document.querySelector('#modal .passo:not([hidden])')?.dataset.q);
  const nOpc = await p2.locator('#modal .passo:not([hidden]) .opc').count();
  await p2.locator('#modal .passo:not([hidden]) .opc').nth(nOpc - 1).click();
  await p2.waitForTimeout(200);
  const trilhaNova = await p2.evaluate(() => document.querySelector('#modal .passo:not([hidden])')?.dataset.q);
  ok('voltar: escondido na 1ª pergunta', escondidoNoInicio === true);
  ok('voltar: volta até o início', voltouAoInicio === 'area', voltouAoInicio);
  ok('voltar: trocar área troca a trilha', trilhaNova === 'tarefa', trilhaNova);

  // ---------- 3. /mapa: entrega com IA ----------
  const c3 = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const p3 = await c3.newPage();
  p3.on('pageerror', e => erros.push('mapa: ' + e.message));
  await p3.goto(BASE + '/mapa?utm_source=regressao', { waitUntil: 'domcontentloaded' });
  await responderTudo(p3, '#quiz');
  await p3.waitForTimeout(500);
  const oto = await p3.evaluate(() => {
    const el = id => document.getElementById(id);
    return {
      visivel: !!el('oto') && !el('oto').hidden,
      segurouOMapa: el('resultado').hidden,
      conta: [...document.querySelectorAll('.oto-conta span')].map(s => s.textContent.trim()).join(' | '),
      href: el('oto-comprar')?.href || '',
    };
  });
  ok('/mapa: tela pós-compra aparece antes do mapa', oto.visivel && oto.segurouOMapa);
  ok('/mapa: a conta do upsell bate', /R\$ 197/.test(oto.conta) && /- R\$ 67/.test(oto.conta)
     && /R\$ 130/.test(oto.conta), oto.conta);
  ok('/mapa: o botão leva ao checkout do upsell com UTM',
     oto.href.includes(CHECKOUT_UPSELL) && oto.href.includes('utm_source=regressao'), oto.href);
  await p3.locator('#oto-pular').click();
  await p3.waitForTimeout(300);
  ok('/mapa: um clique abre a entrega', await p3.evaluate(() => !document.getElementById('resultado').hidden));
  const tMapa = await esperar(p3, () => (document.getElementById('res-corta-ia')?.textContent || '').trim().length > 50);
  const mapa = await p3.evaluate(() => {
    const t = id => (document.getElementById(id)?.textContent || '').trim();
    const b = { ABERTURA: t('res-abertura'), CORTE: t('res-corta-ia') };
    for (let i = 0; i < 3; i++) {
      b['PORQUE' + (i + 1)] = (document.getElementById('porque' + i)?.querySelector('p')?.textContent || '').trim();
      b['PROMPT' + (i + 1)] = t('p' + i);
    }
    const vals = Object.values(b);
    return {
      cheios: vals.filter(v => v.length > 40).length,
      lacunas: vals.some(v => /\{[^}]+\}/.test(v)),
      genero: /\b(eu mesma|eu mesmo|sozinh[ao])\b/i.test(vals.join(' ')),
      codigo: document.getElementById('res-codigo-valor')?.textContent || '',
    };
  });
  ok('/mapa: 8 blocos escritos pela IA', mapa.cheios === 8, `${mapa.cheios}/8 em ${tMapa}s`);
  ok('/mapa: sem lacuna {}', !mapa.lacunas);
  if (mapa.genero) {
    const bruto = await p3.evaluate(() => [...document.querySelectorAll('#resultado')].map(n => n.textContent).join('\n'));
    require('fs').writeFileSync('/tmp/regressao-genero.txt', bruto);
    ok('/mapa: sem marca de gênero', false, 'texto salvo em /tmp/regressao-genero.txt');
  } else ok('/mapa: sem marca de gênero', true);
  ok('/mapa: mostra o código', mapa.codigo.length > 8, mapa.codigo);

  const fimDoMapa = await p3.evaluate(() => {
    const el = id => document.getElementById(id);
    const b = el('pres-enviar');
    return {
      asc: !!el('ascensao') && !el('ascensao').hidden,
      ascHref: el('ascensao')?.querySelector('a')?.href || '',
      ascPreco: (document.querySelector('.asc-preco')?.textContent || '').replace(/\s+/g, ' ').trim(),
      presente: !!el('presente') && !el('presente').hidden,
      opcoes: document.querySelectorAll('#pres-opcoes .opc').length,
      botaoApagado: !!b && b.disabled,
    };
  });
  ok('/mapa: CTA de ascensão no fim da entrega',
     fimDoMapa.asc && fimDoMapa.ascHref.includes(CHECKOUT_UPSELL) && /130/.test(fimDoMapa.ascPreco),
     fimDoMapa.ascPreco);
  // o voto não é enviado aqui de propósito: cada rodada viraria uma linha falsa na planilha
  ok('/mapa: formulário do presente pronto',
     fimDoMapa.presente && fimDoMapa.opcoes === 6 && fimDoMapa.botaoApagado,
     `${fimDoMapa.opcoes} opções`);

  // ---------- 4. código em outro aparelho ----------
  const c4 = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const p4 = await c4.newPage();
  p4.on('pageerror', e => erros.push('código: ' + e.message));
  await p4.goto(`${BASE}/mapa?c=${encodeURIComponent(lp.codigo)}`, { waitUntil: 'domcontentloaded' });
  const entrou = await esperar(p4, () => document.getElementById('quiz')?.hidden === true, 30000);
  ok('código na URL abre sem refazer', entrou !== null);

  // ---------- 5. memória parcial ----------
  const ANTIGA = { v: 1, ts: Date.now(), livre: {}, pids: [], resp: {
    area: 0, c_tarefa: 0, tempo_ia: 1, quantas: 2, gasto: 1, c_ideia: 1, c_voz: 2,
    generica: 0, parada: 1, refaz: 1, horas: 2, nivel: 1, prazo: 1, estilo: 0, orcamento: 1, onde: 1 } };
  const c5 = await browser.newContext({ viewport: { width: 390, height: 844 } });
  await c5.addInitScript(m => localStorage.setItem('qia:resp', JSON.stringify(m)), ANTIGA);
  const p5 = await c5.newPage();
  p5.on('pageerror', e => erros.push('parcial: ' + e.message));
  await p5.goto(BASE + '/mapa', { waitUntil: 'domcontentloaded' });
  await p5.waitForTimeout(1000);
  const avisoParcial = await p5.evaluate(() => !document.getElementById('completando-aviso')?.hidden);
  const faltaram = await responderTudo(p5, '#quiz');
  ok('memória parcial: avisa', avisoParcial);
  ok('memória parcial: pergunta só o que falta', faltaram <= 6, `${faltaram} passos (era 19+)`);

  // ---------- 6. /plano ----------
  const c6 = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const p6 = await c6.newPage();
  p6.on('pageerror', e => erros.push('plano: ' + e.message));
  await p6.goto(BASE + '/plano', { waitUntil: 'domcontentloaded' });
  await responderTudo(p6, '#quiz');
  const tDias = await esperar(p6, () => [...document.querySelectorAll('.dia-ia')].filter(d => d.textContent.trim().length > 40).length >= 7);
  const tCfg = await esperar(p6, () => [...document.querySelectorAll('.cfg-texto')].filter(x => !x.textContent.includes('escrito para o seu caso quando')).length >= 3);
  ok('/plano: 7 dias escritos', tDias !== null, tDias ? tDias + 's' : '');
  ok('/plano: 3 configurações escritas', tCfg !== null, tCfg ? tCfg + 's' : '');
  await p6.locator('#material').fill('Preciso responder este cliente que pediu orçamento de um projeto de 40 metros quadrados, com prazo de 20 dias e pagamento parcelado. Ele já pediu desconto duas vezes e some depois que eu mando o valor.');
  await p6.locator('#material-rodar').click();
  const tMat = await esperar(p6, () => (document.getElementById('material-saida')?.textContent || '').length > 300);
  ok('/plano: material volta rodado', tMat !== null, tMat ? tMat + 's' : '');

  // ---------- relatório ----------
  console.log('\n================ REGRESSÃO ================');
  for (const x of r) console.log(`${x.passou ? ' ok ' : 'FALHA'} | ${x.nome}${x.obs ? '  (' + x.obs + ')' : ''}`);
  const falhas = r.filter(x => !x.passou).length;
  console.log(`\n${r.length - falhas}/${r.length} passaram`);
  console.log('erros de página:', erros.join(' | ') || 'nenhum');
  await browser.close();
  process.exit(falhas ? 1 : 0);
})();
