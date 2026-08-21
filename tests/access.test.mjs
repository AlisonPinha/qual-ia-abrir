import test from "node:test";
import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import {
  entitlementDoProduto,
  interno,
  normalizarPedido,
} from "../api/_access.mjs";
import { prepararCompraAprovada, prepararVendaParaPlanilha } from "../api/cakto.mjs";

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

test("espelho de venda leva UTM sem PII, sck ou query string", () => {
  const venda = prepararVendaParaPlanilha({
    id: "856c81b3-b347-4926-84b7-5d47676942cf",
    refId: "82QBXtc",
    status: "paid",
    baseAmount: "66.01",
    sck: "qia2_26KM-6623-8ATM-26SJ.abcdefghijklmnopqrstuvwx",
    checkoutUrl: "https://pay.cakto.com.br/3fxqxg5_1049811?utm_source=teste&utm_medium=controlado&utm_campaign=homologacao&utm_content=criativo_1&sck=qia2_SEGREDO.claim",
    customer: { name: "Pessoa Teste", email: "pessoa@example.com", phone: "11999990000" },
    product: { id: "produto-1", name: "Qual IA Usar?" },
    paidAt: "2026-08-20T21:03:00-03:00",
  }, "purchase_approved");
  assert.equal(venda.pedido, "856c81b3-b347-4926-84b7-5d47676942cf");
  assert.equal(venda.referencia, "82QBXtc");
  assert.equal(venda.status, "paid");
  assert.equal(venda.valor, 66.01);
  assert.equal(venda.utm_source, "teste");
  assert.equal(venda.utm_medium, "controlado");
  assert.equal(venda.utm_campaign, "homologacao");
  assert.equal(venda.utm_content, "criativo_1");
  assert.equal(venda.checkout, "https://pay.cakto.com.br/3fxqxg5_1049811");
  assert.equal(venda.codigo_diagnostico, "26KM-6623-8ATM-26SJ");
  const serializada = JSON.stringify(venda);
  assert.doesNotMatch(serializada, /pessoa@example|11999990000|SEGREDO|claim/);
});

test("reembolso gera atualização da mesma chave mesmo com payload mínimo", () => {
  const venda = prepararVendaParaPlanilha({
    id: "pedido-1",
    refId: "REF-1",
  }, "refund");
  assert.equal(venda.pedido, "pedido-1");
  assert.equal(venda.referencia, "REF-1");
  assert.equal(venda.evento, "refund");
  assert.equal(venda.status, "refund");
});

test("token assinado rejeita alteração e vencimento", async () => {
  const valido = await interno.assinar({ t: "session", o: "pedido-1", exp: Date.now() + 60_000 });
  assert.equal((await interno.verificarAssinatura(valido, "session")).o, "pedido-1");
  const adulterado = valido.slice(0, -1) + (valido.endsWith("A") ? "B" : "A");
  assert.equal(await interno.verificarAssinatura(adulterado, "session"), null);
  const vencido = await interno.assinar({ t: "session", o: "pedido-1", exp: Date.now() - 1 });
  assert.equal(await interno.verificarAssinatura(vencido, "session"), null);
});

test("entregas não existem no público e o checkout exige diagnóstico", async () => {
  await assert.rejects(stat(new URL("../public/mapa/index.html", import.meta.url)));
  await assert.rejects(stat(new URL("../public/plano/index.html", import.meta.url)));
  assert.ok((await stat(new URL("../_private/mapa.html", import.meta.url))).size > 100_000);
  assert.ok((await stat(new URL("../_private/plano.html", import.meta.url))).size > 100_000);
  for (const caminho of ["../public/index.html", "../public/abas/index.html", "../public/regra/index.html", "../public/stack/index.html"]) {
    const lp = await readFile(new URL(caminho, import.meta.url), "utf8");
    assert.match(lp, /searchParams\.set\("sck", "qia2_" \+ codigo \+ "\." \+ claim\)/);
    assert.match(lp, /if \(!checkoutComDiagnostico\(a\)\)/);
    assert.match(lp, /Fazer o diagnóstico e desbloquear por R\$ 67/);
    assert.doesNotMatch(lp, /coupon|cupom/i);
    assert.doesNotMatch(lp, /id="pos-clique"/);
  }
});
