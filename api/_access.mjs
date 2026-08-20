import { neon } from "@neondatabase/serverless";

const COOKIE = "qia_sessao";
const SESSAO_DIAS = 30;
const STATUS_ATIVOS = new Set(["paid", "approved", "purchase_approved"]);
const PRODUTOS_MAPA = new Set([
  "Qual IA Usar?",
  "Método das 3 Abas",
  "Regra das 3 IAs",
  "Stack Mínima",
]);
const PRODUTOS_PLANO = new Set(["Sua primeira semana pronta"]);

let banco;
let schemaPronto;

const texto = valor => typeof valor === "string" ? valor.trim() : "";
const emailNormalizado = valor => texto(valor).toLowerCase().slice(0, 320);

export function telefoneNormalizado(valor) {
  const digitos = String(valor || "").replace(/\D/g, "");
  if (digitos.length < 10 || digitos.length > 15) return "";
  return digitos.startsWith("55") ? digitos : `55${digitos}`;
}

function segredo(nome) {
  const valor = process.env[nome];
  if (!valor || valor.length < 32) throw new Error(`${nome} ausente ou curto`);
  return valor;
}

function sql() {
  if (!process.env.DATABASE_URL) throw new Error("DATABASE_URL ausente");
  if (!banco) banco = neon(process.env.DATABASE_URL);
  return banco;
}

