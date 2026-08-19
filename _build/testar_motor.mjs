// Confere o motor depois da ramificação por área. Roda em cima de _lib/motor.mjs,
// o mesmo arquivo que a /api/mapa importa, então testa o artefato e não uma cópia.
//
// Uso: node _build/testar_motor.mjs   (depois de python3 _build/gerar_mapa.py)
//
// O que ele pega, que uma leitura não pega: peso apontando para ferramenta que não
// existe, trilha que não fecha o questionário, e ferramenta do catálogo que ficou
// impossível de sair em qualquer combinação, ou seja, peso morto vendido como opção.

import { MOTOR, calcularStack, pidsExigidos } from "../_lib/motor.mjs";

const ferramentas = Object.keys(MOTOR.ferramentas);
const falhas = [];
const checar = (ok, msg) => { if (!ok) falhas.push(msg); };

// 1. todo peso aponta para ferramenta que existe
for (const [pid, opcoes] of Object.entries(MOTOR.pesos))
  for (const pesos of opcoes)
    for (const nome of Object.keys(pesos))
      checar(ferramentas.includes(nome), `${pid}: peso para "${nome}", que não está no catálogo`);

// 2. cada área fecha o questionário com o mesmo número de perguntas
const [qArea] = MOTOR.perfil;
const areas = MOTOR.rotulos[qArea].map((_r, i) => i);
for (const a of areas) {
  // "quantas: 1" liga as perguntas que só valem para quem já tem alguma ferramenta:
  // é o caminho mais longo, que é o que MOTOR.total mede
  const exigidos = pidsExigidos(MOTOR, { [qArea]: a, quantas: 1 });
  checar(exigidos.length === MOTOR.total,
    `área "${MOTOR.rotulos[qArea][a]}": ${exigidos.length} perguntas, o contador diz ${MOTOR.total}`);
  checar(exigidos.includes(qArea), `área ${a}: a pergunta de área sumiu da trilha`);
}

// 3. varredura: toda combinação das perguntas que mexem no resultado
const vistas = new Map(ferramentas.map(n => [n, 0]));
let combinacoes = 0;

for (const a of areas) {
  const base = { [qArea]: a };
  // perguntas desta trilha que mudam alguma coisa: as que têm peso, mais orçamento
  // (decide quantas entram já) e "onde" (celular corta o Claude Code)
  const variar = pidsExigidos(MOTOR, base).filter(pid =>
    pid !== qArea && (MOTOR.pesos[pid].some(p => Object.keys(p).length)
                      || pid === MOTOR.perfil[1] || pid === MOTOR.celular[0]));

  const varrer = (i, resp) => {
    if (i === variar.length) {
      combinacoes++;
      for (const s of calcularStack(MOTOR, resp).stack) vistas.set(s.nome, vistas.get(s.nome) + 1);
      return;
    }
    const pid = variar[i];
    for (let j = 0; j < MOTOR.rotulos[pid].length; j++) varrer(i + 1, { ...resp, [pid]: j });
  };
  varrer(0, base);
}

for (const [nome, n] of vistas)
  checar(n > 0, `"${nome}" não entra na stack em nenhuma combinação: é peso morto no catálogo`);

console.log(`${combinacoes.toLocaleString("pt-BR")} combinações, ${MOTOR.total} perguntas por pessoa`);
for (const [nome, n] of [...vistas].sort((x, y) => y[1] - x[1]))
  console.log(`  ${nome.padEnd(12)} ${(n / combinacoes * 100).toFixed(1).padStart(5)}% das stacks`);

if (falhas.length) {
  console.error("\nFALHOU:");
  for (const f of falhas) console.error("  " + f);
  process.exit(1);
}
console.log("\nok");
