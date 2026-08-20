import { cookieSessao, reivindicarAcesso } from "./_access.mjs";

export const config = { maxDuration: 10 };

const headers = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
};

export default {
  async fetch(request) {
    if (request.method !== "POST") return new Response("", { status: 405 });
    const cru = await request.text();
    if (cru.length > 2000) return new Response("", { status: 413 });
    let dados = {};
    try { dados = JSON.parse(cru); } catch { /* resposta genérica abaixo */ }
    try {
      const acesso = await reivindicarAcesso(request, dados);
      if (!acesso) {
        return new Response(JSON.stringify({ autenticado: false }), { status: 200, headers });
      }
      return new Response(JSON.stringify({ autenticado: true, destino: acesso.destino }), {
        status: 200,
        headers: { ...headers, "set-cookie": cookieSessao(acesso.sessao) },
      });
    } catch (erro) {
      console.error("[acesso] falha ao validar compra", erro?.message);
      return new Response(JSON.stringify({ autenticado: false, indisponivel: true }), {
        status: 503, headers,
      });
    }
  },
};
