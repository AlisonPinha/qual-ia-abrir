#!/usr/bin/env node
// Importa uma compra anterior ao webhook sem guardar dados do cliente no repositório.
// Uso: node scripts/importar-pedido.mjs --id ... --email ... --phone ... --produto ... [--ref ...] [--pago-em ...]

import { normalizarPedido, registrarCompra } from "../api/_access.mjs";

const args = new Map();
for (let i = 2; i < process.argv.length; i++) {
  const chave = process.argv[i];
  if (!chave.startsWith("--")) continue;
  args.set(chave, process.argv[++i] || "");
}

const pedido = normalizarPedido({
  id: args.get("--id"),
  status: "paid",
  paidAt: args.get("--pago-em") || new Date().toISOString(),
  refId: args.get("--ref") || "",
  customer: { email: args.get("--email"), phone: args.get("--phone") },
  product: { name: args.get("--produto") },
  sck: args.get("--sck") || "",
});

if (!pedido?.phone) {
  console.error("Pedido inválido. Informe --id, --email, --phone e um --produto conhecido.");
  process.exitCode = 2;
} else {
  const salvo = await registrarCompra(pedido);
  console.log(`Pedido ${salvo.id} importado. A Cakto continua responsável pelo e-mail.`);
}
