#!/usr/bin/env python3
"""Gera a porta pública de recuperação; a entrega continua privada no servidor."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "public" / "acesso" / "index.html"
SAIDA.parent.mkdir(parents=True, exist_ok=True)

HTML = r'''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>Abrir minha compra · Qual IA Usar?</title>
  <link rel="icon" href="/icon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap">
  <style>
    :root{color-scheme:dark;--fundo:#0d0b12;--card:#17131f;--texto:#f7f3ff;--muted:#aaa2b5;--roxo:#865cff;--borda:rgba(255,255,255,.11)}
    *{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(circle at 50% 0,#23183b 0,transparent 44%),var(--fundo);color:var(--texto);font-family:Poppins,system-ui,sans-serif}
    main{width:min(100% - 32px,560px);margin:0 auto;padding:48px 0 80px}.marca{display:inline-block;color:#cdbdff;font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:34px}
    .card{background:rgba(23,19,31,.94);border:1px solid var(--borda);border-radius:20px;padding:clamp(24px,6vw,42px);box-shadow:0 28px 90px rgba(0,0,0,.28)}
    .selo{display:inline-block;background:rgba(134,92,255,.14);color:#cbbaff;border:1px solid rgba(134,92,255,.3);border-radius:999px;padding:7px 11px;font-size:12px;font-weight:700}
    h1{font-size:clamp(28px,7vw,42px);line-height:1.08;letter-spacing:-.035em;margin:18px 0 14px}p{color:var(--muted);line-height:1.65;margin:0 0 24px;font-size:15px}
    label{display:block;font-size:13px;font-weight:600;margin-bottom:8px}input{width:100%;height:52px;border-radius:10px;border:1px solid var(--borda);background:#0f0c15;color:var(--texto);padding:0 14px;font:inherit;outline:none}input:focus{border-color:var(--roxo);box-shadow:0 0 0 3px rgba(134,92,255,.16)}
    button{width:100%;height:52px;margin-top:12px;border:0;border-radius:10px;background:var(--roxo);color:white;font:700 15px Poppins,sans-serif;cursor:pointer}button:disabled{opacity:.65;cursor:wait}
    .retorno{margin:18px 0 0;color:#d8cfff;font-size:14px}.ajuda{border-top:1px solid var(--borda);margin-top:30px;padding-top:24px;font-size:13px}.ajuda a{color:#cbbaff}.erro-link{background:rgba(255,92,119,.1);border:1px solid rgba(255,92,119,.25);color:#ffc2cc;padding:12px 14px;border-radius:10px;margin-bottom:18px;font-size:13px}
  </style>
</head>
<body>
<main>
  <a class="marca" href="/">Qual IA Usar?</a>
  <section class="card">
    <span class="selo">Acesso de comprador</span>
    <h1>Abra o que você comprou.</h1>
    <p>Use os mesmos dados informados na compra. A confirmação acontece aqui, sem depender de um segundo e-mail.</p>
    <div class="erro-link" id="erro-link" hidden></div>
    <p class="retorno" id="automatico" role="status" hidden>Conferindo a compra neste aparelho...</p>
    <form id="form">
      <label for="email">E-mail da compra</label>
      <input id="email" name="email" type="email" autocomplete="email" inputmode="email" required placeholder="voce@exemplo.com">
      <label for="phone" style="margin-top:14px">WhatsApp usado na compra</label>
      <input id="phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required placeholder="(11) 99999-0000">
      <button id="enviar" type="submit">Abrir minha compra</button>
    </form>
    <p class="retorno" id="retorno" role="status" hidden></p>
    <p class="ajuda">A Cakto já confirmou o pagamento por e-mail. Estes dados servem apenas para localizar essa compra; o telefone é comparado por hash e não é salvo aqui em texto aberto. Depois, este aparelho fica conectado por 30 dias.</p>
  </section>
</main>
<script>
  const CLAIM_CHAVE = 'qia:claim';
  const form = document.getElementById('form');
  const retorno = document.getElementById('retorno');
  const erro = document.getElementById('erro-link');
  const botao = document.getElementById('enviar');

  async function reivindicar(payload, automatico = false) {
    if (!automatico) { botao.disabled = true; botao.textContent = 'Conferindo...'; }
    try {
      const resposta = await fetch('/api/acesso', {method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
      const dados = await resposta.json();
      if (dados.autenticado && /^\/(mapa|plano)(?:\?|$)/.test(dados.destino || '')) {
        try { localStorage.removeItem(CLAIM_CHAVE); } catch (_) {}
        location.replace(dados.destino);
        return true;
      }
      if (!automatico) {
        erro.textContent = dados.indisponivel
          ? 'A conferência está temporariamente indisponível. Tente novamente em alguns minutos.'
          : 'Não encontrei uma compra aprovada com esses dados. Confira o e-mail e o WhatsApp usados no checkout.';
        erro.hidden = false;
      }
    } catch (_) {
      if (!automatico) {
        erro.textContent = 'Não consegui conferir agora. Verifique a conexão e tente novamente.';
        erro.hidden = false;
      }
    }
    if (!automatico) { botao.disabled = false; botao.textContent = 'Abrir minha compra'; }
    return false;
  }

  form.addEventListener('submit', async ev => {
    ev.preventDefault(); erro.hidden = true; retorno.hidden = true;
    await reivindicar({
      email: document.getElementById('email').value,
      phone: document.getElementById('phone').value,
    });
  });

  (async () => {
    const botao = document.getElementById('enviar');
    try {
      const salvo = JSON.parse(localStorage.getItem(CLAIM_CHAVE) || 'null');
      if (!salvo?.valor || salvo.ate <= Date.now()) return;
      document.getElementById('automatico').hidden = false;
      const abriu = await reivindicar({claim: salvo.valor}, true);
      if (!abriu) document.getElementById('automatico').hidden = true;
    } catch (_) { document.getElementById('automatico').hidden = true; }
  })();
</script>
</body>
</html>'''

SAIDA.write_text(HTML, encoding="utf-8")
print(f"gerado: {SAIDA.relative_to(RAIZ)}  ({len(HTML):,} bytes)")