export async function prepararBanco() {
  if (!schemaPronto) schemaPronto = (async () => {
    const db = sql();
    await db`
      CREATE TABLE IF NOT EXISTS qia_orders (
        id TEXT PRIMARY KEY,
        ref_id TEXT,
        email_hash TEXT NOT NULL,
        phone_hash TEXT,
        claim_hash TEXT,
        claim_used_at TIMESTAMPTZ,
        product_id TEXT,
        product_name TEXT NOT NULL,
        entitlement TEXT NOT NULL CHECK (entitlement IN ('mapa', 'plano')),
        diagnostic_code TEXT,
        checkout_url TEXT,
        status TEXT NOT NULL,
        access_version INTEGER NOT NULL DEFAULT 1,
        paid_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await db`CREATE INDEX IF NOT EXISTS qia_orders_email_phone_idx ON qia_orders (email_hash, phone_hash, updated_at DESC)`;
    await db`CREATE INDEX IF NOT EXISTS qia_orders_claim_idx ON qia_orders (claim_hash) WHERE claim_hash IS NOT NULL`;
    await db`
      CREATE TABLE IF NOT EXISTS qia_revocations (
        order_id TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await db`
      CREATE TABLE IF NOT EXISTS qia_access_attempts (
        id BIGSERIAL PRIMARY KEY,
        identity_key TEXT NOT NULL,
        ip_key TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await db`CREATE INDEX IF NOT EXISTS qia_access_attempts_time_idx ON qia_access_attempts (created_at)`;
  })().catch(erro => {
    schemaPronto = undefined;
    throw erro;
  });
  return schemaPronto;
}

function bytesBase64url(bytes) {
  return Buffer.from(bytes).toString("base64url");
}

function jsonBase64url(valor) {
  return Buffer.from(JSON.stringify(valor), "utf8").toString("base64url");
}

function lerJsonBase64url(valor) {
  return JSON.parse(Buffer.from(valor, "base64url").toString("utf8"));
}

async function hmacCom(chaveBruta, valor) {
  const chave = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(chaveBruta),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  return bytesBase64url(await crypto.subtle.sign("HMAC", chave, new TextEncoder().encode(valor)));
}

async function hmacSessao(valor) {
  return hmacCom(segredo("ACCESS_TOKEN_SECRET"), valor);
}

async function hashPrivado(tipo, valor) {
  return hmacCom(segredo("ACCESS_DATA_SECRET"), `${tipo}:${valor}`);
}

function iguais(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let diferente = 0;
  for (let i = 0; i < a.length; i++) diferente |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diferente === 0;
}

async function assinar(payload) {
  const corpo = jsonBase64url(payload);
  return `${corpo}.${await hmacSessao(corpo)}`;
}

async function verificarAssinatura(token, tipo) {
  const [corpo, assinatura, sobra] = texto(token).split(".");
  if (!corpo || !assinatura || sobra) return null;
  if (!iguais(assinatura, await hmacSessao(corpo))) return null;
  let payload;
  try { payload = lerJsonBase64url(corpo); } catch { return null; }
  if (payload?.t !== tipo || !Number.isFinite(payload.exp) || payload.exp <= Date.now()) return null;
  return payload;
}

export function entitlementDoProduto(produto = {}) {
  const nome = texto(produto.name);
  if (PRODUTOS_PLANO.has(nome)) return "plano";
  if (PRODUTOS_MAPA.has(nome)) return "mapa";
  return null;
}

// qia2_<código do diagnóstico>.<segredo aleatório do aparelho>
function dadosDoSck(valor) {
  const sck = texto(valor).slice(0, 255);
  const match = /^qia2_([A-Za-z0-9_-]{8,180})\.([A-Za-z0-9_-]{20,80})$/.exec(sck);
  return match ? { diagnosticCode: match[1], claimSecret: match[2] } : {
    diagnosticCode: null, claimSecret: null,
  };
}

export function normalizarPedido(dado) {
  const produto = dado?.product || {};
  const cliente = dado?.customer || {};
  const id = texto(dado?.id || dado?.order_id);
  const email = emailNormalizado(cliente.email);
  const phone = telefoneNormalizado(cliente.phone ?? cliente.cellphone ?? cliente.phone_number);
  const entitlement = entitlementDoProduto(produto);
  const sck = texto(dado?.sck || dado?.tracking?.sck);
  const { diagnosticCode, claimSecret } = dadosDoSck(sck);
  if (!id || !email || !entitlement) return null;
  const dataBruta = texto(dado.paidAt || dado.paid_at || dado.createdAt || dado.created_at);
  const data = Date.parse(dataBruta);
  return {
    id,
    refId: texto(dado.refId || dado.ref_id),
    email,
    phone,
    claimSecret,
    productId: texto(produto.id || produto.short_id).slice(0, 200),
    productName: texto(produto.name).slice(0, 255),
    entitlement,
    diagnosticCode,
    checkoutUrl: texto(dado.checkoutUrl || dado.checkout_url).slice(0, 2048),
    paidAt: Number.isFinite(data) ? new Date(data).toISOString() : null,
  };
}

export async function registrarCompra(pedido) {
  await prepararBanco();
  const db = sql();
  const emailHash = await hashPrivado("email", pedido.email);
  const phoneHash = pedido.phone ? await hashPrivado("phone", pedido.phone) : null;
  const claimHash = pedido.claimSecret ? await hashPrivado("claim", pedido.claimSecret) : null;
  const linhas = await db`
    INSERT INTO qia_orders (
      id, ref_id, email_hash, phone_hash, claim_hash, product_id, product_name,
      entitlement, diagnostic_code, checkout_url, status, paid_at
    ) VALUES (
      ${pedido.id}, ${pedido.refId || null}, ${emailHash}, ${phoneHash}, ${claimHash},
      ${pedido.productId || null}, ${pedido.productName}, ${pedido.entitlement},
      ${pedido.diagnosticCode || null}, ${pedido.checkoutUrl || null},
      COALESCE((SELECT status FROM qia_revocations WHERE order_id = ${pedido.id}), 'paid'),
      ${pedido.paidAt}
    )
    ON CONFLICT (id) DO UPDATE SET
      ref_id = COALESCE(EXCLUDED.ref_id, qia_orders.ref_id),
      email_hash = EXCLUDED.email_hash,
      phone_hash = COALESCE(EXCLUDED.phone_hash, qia_orders.phone_hash),
      claim_hash = CASE WHEN qia_orders.claim_used_at IS NOT NULL THEN qia_orders.claim_hash
                        ELSE COALESCE(EXCLUDED.claim_hash, qia_orders.claim_hash) END,
      product_id = COALESCE(EXCLUDED.product_id, qia_orders.product_id),
      product_name = EXCLUDED.product_name,
      entitlement = EXCLUDED.entitlement,
      diagnostic_code = COALESCE(EXCLUDED.diagnostic_code, qia_orders.diagnostic_code),
      checkout_url = COALESCE(EXCLUDED.checkout_url, qia_orders.checkout_url),
      status = COALESCE(
        (SELECT status FROM qia_revocations WHERE order_id = EXCLUDED.id),
        CASE WHEN qia_orders.status IN ('refund', 'chargeback') THEN qia_orders.status ELSE 'paid' END
      ),
      paid_at = COALESCE(EXCLUDED.paid_at, qia_orders.paid_at),
      updated_at = NOW()
    RETURNING id, entitlement, diagnostic_code, status, access_version
  `;
  return linhas[0];
}

export async function revogarPedido(id, status) {
  if (!texto(id)) return false;
  await prepararBanco();
  const db = sql();
  await db`
    INSERT INTO qia_revocations (order_id, status)
    VALUES (${texto(id)}, ${texto(status).toLowerCase()})
    ON CONFLICT (order_id) DO UPDATE SET status = EXCLUDED.status, created_at = NOW()
  `;
  const linhas = await db`
    UPDATE qia_orders
    SET status = ${texto(status).toLowerCase()}, access_version = access_version + 1, updated_at = NOW()
    WHERE id = ${texto(id)}
    RETURNING id
  `;
  return linhas.length > 0;
}

function destinoDoPedido(pedido) {
  const caminho = pedido.entitlement === "plano" ? "/plano" : "/mapa";
  if (!pedido.diagnostic_code) return caminho;
  return `${caminho}?c=${encodeURIComponent(pedido.diagnostic_code)}`;
}

function ipDoRequest(request) {
  return texto(request.headers.get("x-forwarded-for")?.split(",")[0]
    || request.headers.get("x-real-ip") || "sem-ip");
}

async function passouLimite(request, identityKey) {
  const db = sql();
  const ipKey = await hashPrivado("ip", ipDoRequest(request));
  await db`DELETE FROM qia_access_attempts WHERE created_at < NOW() - INTERVAL '7 days'`;
  const recentes = await db`
    SELECT COUNT(*)::int AS total
    FROM qia_access_attempts
    WHERE created_at > NOW() - INTERVAL '15 minutes'
      AND (identity_key = ${identityKey} OR ip_key = ${ipKey})
  `;
  if ((recentes[0]?.total || 0) >= 6) return false;
  await db`INSERT INTO qia_access_attempts (identity_key, ip_key) VALUES (${identityKey}, ${ipKey})`;
  return true;
}

async function criarSessao(pedido) {
  const sessao = await assinar({
    t: "session", o: pedido.id, v: pedido.access_version,
    e: pedido.entitlement, exp: Date.now() + SESSAO_DIAS * 86400_000,
  });
  return { pedido, sessao, destino: destinoDoPedido(pedido) };
}

export async function reivindicarAcesso(request, dados = {}) {
  await prepararBanco();
  const db = sql();
  const claim = texto(dados.claim);
  let identityKey;
  let pedidos;

  if (/^[A-Za-z0-9_-]{20,80}$/.test(claim)) {
    const claimHash = await hashPrivado("claim", claim);
    identityKey = claimHash;
    if (!await passouLimite(request, identityKey)) return null;
    pedidos = await db`
      UPDATE qia_orders
      SET claim_hash = NULL, claim_used_at = NOW(), updated_at = NOW()
      WHERE id = (
        SELECT id FROM qia_orders
        WHERE claim_hash = ${claimHash} AND claim_used_at IS NULL
          AND status IN ('paid', 'approved', 'purchase_approved')
        ORDER BY CASE WHEN entitlement = 'plano' THEN 1 ELSE 0 END DESC, updated_at DESC
        LIMIT 1
      )
      RETURNING id, entitlement, diagnostic_code, status, access_version
    `;
  } else {
    const email = emailNormalizado(dados.email);
    const phone = telefoneNormalizado(dados.phone);
    if (!email || !/^\S+@\S+\.\S+$/.test(email) || !phone) return null;
    const emailHash = await hashPrivado("email", email);
    const phoneHash = await hashPrivado("phone", phone);
    identityKey = await hashPrivado("identity", `${emailHash}:${phoneHash}`);
    if (!await passouLimite(request, identityKey)) return null;
    pedidos = await db`
      SELECT id, entitlement, diagnostic_code, status, access_version
      FROM qia_orders
      WHERE email_hash = ${emailHash} AND phone_hash = ${phoneHash}
        AND status IN ('paid', 'approved', 'purchase_approved')
      ORDER BY CASE WHEN entitlement = 'plano' THEN 1 ELSE 0 END DESC, updated_at DESC
      LIMIT 1
    `;
  }

  return pedidos[0] ? criarSessao(pedidos[0]) : null;
}

function cookieDoRequest(request) {
  const cookies = request.headers.get("cookie") || "";
  for (const pedaco of cookies.split(";")) {
    const [nome, ...resto] = pedaco.trim().split("=");
    if (nome === COOKIE) return decodeURIComponent(resto.join("="));
  }
  return "";
}

export function cookieSessao(valor) {
  return `${COOKIE}=${encodeURIComponent(valor)}; Path=/; Max-Age=${SESSAO_DIAS * 86400}; HttpOnly; Secure; SameSite=Lax`;
}

export function cookieSaida() {
  return `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`;
}

export async function autorizar(request, necessario) {
  const payload = await verificarAssinatura(cookieDoRequest(request), "session");
  if (!payload?.o) return null;
  await prepararBanco();
  const pedidos = await sql()`
    SELECT id, entitlement, diagnostic_code, status, access_version
    FROM qia_orders WHERE id = ${payload.o} LIMIT 1
  `;
  const pedido = pedidos[0];
  if (!pedido || !STATUS_ATIVOS.has(pedido.status) || pedido.access_version !== payload.v) return null;
  const permitido = necessario === "mapa"
    ? pedido.entitlement === "mapa" || pedido.entitlement === "plano"
    : pedido.entitlement === "plano";
  return permitido ? pedido : null;
}

export const interno = {
  assinar,
  verificarAssinatura,
  dadosDoSck,
  destinoDoPedido,
  STATUS_ATIVOS,
};
