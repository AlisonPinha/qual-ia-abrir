import test from "node:test";
import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import {
  entitlementDoProduto,
  interno,
  normalizarPedido,
} from "../api/_access.mjs";
import { prepararCompraAprovada } from "../api/cakto.mjs";

process.env.ACCESS_TOKEN_SECRET = "teste-local-com-mais-de-trinta-e-dois-caracteres";
process.env.ACCESS_DATA_SECRET = "outro-segredo-local-com-mais-de-trinta-e-dois";

test("mapeia somente os cinco produtos pagos conhecidos", () => {
  assert.equal(entitlementDoProduto({ name: "Qual IA Usar?" }), "mapa");
  assert.equal(entitlementDoProduto({ name: "Método das 3 Abas" }), "mapa");
  assert.equal(entitlementDoProduto({ name: "Regra das 3 IAs" }), "mapa");
  assert.equal(entitlementDoProduto({ name: "Stack Mínima" }), "mapa");
  assert.equal(entitlementDoProduto({ name: "Sua primeira semana pronta" }), "plano");
  assert.equal(entitlementDoProduto({ name: "Produto inventado" }), null);
});

test("pedido aprovado liga o sck ao diagnóstico sem tratar o código como acesso", () => {
  const pedido = normalizarPedido({
    id: "pedido-1",
    status: "paid",
    sck: "qia2_QIA-RESPOSTAS_123.abcdefghijklmnopqrstuvwx",
    customer: { name: "Pessoa Teste", email: " PESSOA@EXEMPLO.COM ", phone: "(11) 99999-0000" },
    product: { id: "produto-1", name: "Qual IA Usar?" },
    paidAt: "2026-08-20T12:00:00-03:00",
  });
  assert.equal(pedido.email, "pessoa@exemplo.com");
  assert.equal(pedido.phone, "5511999990000");
  assert.equal(pedido.diagnosticCode, "QIA-RESPOSTAS_123");
  assert.equal(pedido.claimSecret, "abcdefghijklmnopqrstuvwx");
  assert.equal(pedido.entitlement, "mapa");
  assert.deepEqual(interno.dadosDoSck("QIA-RESPOSTAS_123"), {diagnosticCode:null, claimSecret:null});
});

test("compra aprovada libera acesso mesmo se o preço faltar para o Meta", () => {
  const compra = prepararCompraAprovada({
    id: "pedido-sem-preco",
    status: "paid",
    customer: { email: "pessoa@exemplo.com", phone: "11999990000" },
    product: { id: "produto-1", name: "Qual IA Usar?" },
  });
  assert.equal(compra.preco, null);
  assert.equal(compra.acesso.id, "pedido-sem-preco");
  assert.equal(compra.acesso.entitlement, "mapa");
});

test("token assinado rejeita alteração e vencimento", async () => {
  const valido = await interno.assinar({ t: "session", o: "pedido-1", exp: Date.now() + 60_000 });
  assert.equal((await interno.verificarAssinatura(valido, "session")).o, "pedido-1");
  const adulterado = valido.slice(0, -1) + (valido.endsWith("A") ? "B" : "A");
  assert.equal(await interno.verificarAssinatura(adulterado, "session"), null);
  const vencido = await interno.assinar({ t: "session", o: "pedido-1", exp: Date.now() - 1 });
  assert.equal(await interno.verificarAssinatura(vencido, "session"), null);
});

test("entregas não existem no diretório público e todas as LPs enviam sck", async () => {
  await assert.rejects(stat(new URL("../public/mapa/index.html", import.meta.url)));
  await assert.rejects(stat(new URL("../public/plano/index.html", import.meta.url)));
  assert.ok((await stat(new URL("../_private/mapa.html", import.meta.url))).size > 100_000);
  assert.ok((await stat(new URL("../_private/plano.html", import.meta.url))).size > 100_000);
  for (const caminho of ["../public/index.html", "../public/abas/index.html", "../public/regra/index.html", "../public/stack/index.html"]) {
    const lp = await readFile(new URL(caminho, import.meta.url), "utf8");
    assert.match(lp, /searchParams\.set\("sck", "qia2_" \+ codigo \+ "\." \+ claim\)/);
    assert.doesNotMatch(lp, /id="pos-clique"/);
  }
});
