# Status e pendências

Atualizado em 18/08/2026.

## O que a página é hoje

LP de venda do **Qual IA Usar? (R$ 47)**, modelada na LP do meuassessor.com. Nove seções:

1. **Hero** com mockup de iPhone rodando uma conversa de WhatsApp (o produto trabalhando)
2. **Faixa** de argumentos de compra
3. **Problema** em 4 sintomas
4. **Casos de uso**: 4 cards com pedido em áudio e resposta oculta, mais 6 chips
5. **Diagnóstico** (o pop-up), chamada com os 3 passos
6. **Escopo**: as 9 ferramentas, só logo e nome
7. **Órbita** radial das categorias
8. **A conta do erro**: US$ 240 / 399 / 700+ por ano contra R$ 47 uma vez
9. **Oferta** com preço, 8 entregáveis e garantia, depois FAQ e fecho

Decisão do Alison em 18/08: **nada de graça**. Saíram a lista pública das 24 tarefas, os
desempates, os papéis das cinco principais, as descrições das ferramentas e o bloco de captura
gratuita. O resultado do diagnóstico é teaser com silhuetas.

## Pendências, em ordem de bloqueio

| # | Pendência | Onde | Impacto |
|---|---|---|---|
| 1 | **`CHECKOUT_URL` vazia** | topo de `gerar.py` | **A página não vende.** Os 2 botões caem em lista de espera pelo direct. Kiwify é a recomendação nesse ticket (4,99% + R$ 0,50 contra 9,9% + R$ 1,00 da Hotmart) |
| 2 | **`CAPTURA_URL` em `"DEMO"`** | topo de `gerar.py` | A tela de contato aparece mas **não grava**. Nunca publicar assim. Apps Script pronto em `_docs/apps-script-captura.js` |
| 3 | **O produto não existe** | fora do repo | A LP promete tutoriais, comparativos e plano de 7 dias. Precisa existir antes da primeira venda |
| 4 | **Custo do Higgsfield** | `dados.json` → `diagnostico.acesso` | Único não conferido; o build avisa a cada execução |
| 5 | **Web Analytics** | painel da Vercel | Sem ele não dá para saber em qual pergunta as pessoas abandonam |
| 6 | **Seção de autoridade** | seção `#prova` | Decisão do Alison: quais credenciais podem ir para o ar (Meta Business Partner, ERP em produção) |
| 7 | **Pop-up por exit-intent** | não implementado | Discutido, não construído. Recomendado só no desktop |

## O funil do meuassessor, mapeado em 18/08

Serve de referência para os próximos passos:

- **Todos os CTAs da LP** apontam para a âncora de preço, nenhum sai da página. Só o botão do preço vai para o checkout.
- **Checkout em 4 passos:** dados (nome, WhatsApp, e-mail, senha) → plano → pagamento → ativação. Gravam o cliente **antes** de mostrar o preço.
- **Planos:** mensal R$ 59,90 e anual R$ 358,80 (12x de R$ 29,90). O "R$ 29,90" da LP é o anual parcelado.
- **Beacon próprio de funil:** `POST /api/assinar/funil-visita-site`, 1x por sessão, `sendBeacon` com fallback. Não dependem só de Pixel.
- **Etapa gravada a cada passo** (`/api/assinar/sessao/etapa`) e **retomada de sessão** (`/api/assinar/sessao/{token}` devolve `{etapa, metodo}`).
- **Cupom pela URL** (`?cupom=X`) grava por 7 dias no `localStorage` e decora todos os links do checkout com cupom, `fbclid` e as 5 UTMs.
- **Gateways:** EFI/Gerencianet e Asaas para PIX, Hotmart no estorno.
- **Dedup de evento:** `analytics_event_id` do servidor usado no Pixel e na CAPI.

## Próximo passo sugerido

Ligar `CHECKOUT_URL` e `CAPTURA_URL`. Sem os dois, a página convence e não cobra, e o lead
que chega no fim do diagnóstico se perde.
