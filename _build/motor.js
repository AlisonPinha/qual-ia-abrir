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

// Trocar uma resposta pode derrubar as que dependiam dela: quem responde "Conteúdo",
// anda cinco perguntas da trilha e volta para marcar "Jurídico" deixaria cinco respostas
// órfãs, e a stack sairia calculada com pergunta que a pessoa não viu. Roda em laço porque
// apagar uma pode invalidar outra.
function limparOrfas(MOTOR, resp) {
  for (let volta = 0; volta < 20; volta++) {
    let mudou = false;
    for (const pid of Object.keys(resp))
      if (!valePergunta(MOTOR, pid, resp)) { delete resp[pid]; mudou = true; }
    if (!mudou) return;
  }
}

function calcularStack(MOTOR, resp) {
  const pontos = {};
  for (const [q, i] of Object.entries(resp))
    for (const [ferr, p] of Object.entries(MOTOR.pesos[q][i] || {}))
      pontos[ferr] = (pontos[ferr] || 0) + p;

  // no celular não adianta mandar assinar o que só roda no computador
  const [qCel, iCel] = MOTOR.celular;
  const noCelular = resp[qCel] === iCel;
  const soNoComputador = n => noCelular && MOTOR.semCelular.includes(n);
  for (const n of MOTOR.semCelular) if (noCelular) delete pontos[n];

  // O orçamento declarado tira da mesa o que não cabe nele. Teto -1 é "só o que tem
  // camada gratuita de verdade". Mandar assinar R$ 254 por mês a quem acabou de dizer
  // que tem R$ 150 é recomendação que ninguém executa, e o mapa perde a autoridade.
  const iOrc = resp[MOTOR.perfil[1]] ?? 1;
  const teto = MOTOR.teto[iOrc];
  const cabeNoBolso = n => teto < 0 ? MOTOR.ferramentas[n].free : MOTOR.ferramentas[n].faixa <= teto;
  for (const n of Object.keys(pontos)) if (!cabeNoBolso(n)) delete pontos[n];

  const ranking = Object.entries(pontos).sort((a, b) => b[1] - a[1]);
  const top = ranking.slice(0, 3).map(([n]) => n);

  // A promessa é de três. Quando o filtro do bolso ou do aparelho tira gente demais,
  // completa na ordem do catálogo, que começa pelas generalistas: entregar duas
  // ferramentas a quem comprou um mapa de três é quebrar o produto para consertar o motor.
  const elegivel = n => cabeNoBolso(n) && !soNoComputador(n);
  // Especialista antes de generalista: quem paga por um mapa não paga para ouvir
  // "usa ChatGPT e Claude". Quando o bolso é curto, quem entra são as especialistas
  // que resolvem de graça o que generalista nenhuma faz: slide, voz, automação, fonte.
  const fallback = Object.keys(MOTOR.ferramentas)
    .filter(n => !top.includes(n) && elegivel(n))
    .sort((a, b) => (MOTOR.ferramentas[a].generalista ? 1 : 0) - (MOTOR.ferramentas[b].generalista ? 1 : 0));
  for (const n of fallback) {
    if (top.length >= 3) break;
    top.push(n);
  }

  // quantas entram já, conforme o orçamento declarado
  let cabem = MOTOR.cabem[iOrc];
  // quem prefere dominar uma a fundo não recebe três para abrir na mesma semana
  const [qFoco, iFoco] = MOTOR.foco;
  if (resp[qFoco] === iFoco) cabem = Math.min(cabem, 1);
  const stack = top.map((n, i) => {
    const f = MOTOR.ferramentas[n];
    // quem declarou que não vai pagar nada precisa da porta de entrada gratuita da
    // ferramenta certa, não de uma data para assinar
    const pelaGratuita = teto < 0 && f.free && f.faixa !== 0;
    return {
      nome: n,
      // "assina agora" numa ferramenta grátis derruba a credibilidade do mapa inteiro
      quando: f.faixa === 0 ? MOTOR.gratis
        : pelaGratuita ? MOTOR.gratisPlano
        : MOTOR.ordem[i < cabem ? 0 : (i === cabem ? 1 : 2)],
      ...f,
      // dizer "plano grátis" ao lado de "R$ 104/mês" se contradiz na mesma linha
      // o teaser já disse "de graça": aqui vai o que custa se ela quiser mais, que é
      // a promessa de custo real do produto
      ...(pelaGratuita ? { curto: MOTOR.curtoGratis.replace("{custo}", f.curto) } : {})
    };
  });

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
    .filter(n => !soNoComputador(n))
    .sort((a, b) => (MOTOR.ferramentas[b].faixa - MOTOR.ferramentas[a].faixa)
                 || ((pontos[a] || 0) - (pontos[b] || 0)))
    .slice(0, 3);

  return { stack, corta };
}
