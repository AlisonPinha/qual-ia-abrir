// Memória do diagnóstico e envio anônimo. Compartilhado pelo site e pela entrega paga.
//
// Memória: as respostas ficam no navegador para o comprador não ter que refazer o
// diagnóstico dentro do /mapa. Só vale no mesmo aparelho; em outro, o mapa pergunta
// de novo, que é o comportamento normal.
//
// Anônimo: nem nome nem WhatsApp saem daqui. Só o que foi respondido e o que o motor
// recomendou, para saber qual perfil responde e onde as pessoas abandonam.

const SESSAO_CHAVE = "qia:resp";
const SESSAO_DIAS = 30;

// Assinatura das opções de uma pergunta. Sem isto, uma resposta guardada com o
// questionário antigo continuaria "válida" depois de a gente inserir uma opção nova, e o
// índice 0 do orçamento, que era "Até R$ 150", passaria a significar "só o que é grátis".
function assinaturaPergunta(rotulos) {
  let h = 5381;
  for (const r of rotulos) for (let i = 0; i < r.length; i++) h = ((h * 33) ^ r.charCodeAt(i)) >>> 0;
  return h;
}

function salvarSessao(resp, pids, livre, MOTOR) {
  try {
    const sig = {};
    if (MOTOR) for (const pid of Object.keys(resp))
      if (MOTOR.rotulos[pid]) sig[pid] = assinaturaPergunta(MOTOR.rotulos[pid]);
    localStorage.setItem(SESSAO_CHAVE, JSON.stringify({
      v: 2, resp, pids, livre: livre || {}, sig, ts: Date.now()
    }));
  } catch (e) { /* modo privado ou storage cheio: seguir sem memória */ }
}

// Devolve as respostas salvas apenas se cobrirem TODAS as perguntas desta página.
// Se o questionário mudou desde a última visita, ignora e deixa refazer: melhor
// perguntar de novo do que montar a stack com pergunta que não existe mais.
// `exigidos` é função porque, com trilha por área, quais perguntas são obrigatórias
// depende das próprias respostas salvas.
// Devolve o que dá para aproveitar, não tudo ou nada. Quando o questionário muda, quem já
// respondeu completa só o que falta em vez de recomeçar: na primeira venda, a compradora
// refez as 23 etapas por causa disso, e depois refaria de novo a cada mudança nossa.
// `completa` diz se as respostas cobrem tudo o que o motor exige agora.
function lerSessao(exigidos, MOTOR) {
  try {
    const bruto = localStorage.getItem(SESSAO_CHAVE);
    if (!bruto) return null;
    const d = JSON.parse(bruto);
    if (d.v !== 1 && d.v !== 2) return null;
    if (Date.now() - d.ts > SESSAO_DIAS * 864e5) return null;

    const resp = {};
    for (const [pid, i] of Object.entries(d.resp || {})) {
      const rotulos = MOTOR && MOTOR.rotulos[pid];
      if (!rotulos) continue;                       // pergunta que não existe mais
      if (!Number.isInteger(i) || i >= rotulos.length) continue;
      // sem assinatura (memória da versão 1) as opções podem ter mudado por baixo:
      // só aproveita o que ainda bate exatamente
      if (d.v === 2 && d.sig && d.sig[pid] !== assinaturaPergunta(rotulos)) continue;
      // memória sem assinatura: aproveita tudo, menos as perguntas que a gente sabe que
      // tiveram as opções mexidas desde então
      if (d.v === 1 && (MOTOR.mudaram || []).includes(pid)) continue;
      resp[pid] = i;
    }
    if (!Object.keys(resp).length) return null;
    return { resp, livre: d.livre || {}, completa: exigidos(resp).every(p => p in resp) };
  } catch (e) { return null; }
}

function limparSessao() {
  try { localStorage.removeItem(SESSAO_CHAVE); } catch (e) {}
}

// Origem do tráfego: o que veio na URL, guardado para a compra que acontece dias
// depois não aparecer como direta. Last touch: parâmetro novo passa a valer.
const ORIGEM_CHAVE = "qia:org";

function origemTrafego() {
  const agora = location.search.slice(1);
  try {
    if (agora) localStorage.setItem(ORIGEM_CHAVE, agora);
    return agora || localStorage.getItem(ORIGEM_CHAVE) || "";
  } catch (e) { return agora; }        // modo privado: vale só a visita atual
}

// Envio anônimo. no-cors porque o Apps Script não devolve cabeçalho de CORS:
// o que importa é gravar, não ler a resposta. Falha em silêncio de propósito,
// porque analytics não pode quebrar a entrega.
function enviarAnalitico(url, origem, MOTOR, resp, stack, corta, livre) {
  if (!url) return;
  try {
    const respostas = {};
    for (const [q, i] of Object.entries(resp)) {
      if (q.startsWith("break")) continue;          // o break não é resposta
      respostas[q] = MOTOR.rotulos[q][i];
    }
    fetch(url, {
      method: "POST",
      mode: "no-cors",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify({
        tipo: "diagnostico",
        origem,                                      // "site" ou "mapa"
        utm: origemTrafego(),                        // de onde a pessoa veio
        respostas,
        // o que a pessoa escreveu quando nenhuma opção era a dela: é o que diz
        // qual tarefa está faltando no quiz
        descreveu: Object.values(livre || {}).join(" | "),
        stack: stack.map(s => s.nome),
        cortar: corta,
        ts: new Date().toISOString()
      })
    }).catch(() => {});
  } catch (e) { /* nunca atrapalhar o resultado */ }
}
