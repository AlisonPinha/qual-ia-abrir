import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const config = JSON.parse(
  await readFile(new URL("../vercel.json", import.meta.url), "utf8"),
);

const BIO_DESTINATION =
  "https://diagnostico.noahai.com.br/?utm_source=instagram&utm_medium=organic_social&utm_campaign=qual_ia_usar&utm_content=link_bio";

test("/bio redireciona para a LP com a atribuição fixa da bio", () => {
  const redirect = config.redirects.find(({ source }) => source === "/bio");

  assert.ok(redirect, "a rota /bio precisa existir");
  assert.equal(redirect.destination, BIO_DESTINATION);
  assert.equal(redirect.permanent, false);
});

test("/bio é resolvida antes do redirecionamento genérico do domínio Vercel", () => {
  const bioIndex = config.redirects.findIndex(({ source }) => source === "/bio");
  const fallbackIndex = config.redirects.findIndex(
    ({ source }) => source === "/:path*",
  );

  assert.ok(bioIndex >= 0);
  assert.ok(fallbackIndex >= 0);
  assert.ok(bioIndex < fallbackIndex);
});
