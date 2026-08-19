// Cálculo da stack. Injetado nas duas páginas (index e mapa) para que a versão
// paga nunca devolva um resultado diferente do que o teaser mostrou.
// Recebe o dicionário MOTOR e as respostas; não toca no DOM.

// Trilha por área: a pergunta com regra só existe para quem respondeu aquela
// área. Sem regra em MOTOR.se, a pergunta é do tronco e vale para todo mundo.
function valePergunta(MOTOR, pid, resp) {
  const se = MOTOR.se[pid];
  return !se || Object.entries(se).every(([q, valores]) => valores.includes(resp[q]));
}

// As perguntas que esta pessoa precisa ter respondido, dadas as respostas dela.
function pidsExigidos(MOTOR, resp) {
  return MOTOR.pids.filter(pid => valePergunta(MOTOR, pid, resp));
}

function calcularStack(MOTOR, resp) {
  const pontos = {};
  for (const [q, i] of Object.entries(resp))
    for (const [ferr, p] of Object.entries(MOTOR.pesos[q][i] || {}))
      pontos[ferr] = (pontos[ferr] || 0) + p;

  // no celular o Claude Code não roda: é terminal, não chat
  const [qCel, iCel] = MOTOR.celular;
  const noCelular = resp[qCel] === iCel;
  if (noCelular) delete pontos["Claude Code"];

  const ranking = Object.entries(pontos).sort((a, b) => b[1] - a[1]);
  const top = ranking.slice(0, 3).map(([n]) => n);

  // quantas entram já, conforme o orçamento declarado
  const cabem = MOTOR.cabem[resp[MOTOR.perfil[1]] ?? 0];
  const stack = top.map((n, i) => ({
    nome: n,
    // "assina agora" numa ferramenta grátis derruba a credibilidade do mapa inteiro
    quando: MOTOR.ferramentas[n].faixa === 0
      ? MOTOR.gratis
      : MOTOR.ordem[i < cabem ? 0 : (i === cabem ? 1 : 2)],
    ...MOTOR.ferramentas[n]
  }));

  // Claude Code vem dentro do plano do Claude: uma assinatura só, um momento só
  const cc = stack.find(s => s.nome === "Claude Code");
  const cl = stack.find(s => s.nome === "Claude");
  if (cc && cl) {
    const antes = MOTOR.ordem.indexOf(cc.quando) <= MOTOR.ordem.indexOf(cl.quando) ? cc.quando : cl.quando;
    cc.quando = cl.quando = antes;
  }

  // o corte: o que a pessoa provavelmente ia assinar por hype e não precisa agora
  const corta = Object.keys(MOTOR.ferramentas)
    .filter(n => !top.includes(n))
    .filter(n => !(noCelular && n === "Claude Code"))
    .sort((a, b) => (MOTOR.ferramentas[b].faixa - MOTOR.ferramentas[a].faixa)
                 || ((pontos[a] || 0) - (pontos[b] || 0)))
    .slice(0, 3);

  return { stack, corta };
}
