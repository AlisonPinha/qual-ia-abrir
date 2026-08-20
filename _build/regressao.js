// Regressão do Qual IA Usar. Roda a bateria inteira contra produção e devolve um relatório.
//
// Uso: cd ~/.claude/skills/playwright-skill && node run.js _build/regressao.js
//
// Cobre: quiz da LP, teaser em silhueta, código do diagnóstico, botão do WhatsApp, bloqueio
// do checkout antes do quiz, checkout com UTM + sck, paywall, pós-compra e entrega com IA,
// CTA de ascensão, formulário do presente, respostas em outro aparelho, memória parcial e
// a /plano inteira, incluindo o material rodado.
//
// Custo por rodada: 1 chamada ao /api/mapa e 3 ao /api/plano. Os limites por IP são 6 e
// 6/6/5 por hora, então dá para rodar umas duas vezes seguidas, não mais.
const { chromium } = require('playwright');

const BASE = 'https://diagnostico.noahai.com.br';
const CHECKOUT_UPSELL = 'pay.cakto.com.br/j79id6y_1051180';
// Valor do cookie qia_sessao de uma conta interna com entitlement plano. Nunca commitar.
// Sem ele a bateria valida toda a parte pública e o bloqueio, depois para antes da entrega.
const SESSAO = process.env.QIA_SESSION_COOKIE || '';
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
  const contexto = async viewport => {
    const c = await browser.newContext({ viewport });
    if (SESSAO) await c.addCookies([{
      name: 'qia_sessao', value: SESSAO, domain: 'diagnostico.noahai.com.br', path: '/',
      httpOnly: true, secure: true, sameSite: 'Lax',
    }]);
    return c;
  };

  // ---------- 1. LP: quiz, teaser, código, checkout ----------
  const c1 = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const p1 = await c1.newPage();
  p1.on('pageerror', e => erros.push('LP: ' + e.message));
  await p1.goto(BASE + '/?utm_source=regressao&desconto_antigo=IGNORAR', { waitUntil: 'domcontentloaded' });
  const paginasAntes = c1.pages().length;
  await p1.locator('#oferta a[href*="pay.cakto"]').click();
  await p1.waitForTimeout(400);
  const antesDoQuiz = await p1.evaluate(() => ({
    modal: document.getElementById('modal')?.open === true,
    checkout: document.querySelector('#oferta a[href*="pay.cakto"]')?.href || '',
  }));
  ok('LP: comprar antes do diagnóstico abre o quiz', antesDoQuiz.modal
     && c1.pages().length === paginasAntes && !/[?&]sck=/.test(antesDoQuiz.checkout));
  const cliques = await responderTudo(p1, '#modal');
  await p1.waitForTimeout(900);
  const lp = await p1.evaluate(() => ({
    titulo: document.getElementById('res-titulo')?.textContent?.trim(),
    codigoNaOferta: !!document.getElementById('res-codigo'),
    checkout: document.querySelector('a[href*="pay.cakto"]')?.href || '',
    ctaOferta: document.querySelector('#oferta a[href*="pay.cakto"]')?.textContent?.trim() || '',
    silhueta: document.querySelectorAll('#res-stack .oculto').length,
  }));
  ok('LP: quiz completa', cliques >= 14, `${cliques} cliques`);
  ok('LP: resultado aparece', /stack/i.test(lp.titulo || ''), lp.titulo);
  ok('LP: teaser em silhueta', lp.silhueta === 3, `${lp.silhueta} cards ocultos`);
  ok('LP: CTA de preço vira compra depois do diagnóstico', /^Quero a minha stack/.test(lp.ctaOferta), lp.ctaOferta);
  // o código ao lado do preço convidava a adiar a compra: ele só aparece para quem sai
  ok('LP: código fora da oferta', lp.codigoNaOferta === false);
  const checkoutLp = new URL(lp.checkout);
  ok('LP: checkout leva UTM e diagnóstico no sck', checkoutLp.searchParams.get('utm_source') === 'regressao'
     && /^qia2_.{8,}\.[A-Za-z0-9_-]{20,}$/.test(checkoutLp.searchParams.get('sck') || ''));
  ok('LP: parâmetro estranho não viaja ao checkout', !checkoutLp.searchParams.has('desconto_antigo'));

  // ---------- 2. saída: a retenção guarda as respostas, não o acesso pago ----------
  const c2 = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const p2 = await c2.newPage();
  p2.on('pageerror', e => erros.push('saída: ' + e.message));
  await p2.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  await p2.locator('.abre-diag').first().click();
  await p2.waitForTimeout(400);
  // quem sai no meio não tem código, porque o código é o quiz inteiro codificado
  for (let i = 0; i < 3; i++) { await p2.locator('#modal .passo:not([hidden]) .opc').first().click(); await p2.waitForTimeout(110); }
  await p2.goBack();
  await p2.waitForTimeout(400);
  const meio = await p2.evaluate(() => ({
    retencao: !document.getElementById('retencao').hidden,
    codigo: !document.getElementById('ret-codigo').hidden,
  }));
  ok('saída no meio: retenção aparece', meio.retencao === true);
  ok('saída no meio: sem código para guardar', meio.codigo === false);

  // com o quiz inteiro respondido, a mesma tela entrega o código
  await p2.locator('#retencao-fica').click();
  await responderTudo(p2, '#modal');
  await p2.waitForTimeout(900);
  await p2.goBack();
  await p2.waitForTimeout(400);
  const fim = await p2.evaluate(() => ({
    titulo: document.getElementById('retencao-titulo')?.textContent || '',
    passo1: !!document.getElementById('ret-passo1')?.offsetParent,
    codigo: !!document.getElementById('ret-codigo')?.offsetParent,
  }));
  ok('saída com quiz pronto: tela 1 aparece', fim.passo1 === true);
  ok('saída: fala de diagnóstico pronto', /pronto/i.test(fim.titulo), fim.titulo);
  ok('saída: código não sai antes do contato', fim.codigo === false);

  // confirmar a saída abre o pedido de WhatsApp. A bateria PARA aqui de propósito: clicar
  // em "Me manda no WhatsApp" gravaria um lead de teste na planilha de verdade
  await p2.locator('#retencao-sai').click();
  await p2.waitForTimeout(300);
  const contato = await p2.evaluate(() => ({
    passo2: !!document.getElementById('ret-passo2')?.offsetParent,
    href: document.getElementById('saida-enviar')?.href || '',
    campos: !!document.getElementById('saida-nome') && !!document.getElementById('saida-zap'),
  }));
  ok('saída: confirmar abre o pedido de contato', contato.passo2 === true && contato.campos === true);
  // o link tem que ser o da LP: /mapa é a entrega paga e exige uma sessão de comprador
  ok('saída: o link leva a LP, não a entrega', /wa\.me/.test(contato.href)
     && /\/\?c=/.test(decodeURIComponent(contato.href))
     && !/\/mapa/.test(decodeURIComponent(contato.href)), decodeURIComponent(contato.href).slice(0, 90));

  // e o link que ela guarda tem que cumprir o que promete: abrir no resultado dela
  const link = (decodeURIComponent(contato.href).match(/https?:\/\/[^\s]+/g) || []).pop() || '';
  const codigo = new URL(link).searchParams.get('c') || '';
  const c2b = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const p2b = await c2b.newPage();
  await p2b.goto(link, { waitUntil: 'domcontentloaded' });
  await p2b.waitForTimeout(1500);
  const volta = await p2b.evaluate(() => ({
    resultado: !document.getElementById('resultado')?.hidden,
    silhueta: document.querySelectorAll('#res-stack .oculto').length,
  }));
  ok('link guardado: abre no resultado, ainda em silhueta', volta.resultado === true && volta.silhueta === 3,
     `${volta.silhueta} ocultos`);

  // ---------- 2b. paywall ----------
  const semSessao = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const bloqueada = await semSessao.newPage();
  await bloqueada.goto(BASE + '/mapa', { waitUntil: 'domcontentloaded' });
  ok('paywall: /mapa sem sessão vai para /acesso', /\/acesso(?:\?|$)/.test(bloqueada.url()), bloqueada.url());
  await semSessao.close();
  if (!SESSAO) {
    console.log('\nParte pública concluída. Defina QIA_SESSION_COOKIE para testar as entregas pagas.');
    console.log('\n================ REGRESSÃO ================');
    for (const x of r) console.log(`${x.passou ? ' ok ' : 'FALHA'} | ${x.nome}${x.obs ? '  (' + x.obs + ')' : ''}`);
    const falhasPublicas = r.filter(x => !x.passou).length;
    console.log(`\n${r.length - falhasPublicas}/${r.length} passaram`);
    await browser.close();
    process.exit(falhasPublicas ? 1 : 0);
  }

  // ---------- 3. /mapa: entrega com IA ----------
  const c3 = await contexto({ width: 390, height: 844 });
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
  // O fim do stream é o aviso "escrevendo" sumir, não o último bloco passar de 50
  // caracteres. Medir por tamanho lê o CORTE pela metade, porque ele é o último a ser
  // preenchido: cinco personas rodadas em 20/08 vieram todas com ele cortado no meio da
  // frase, e a bateria dava 8/8 assim mesmo.
  const tMapa = await esperar(p3, () => {
    const aviso = document.getElementById('res-escrevendo');
    const corte = (document.getElementById('res-corta-ia')?.textContent || '').trim();
    return aviso && aviso.hidden && corte.length > 50;
  });
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
      // bloco que acaba no meio da frase conta como cheio se olhar só o tamanho. Prompt
      // pode terminar em colchete de instrução, então a régua vale para os de texto
      cortados: ['ABERTURA', 'PORQUE1', 'PORQUE2', 'PORQUE3', 'CORTE']
        .filter(k => b[k] && !/[.!?]$/.test(b[k].trim())),
      lacunas: vals.some(v => /\{[^}]+\}/.test(v)),
      // só o que marca quem fala: "ele roda sozinho" é a ferramenta, e acusar isso
      // como defeito faz a bateria mentir
      genero: /\beu mesm[oa]\b|\beu\b[^.]{0,14}\bsozinh[oa]\b|\bcansad[oa]\b/i.test(vals.join(' ')),
      codigo: document.getElementById('res-codigo-valor')?.textContent || '',
    };
  });
  ok('/mapa: 8 blocos escritos pela IA', mapa.cheios === 8, `${mapa.cheios}/8 em ${tMapa}s`);
  ok('/mapa: nenhum bloco cortado no meio da frase', mapa.cortados.length === 0,
     mapa.cortados.join(', '));
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
  const c4 = await contexto({ width: 1280, height: 900 });
  const p4 = await c4.newPage();
  p4.on('pageerror', e => erros.push('código: ' + e.message));
  await p4.goto(`${BASE}/mapa?c=${encodeURIComponent(codigo)}`, { waitUntil: 'domcontentloaded' });
  const entrou = await esperar(p4, () => document.getElementById('quiz')?.hidden === true, 30000);
  ok('sessão + código do diagnóstico abrem sem refazer', entrou !== null && !!codigo, codigo);

  // ---------- 5. memória parcial ----------
  const ANTIGA = { v: 1, ts: Date.now(), livre: {}, pids: [], resp: {
    area: 0, c_tarefa: 0, tempo_ia: 1, quantas: 2, gasto: 1, c_ideia: 1, c_voz: 2,
    generica: 0, parada: 1, refaz: 1, horas: 2, nivel: 1, prazo: 1, estilo: 0, orcamento: 1, onde: 1 } };
  const c5 = await contexto({ width: 390, height: 844 });
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
  const c6 = await contexto({ width: 390, height: 844 });
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
