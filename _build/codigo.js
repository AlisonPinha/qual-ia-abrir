// Código de acesso: as respostas viram um código curto que a pessoa digita em qualquer
// aparelho. Existe porque a memória do diagnóstico é do navegador, e na primeira venda de
// teste o comprador respondeu no celular, abriu o e-mail no computador e teve que refazer
// as 23 etapas. Quem pagou não pode trabalhar de novo.
//
// Sem banco e sem depender da plataforma de pagamento: o código É o dado. Cada resposta
// cabe em 4 bits (a pergunta de área tem 10 opções, então 3 bits não bastam), e 19
// respostas viram uns 16 caracteres. A ordem é a que o próprio motor exige, e a trilha se resolve sozinha na
// leitura: a área vem primeiro e decide quais perguntas vêm depois.

const ALFABETO = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ";   // sem 0/O e 1/I, que a pessoa confunde
const BITS_POR_RESPOSTA = 4;   // 16 opções por pergunta; a de área já usa 10

function gerarCodigo(MOTOR, resp) {
  const pids = pidsExigidos(MOTOR, resp);
  let bits = "";
  for (const pid of pids) {
    const i = resp[pid];
    if (!Number.isInteger(i) || i > 15) return "";     // fora do que o código sabe guardar
    bits += i.toString(2).padStart(BITS_POR_RESPOSTA, "0");
  }
  while (bits.length % 5) bits += "0";
  let saida = "";
  for (let i = 0; i < bits.length; i += 5)
    saida += ALFABETO[parseInt(bits.slice(i, i + 5), 2)];
  return saida.replace(/(.{4})(?=.)/g, "$1-");         // A7K2-M9P4-X3, mais fácil de ditar
}

function lerCodigo(MOTOR, texto) {
  const limpo = String(texto || "").toUpperCase().replace(/[^0-9A-Z]/g, "")
    .replace(/O/g, "0").replace(/I/g, "1");            // quem digita troca essas duas
  if (limpo.length < 4) return null;
  let bits = "";
  for (const c of limpo) {
    const v = ALFABETO.indexOf(c);
    if (v < 0) return null;
    bits += v.toString(2).padStart(5, "0");
  }
  // a trilha só é conhecida depois da área, então lê uma pergunta por vez e pergunta ao
  // motor qual vem em seguida
  const resp = {};
  let cursor = 0;
  for (let passo = 0; passo < 60; passo++) {
    const pids = pidsExigidos(MOTOR, resp);
    const pid = pids.find(p => !(p in resp));
    if (!pid) break;
    if (cursor + BITS_POR_RESPOSTA > bits.length) return null;
    const i = parseInt(bits.slice(cursor, cursor + BITS_POR_RESPOSTA), 2);
    cursor += BITS_POR_RESPOSTA;
    if (!MOTOR.rotulos[pid] || i >= MOTOR.rotulos[pid].length) return null;
    resp[pid] = i;
  }
  return pidsExigidos(MOTOR, resp).every(p => p in resp) ? resp : null;
}
