// Refaz a conta do corte com o catálogo de 12, que o PLANO-EXECUCAO pede desde a saída da
// Poppy AI: os R$ 479 e os 91,4% são de 20/08 e não valem mais. Roda a mesma varredura do
// testar_motor.mjs e soma o custo mensal real de cada ferramenta cortada.
import { MOTOR, calcularStack, pidsExigidos } from "../_lib/motor.mjs";
import fs from "node:fs";

const dados = JSON.parse(fs.readFileSync(new URL("../_build/dados.json", import.meta.url), "utf8"));
const mes = Object.fromEntries(Object.entries(dados.diagnostico.acesso).map(([n, v]) => [n, v.mes || 0]));

const [qArea] = MOTOR.perfil;
const areas = MOTOR.rotulos[qArea].map((_r, i) => i);
const cortes = [], stacks = [];
let combinacoes = 0, corteMaior = 0, maiorCortePagaMapa = 0;
const preco = Number(dados.oferta.preco);

for (const a of areas) {
  const base = { [qArea]: a };
  const variar = pidsExigidos(MOTOR, base).filter(pid =>
    pid !== qArea && (MOTOR.pesos[pid].some(p => Object.keys(p).length)
                      || pid === MOTOR.perfil[1] || pid === MOTOR.celular[0]));
  const varrer = (i, resp) => {
    if (i === variar.length) {
      combinacoes++;
      const { stack, corta } = calcularStack(MOTOR, resp);
      const custoCorte = corta.reduce((s, n) => s + (mes[n] || 0), 0);
      const custoStack = stack.reduce((s, f) => s + (mes[f.nome] || 0), 0);
      cortes.push(custoCorte); stacks.push(custoStack);
      if (custoCorte > custoStack) corteMaior++;
      if (Math.max(...corta.map(n => mes[n] || 0)) >= preco) maiorCortePagaMapa++;
      return;
    }
    const pid = variar[i];
    for (let j = 0; j < MOTOR.rotulos[pid].length; j++) varrer(i + 1, { ...resp, [pid]: j });
  };
  varrer(0, base);
}

const pct = (arr, p) => { const s = [...arr].sort((x, y) => x - y); return s[Math.floor(s.length * p)]; };
const fmt = n => "R$ " + n.toFixed(0);
const hoje = new Date().toLocaleDateString("pt-BR");

console.log(`\nCONTA DO CORTE refeita em ${hoje}, catálogo de ${Object.keys(MOTOR.ferramentas).length} ferramentas`);
console.log(`${combinacoes.toLocaleString("pt-BR")} combinações\n`);
console.log(`as 3 cortadas somam, por mês:`);
console.log(`  mediana  ${fmt(pct(cortes, .5))}    p10 ${fmt(pct(cortes, .1))}   p90 ${fmt(pct(cortes, .9))}`);
console.log(`a stack recomendada custa, por mês:`);
console.log(`  mediana  ${fmt(pct(stacks, .5))}    p10 ${fmt(pct(stacks, .1))}   p90 ${fmt(pct(stacks, .9))}`);
console.log(`\no corte custa mais que a stack em ${(corteMaior / combinacoes * 100).toFixed(1)}% das combinações`);
console.log(`a MAIOR cortada sozinha paga os R$ ${preco} em ${(maiorCortePagaMapa / combinacoes * 100).toFixed(1)}% (${maiorCortePagaMapa.toLocaleString("pt-BR")} de ${combinacoes.toLocaleString("pt-BR")})`);
