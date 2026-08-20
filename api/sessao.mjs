import { autorizar, cookieSaida } from "./_access.mjs";

const headers = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
};

export default {
  async fetch(request) {
    if (request.method === "DELETE" || request.method === "POST") {
      return new Response(JSON.stringify({ ok: true }), {
        headers: { ...headers, "set-cookie": cookieSaida() },
      });
    }
    if (request.method !== "GET") return new Response("", { status: 405 });
    try {
      const plano = await autorizar(request, "plano");
      if (plano) return new Response(JSON.stringify({ autenticado: true, entitlement: "plano" }), { headers });
      const mapa = await autorizar(request, "mapa");
      return new Response(JSON.stringify({ autenticado: Boolean(mapa), entitlement: mapa ? "mapa" : null }), { headers });
    } catch (erro) {
      console.error("[sessao] falha de autorização", erro?.message);
      return new Response(JSON.stringify({ autenticado: false, entitlement: null }), { status: 503, headers });
    }
  },
};
