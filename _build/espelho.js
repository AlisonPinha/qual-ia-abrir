// A penúltima tela do quiz: repete de volta o que a pessoa respondeu, antes de revelar
// o resultado. Injetado nas duas páginas pelo mesmo motivo do motor.js: o site e a
// entrega paga não podem divergir.
//
// É isto que faz a pergunta que não vota no motor deixar de ser atrito. Ela some hoje
// sem deixar rastro; aqui ela volta como prova de que o diagnóstico é sobre esta pessoa.

// Só rótulo de opção entra: o texto livre que a pessoa escreveu fica de fora, porque
// aqui ele seria eco do que ela digitou, e não prova de que alguém leu.
function montarEspelho(MOTOR, resp) {
  return MOTOR.espelho.flatMap(([pid, rotulo]) => {
    const alvo = pid === "*tarefa"
      ? Object.keys(resp).find(q => /(^|_)tarefa$/.test(q))
      : pid;
    if (!alvo || !(alvo in resp) || !MOTOR.rotulos[alvo]) return [];
    const valor = MOTOR.rotulos[alvo][resp[alvo]];
    return valor ? [[rotulo, valor]] : [];
  });
}

function pintarEspelho(MOTOR, resp, lista) {
  lista.textContent = "";
  for (const [rotulo, valor] of montarEspelho(MOTOR, resp)) {
    const li = document.createElement("li");
    const k = document.createElement("span");
    k.className = "espelho-k";
    k.textContent = rotulo;
    const v = document.createElement("span");
    v.className = "espelho-v";
    v.textContent = valor;
    li.append(k, v);
    lista.appendChild(li);
  }
}
