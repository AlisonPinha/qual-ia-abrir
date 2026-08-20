import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { autorizar } from "./_access.mjs";

const arquivos = {
  mapa: fileURLToPath(new URL("../_private/mapa.html", import.meta.url)),
  plano: fileURLToPath(new URL("../_private/plano.html", import.meta.url)),
};
const cacheHtml = new Map();

async function html(produto) {
  if (!cacheHtml.has(produto)) cacheHtml.set(produto, await readFile(arquivos[produto], "utf8"));
  return cacheHtml.get(produto);
}

export default {
  async fetch(request) {
    if (request.method !== "GET" && request.method !== "HEAD") return new Response("", { status: 405 });
    const produto = new URL(request.url).searchParams.get("produto");
    if (!(produto in arquivos)) return new Response("", { status: 404 });
    let permitido = null;
    try { permitido = await autorizar(request, produto); }
    catch (erro) {
      console.error("[entrega] falha de autorização", produto, erro?.message);
      return new Response("Serviço temporariamente indisponível", {
        status: 503,
        headers: { "cache-control": "no-store", "retry-after": "30" },
      });
    }
    if (!permitido) {
      return new Response(null, {
        status: 302,
        headers: {
          location: `/acesso?destino=${produto}`,
          "cache-control": "private, no-store",
          vary: "Cookie",
        },
      });
    }
    return new Response(request.method === "HEAD" ? null : await html(produto), {
      headers: {
        "content-type": "text/html; charset=utf-8",
        "cache-control": "private, no-store",
        "content-security-policy": "frame-ancestors 'none'",
        "referrer-policy": "strict-origin-when-cross-origin",
        "x-content-type-options": "nosniff",
        "x-frame-options": "DENY",
        vary: "Cookie",
      },
    });
  },
};
