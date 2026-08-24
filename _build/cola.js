(function (raiz) {
  "use strict";

  const PARAMETROS_ORIGEM = [
    "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "fbclid", "gclid"
  ];

  function filtrarOrigem(busca) {
    const entrada = new URLSearchParams(busca || "");
    const saida = new URLSearchParams();
    for (const nome of PARAMETROS_ORIGEM) {
      for (const valor of entrada.getAll(nome)) saida.append(nome, valor);
    }
    return saida;
  }

  function destinoDiagnostico(busca, origem) {
    const destino = new URL("/", origem || "https://diagnostico.noahai.com.br");
    destino.search = filtrarOrigem(busca).toString();
    return destino.pathname + destino.search;
  }

  function ativar() {
    if (!raiz.document || !raiz.location) return;
    const destino = destinoDiagnostico(raiz.location.search, raiz.location.origin);
    raiz.document.querySelectorAll("[data-diagnostico]").forEach(function (link) {
      link.href = destino;
      link.addEventListener("click", function () {
        if (typeof raiz.gtag === "function") {
          const origem = filtrarOrigem(raiz.location.search);
          raiz.gtag("event", "clicou_diagnostico_cola", {
            utm_content: origem.get("utm_content") || "",
          });
        }
      });
    });
  }

  raiz.QIA_COLA = Object.freeze({
    PARAMETROS_ORIGEM: PARAMETROS_ORIGEM.slice(),
    filtrarOrigem,
    destinoDiagnostico,
  });
  ativar();
})(globalThis);
