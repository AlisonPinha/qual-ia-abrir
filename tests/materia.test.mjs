import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import vm from "node:vm";

const raiz = path.resolve(import.meta.dirname, "..");
const dados = JSON.parse(fs.readFileSync(path.join(raiz, "_build/dados.json"), "utf8"));
const html = fs.readFileSync(path.join(raiz, "public/materia/index.html"), "utf8");
const script = fs.readFileSync(path.join(raiz, "_build/cola.js"), "utf8");

// O arquivo se chama cola.js por herança: ele é o script de atribuição que a /materia usa.


test("matéria repassa somente atribuição permitida para a LP", () => {
  const contexto = vm.createContext({ URL, URLSearchParams });
  vm.runInContext(script, contexto);
  const destino = contexto.QIA_COLA.destinoDiagnostico(
    "?utm_source=instagram&utm_medium=direct&utm_campaign=novos_seguidores" +
    "&utm_content=dm_ABC123&fbclid=ok&sck=SEGREDO&injetado=nao",
    "https://diagnostico.noahai.com.br/cola",
  );
  assert.equal(
    destino,
    "/?utm_source=instagram&utm_medium=direct&utm_campaign=novos_seguidores" +
    "&utm_content=dm_ABC123&fbclid=ok",
  );
  assert.doesNotMatch(destino, /sck|SEGREDO|injetado/);
});

test("matéria repete o CTA exato na primeira dobra e no fechamento", () => {
  assert.equal(
    (html.match(/<a class="btn" data-diagnostico href="\/">/g) || []).length,
    2,
  );
  assert.equal(
    (html.match(/>Fazer o meu diagnóstico<\/a>/g) || []).length,
    2,
  );
  // A matéria veste portal, não a marca: matéria roxa não parece matéria, parece banner.
  assert.match(html, /--vermelho: #d8232a/);
  assert.doesNotMatch(html, /#c183fb/);
});

