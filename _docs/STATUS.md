# Status e pendências

## Próxima sessão começa aqui

**Leia primeiro `PLANO-EXECUCAO.md`**, que é a fila com quem faz e critério de pronto, e
`DIAGNOSTICO.md`, que é o quiz por dentro, gerado do `dados.json`.

**Estado em 19/08/2026, tudo no ar:** LP em 4 variantes, `/mapa` com a IA redigindo e vendendo
o upsell, `/plano` com a entrega do upsell, quiz de 23 etapas, código de acesso, a primeira
venda feita, o checkout do upsell de R$ 130 na Cakto e, desde a sessão da noite, o funil do
quiz medido pergunta a pergunta.

### Publicado em 20/08, com a bateria inteira verde

Deploy pela CLI, 34 commits enviados ao GitHub (estavam só no disco desde 19/08) e o Apps
Script na versão 5.

| O que foi medido | Resultado |
|---|---|
| Regressão contra produção | **29 de 29**, sem erro de página. O `/mapa` escreveu 8/8 blocos em 26s e a `/plano` os 7 dias em 11s |
| QA do fluxo novo em produção | **19 de 19**, console limpo |
| Altura em 360x640 e 390x844 | **9 de 9**: o botão de enviar, o "Não, quero sair" e o bloco do código cabem sem rolar |
| `/api/cakto` | 405 em GET, 401 sem segredo e com segredo errado, 400 em corpo quebrado |
| Páginas | LP, `/mapa`, `/plano` e as 3 variantes respondendo 200 |

**No QA de produção o POST do Apps Script e o pixel do Meta ficam bloqueados por rota**, para
o teste não gravar lead falso na planilha nem sujar o Events Manager com `Lead` de mentira. A
regressão para antes de enviar o contato pelo mesmo motivo.

**Um teste quebrou e o defeito era dele:** o bloco do código em outro aparelho lia
`lp.codigo`, que sumiu quando o código saiu da tela de oferta. Passou a ler o código de
dentro do link da saída, que é onde ele vive agora.

### 20/08: a saída do quiz virou duas telas, e o que a revisão dos commits achou

**Três coisas que o Alison apontou na tela, e o que elas revelaram por baixo.**

| O que ele pediu | O que entrou |
|---|---|
| Tirar a seta de voltar do quiz | Ela era desenhada **por cima** do contador "n de 19" (círculo de 34px em `position:absolute`, `top:-6px`). Saiu das três páginas com quiz, junto do histórico e do CSS |
| Tirar o código de acesso de junto do preço | "Não vai comprar agora? Guarda este código" ao lado do botão de compra é permissão para adiar. Ele virou o que a pessoa recebe **em troca do contato**, na saída |
| Pop-up de WhatsApp ao tentar fechar | Entrou como ele desenhou: tela 1 pergunta se tem certeza, tela 2 pede nome e WhatsApp. Só a copy mudou, ver abaixo |

**O achado sério: o botão "Guardar no WhatsApp" entregava o produto pago.** A mensagem que
a LP montava levava o link do `/mapa`, que é a entrega e não tem paywall: o que a protege é
a URL não circular. Quem fazia o quiz e não comprava saía com o endereço do produto no
WhatsApp, pronto para reencaminhar. Estava no ar desde 19/08, na tela que todo mundo via.
Agora o link é o da própria LP com o código, e a LP aprendeu a ler o `?c=`.

**"Você vai perder tudo" não entrou, e não vai entrar.** A LP guarda as respostas a cada
clique e retoma sozinha desde 19/08. Prometer perda seria assustar com o que não acontece,
que é da mesma família da escassez inventada. A tela 1 diz a verdade: onde a pessoa parou,
ou que o diagnóstico já está pronto.

**A tela 2 não liga a captura no meio do quiz.** O lead sai pelo mesmo Web App do envio
anônimo, com `tipo: "lead"`, então a `CAPTURA_URL` continua vazia e o passo de contato
dentro do quiz continua desligado, que é o que o playbook mede como pior (queda de 1% a 2%
por etapa em dois nichos). Quem sai no meio do quiz sai direto: sem as respostas todas não
existe código, e pedir contato sem ter o que entregar seria pedágio.

**Da revisão dos 32 commits que ainda não subiram, dois buracos corrigidos:**
- a coluna `utm` da aba `leads` nascia vazia (cabeçalho com 22 colunas, `appendRow` com 21);
- o `/api/cakto` engolia venda aprovada em silêncio quando o campo não batia, que é o mesmo
  silêncio dos 14 dias sem Purchase. Agora tem `console.error` com id, status e se havia valor.

**Anotado, sem correção:** com order bump, se a Cakto repetir o mesmo `id` nas duas linhas
do `data`, os dois eventos saem com o mesmo `event_id`, o Meta deduplica e o valor do
segundo item some. Só dá para confirmar com payload real de uma venda com bump.

**O que o print pegou e o teste verde não pegava:** o `display:flex` que entrou no
`.res-codigo` vence o `hidden` do navegador, e o bloco do código ficava visível mesmo
escondido. Faltava `.res-codigo[hidden] { display: none; }`. Desde então o QA mede
`offsetParent`, não a propriedade `hidden`.

**Apps Script recolado em 20/08, pelo navegador.** Implantado como **versão 5 na mesma
implantação** (`v5 - lead grava a coluna utm`), então o `ANALITICO_URL` continua valendo:
o código de implantação segue `AKfycbzY1PYcR4EC...`. Conferido com POST real do tipo `lead`:
a aba `leads` **nasceu agora**, com as 22 colunas, e a `utm` veio preenchida com
`utm_source=teste_recolagem&utm_campaign=v5`. A linha de teste foi apagada e a aba ficou
vazia, com o cabeçalho certo, esperando o primeiro lead de verdade.

### A próxima sessão começa por aqui

**O `Purchase` já existe, e agora falta a primeira venda para conferir.** O achado da noite de
19/08 foi que a venda paga não chegava ao Meta: em 14 dias o pixel tinha 115 PageView, 83
ViewContent, 22 InitiateCheckout e **zero `Purchase`**, porque o Pix é pago fora do navegador e
a pessoa nunca volta à página. Resolvido no mesmo dia: `/api/cakto` recebe o webhook
`purchase_approved` e manda o evento pelo servidor, com o id do pedido como `event_id`.

**O que conferir quando cair a próxima venda:** o `Purchase` aparecendo no Events Manager, com
o `content_name` da variante. Se não aparecer, o log da função na Vercel diz por quê: ele
registra a recusa do Meta e nada mais.

**A recuperação por WhatsApp (2.5) está a uma decisão de distância.** A Cakto tem os eventos de
cobrança gerada e não paga, o mesmo webhook já está criado e o n8n tem a fundação pronta. Falta
o Alison dizer de que número sai a mensagem.

### O que está esperando o Alison

- **De que número sai a recuperação por WhatsApp (2.5).** A infra existe: a Cakto tem os
  eventos, a Evolution está no ar e o n8n tem a fundação pronta. O que falta é o número: a
  única instância dele é o `teste1`, no celular pessoal, já amarrada ao Clinic.io. Disparo frio
  ali arrisca o número que ele usa para tudo
- **Gravar a VSL** do upsell, roteiro no vault. As telas eu gravo com Playwright quando ele pedir.
  **O bloco de 1:26 precisa mudar antes:** ele promete "é só nessa tela" e a página não cumpre,
  porque o crédito é de quem comprou, não da tela
- **Revisar a voz dos 7 dias**, que estão no ar em `/plano`
- **Trocar a chave da API**, parado por decisão dele até acabar a fase de teste
- **Colher o primeiro depoimento real** com a compradora de 19/08. O `prova.depoimentos`
  continua vazio de propósito, e a seção some enquanto estiver

### O que fazer no começo da próxima sessão

1. `for v in "" abas regra stack; do python3 _build/gerar.py $v; done`, mais
   `gerar_mapa.py`, `gerar_plano.py` e `gerar_doc_quiz.py`. O `git status` tem que ficar limpo.
2. `node _build/testar_motor.mjs`
3. Se for publicar algo grande, `node run.js _build/regressao.js` de dentro da
   `~/.claude/skills/playwright-skill`. Custa 1 chamada ao `/api/mapa` e 3 ao `/api/plano`.

### O funil do quiz, ligado na noite de 19/08

O envio anônimo só acontecia quando o quiz **terminava**: quem saía no meio não deixava rastro,
e não dava para saber se as 19 perguntas seguram ou derrubam. Agora um `sendBeacon` na saída
grava uma linha por pessoa na aba `abandonos`, com o pid onde ela parou, o enunciado da
pergunta, a posição, quantas respondeu, a área e a UTM. Quem termina fica na mesma linha com
`concluiu=sim`, então numerador e denominador ficam juntos e a taxa sai de uma aba só.

Ligado nas três páginas com quiz. Na LP conta quem abriu o pop-up; no `/mapa` e no `/plano`
conta quem viu o quiz, porque quem entra por código ou por memória não passou por ele.

| O que foi medido | Resultado |
|---|---|
| QA local, com o build servido em `localhost` | **16 de 16** |
| Regressão em produção, depois do deploy | **25 de 25**, sem erro de página |
| Apps Script | versão 4 na **mesma** implantação, então a `ANALITICO_URL` não mudou |
| POST real na planilha | 4 sinais viraram 2 linhas, com o upsert e o congelamento certos |

**Duas das três falhas do QA eram do teste, não do produto.** Esconder a aba com
`bringToFront` não deixa a página `hidden` no Chromium visível, e o `route` do Playwright
enxerga o `sendBeacon` no `pagehide` mas não entrega o corpo: o que prova que o beacon saiu é o
evento de `request`. A terceira era do produto: sem tratamento, quem concluía e depois refazia o
quiz reescrevia a própria linha para "parou na pergunta 1" com "concluiu sim" ao lado. Agora a
linha de quem concluiu fica congelada, e só o horário do último sinal avança.

**A ordem que não pode inverter, e vale para qualquer mudança de payload:** o Apps Script vai
primeiro. O `doPost` manda todo tipo desconhecido para `gravarLead`, então publicar o front
antes faria cada beacon virar linha na aba `leads`. **Isso chegou a acontecer:** na primeira
rodada do QA um contexto do navegador ficou sem interceptação, um beacon real saiu e virou
linha vazia na aba `leads`. Achado na revisão do fim da sessão e apagado.

**Risco conhecido:** conta gratuita do Apps Script tem 90 minutos de execução por dia, o que dá
umas 5.000 gravações. Com tráfego pago grande o teto aparece, e aí a saída é gravar em outro
lugar, não cortar a medição.

### O `Purchase` pelo servidor, ligado em 19/08 à noite

| Peça | Estado |
|---|---|
| `/api/cakto` | no ar, 29 de 29 no QA local |
| Token da API de Conversões | gerado no Events Manager **só para este dataset**, sem a Dataset Quality API, e guardado em `META_CAPI_TOKEN` na Vercel |
| Webhook na Cakto | `Purchase para o Meta (CAPI)`, ativo, nos 5 produtos, evento "Compra aprovada", disparo **Agrupado** |
| `CAKTO_WEBHOOK_SECRET` | é o UUID que **a Cakto gera**, não o que a gente digita |
| Provado em produção | a Cakto entrega no endpoint (2 envios, 1 entregue, 258ms) e o Meta responde `events_received: 1` |
| Venda de 19/08 | recuperada à mão: o webhook só dispara em evento novo, e a CAPI aceita evento de até 7 dias. Pedido `6XF4ljB`, R$ 67, variante **abas**, sem UTM nenhuma |
| Não provado ainda | uma venda real ponta a ponta, que só a próxima compra mostra |

**Onde conferir se o evento chegou:** em **Eventos de teste → canal Site**, que responde na hora
e mostrou `Compra · Processado · Servidor`, uma marcada como `Desduplicado`. O relatório demora:
meia hora depois do envio, nem a visão geral nem o `/stats` mostravam nada, e cerca de uma hora
depois o `/stats` trouxe **`Purchase: 1`**. Não confundir atraso com evento perdido.

**A armadilha do botão "Testar":** ele manda um `purchase_approved` de verdade, e sem guarda um
clique viraria venda de mentira no pixel para sempre. O endpoint ignora o id e o e-mail do
payload de exemplo do painel, e foi conferido: depois de todos os testes, o pixel continua com
**zero** `Purchase`.

**Ao gerar o token, o pixel da NSM veio marcado junto** na opção recomendada (Dataset Quality
API), e a Meta avisa que essa escolha é irreversível. Por isso o token saiu pela opção **sem**
a Quality API, que não força a lista.

### O e-mail de acesso, e a premissa que estava errada

O 2.10 dizia "o e-mail manda só o link do mapa". Conferido no painel: a Cakto **não deixa
editar o corpo do e-mail**, o produtor só controla o campo do link, e a tela pós-compra do
upsell aparece em todo caminho de entrada do `/mapa`, inclusive para quem clica no link do
e-mail. Ou seja, não existe e-mail para escrever e o upsell já é alcançado. Sobra marcar a
origem do link, que é mexer no campo que entrega o produto para quem pagou, e por isso ficou
para ele decidir.

### A revisão da sessão de 19/08, e o que ela achou

Revisão do diff inteiro no fim do dia (18 commits, 20 arquivos). Limpo em: travessão (zero no
que entrou), promessa numérica desatualizada no texto visível, determinismo do build (gerar
duas vezes dá o mesmo byte) e console.

**Dois defeitos reais, os dois filhos da memória parcial que entrou hoje na LP:**

| O que acontecia | Por que nenhum teste pegou |
|---|---|
| O botão de voltar do quiz apagava a resposta do estado da página, mas não do que estava guardado. Sair e reabrir devolvia justamente a resposta desfeita | eu testei a retomada, não o desfazer |
| O refazer zerava a tela e não o guardado: clicar em refazer e fechar reabria no resultado antigo | idem |

**A lição:** ao ligar memória, todo caminho que **apaga** estado tem que apagar nos dois
lugares. Testar só o caminho feliz da retomada deixa o desfazer fora.

### O que eu pego em seguida

Ver "A próxima sessão começa por aqui", no topo: 2.11 (onde a pessoa abandona) e 2.5
(recuperação por WhatsApp). O 2.7 continua esperando existir um próximo produto, que é
justamente o que a aba `presentes` vai dizer, e a VSL (2.6) espera o Alison gravar.

### O que fechou no fim de 19/08

**Back redirect (2.9).** O pop-up não existia no histórico: o voltar levava a pessoa para fora
do site com o quiz pela metade. Agora o voltar fecha o pop-up, e com o quiz começado mostra
**uma vez** onde ela parou. Quem insiste sai.

**A memória parcial na LP, que o back redirect obrigou.** A retenção promete que nada se
perde, e isso era falso: a LP só salvava no fim do quiz e não lia nada ao reabrir. Agora salva
a cada clique e retoma na primeira pergunta sem resposta. **Promessa na tela é requisito de
produto**, não copy.

**One Belief (4.5).** A crença abre o hero das quatro LPs, com o mecanismo de cada variante, e
aparece na tela pós-compra e nas duas entregas. Nas entregas ela vai **sem** o nome do
mecanismo: `/mapa` e `/plano` são uma só para as quatro variantes, e citar "Regra das 3 IAs"
contradiria quem comprou o "Método das 3 Abas". Falta o criativo e o e-mail, que não são meus.

**Dois textos que mentiam**, achados de passagem: o hero e a seção do diagnóstico prometiam
"cinco perguntas", e o quiz tem 19.

### O QA do quiz inteiro, em 19/08

Duas perguntas do Alison: as perguntas são fáceis de entender, e dá para perceber que é preciso
comprar no fim?

**O botão de compra estava abaixo da dobra, e ninguém tinha medido.** No fim do quiz:

| Aparelho | O botão ficava |
|---|---|
| iPhone 14 (390x844) | 582px abaixo da dobra |
| Android pequeno (360x640) | 815px abaixo da dobra |
| Desktop (1280x900) | 415px abaixo da dobra |

É a correção pontual 2 da Frente 6 do playbook ("teve funil que não vendia só porque o botão
caía abaixo da dobra"), e era o item 1.8 da fila. **O que empurrava:** o bloco do código de
acesso, com 200px, no meio do caminho entre o resultado e a oferta. Ele serve a quem já
decidiu, não a quem está decidindo.

O fecho foi reordenado: o CTA sobe para logo abaixo do resultado, com o preço e uma linha do
que vem junto, e o código de acesso desce para depois da oferta, com o texto reescrito para
quem **não** vai comprar agora. Medido de novo: aparece sem rolar nos três aparelhos.

**Oito correções de clareza nas perguntas:**

| O que estava | Por que confundia |
|---|---|
| "Há quanto tempo você usa IA **no trabalho**?" e "Onde você **trabalha** na maior parte do tempo?" | perguntava de trabalho para quem tinha acabado de dizer que é vida pessoal |
| "Na minha vida pessoal, fora do trabalho" | única frase em primeira pessoa entre dez substantivos |
| "...é do tamanho de..." com a opção "Não é volume, é dificuldade" | a opção quebrava a frase da pergunta |
| "Quantas horas por semana **isso** te custa?" | "isso" sem antecedente claro |
| "Você já assinou alguma ferramenta que não usou?" com opções "Nunca / Uma / Mais de uma" | pergunta de sim ou não com opções de quantidade |

**E duas perguntas que não faziam sentido para iniciante viraram condicionais:** quem responde
"Nenhuma ainda" não recebe mais "quando a resposta volta genérica" nem "quantas vezes você
refaz o prompt". **Quem nunca usou IA agora responde 14 perguntas em vez de 19**, e o contador
fecha certo nos dois caminhos (14 de 14 e 19 de 19).

**O que o playbook cobria disso:** só o botão acima da dobra (Frente 6, correção 2). Sobre
clareza das perguntas ele não diz nada; o mais próximo é "não existe funil longo, existe funil
entediante".

### Vida pessoal virou trilha, em 19/08

A LP passou a falar com quem quer IA fora do trabalho (hospedagem, comparação de preço,
viagem), e aí apareceu o furo: **o quiz abria com "No que você trabalha?"**. Quem viesse pelo
anúncio de passagem caía num interrogatório profissional, e mesmo em "Outra área" as perguntas
eram "o que você entrega no fim do dia" e "como o seu trabalho chega em quem recebe".

Agora a primeira tela pergunta **"Onde a IA entra primeiro pra você?"**, com a 11ª opção
"Na minha vida pessoal, fora do trabalho" e trilha própria de 5 perguntas: o que quer resolver
(viagem, compra, estudo, papelada, casa, criação), o que trava na hora de comprar, o que fica
conferindo toda semana, o que queria receber pronto e com que frequência aparece.

**Efeito medido em 587.776 combinações** (era 493.696):

| Ferramenta | Antes | Depois |
|---|---|---|
| Claude | 92,8% | **83,0%** |
| Perplexity | 17,9% | **28,0%** |
| ChatGPT | 53,5% | 58,4% |
| n8n | 12,3% | 13,8% |
| Grok | 0,8% | 1,4% |

A trilha é de pesquisa, comparação e monitoramento, então ela quebra o domínio do Claude, que
é a resposta natural do trabalho. Continuam 19 perguntas por pessoa: a trilha nova tem o mesmo
tamanho das outras dez, senão o build para.

### O contador estava travado nas páginas pagas

Achado pelo QA da trilha nova, e **não era desta mudança**: em `/mapa` e `/plano` o contador
mostrava "1 de 19" em toda tela e a barra quase não saía do lugar. As duas contavam progresso
sobre a **fila do que ainda falta responder**, e a pergunta respondida sai dela na hora, então
a posição era sempre 1. A LP já estava certa, porque lá a fila é o caminho inteiro.

**Quem pagou é que via o contador quebrado.** Agora as duas contam sobre o caminho da pessoa,
respondido ou não: vai de "1 de 19" a "16 de 16" no teste, e o total só desce quando uma
resposta elimina perguntas de vez, que é o comportamento projetado.

### A LP parou de entregar o catálogo, em 19/08

A seção das 13 mostrava logo e nome de todas: quem lia saía com a lista pronta para pesquisar
sozinho, e o produto vende justamente saber quais são as suas 3. Agora:

| Quem | Como aparece |
|---|---|
| Claude, ChatGPT, Gemini, Perplexity | nome e logo, porque são prova emprestada e já são conhecidas |
| As outras 9 | categoria sem nome nem logo, com a silhueta do teaser do resultado |

**Medido em produção:** zero dos 9 nomes no HTML visível. Eles seguem dentro do `<script>`,
nos pesos do motor, que precisa rodar no navegador para o teaser existir. O paywall continua
sendo o de sempre: `passo`, `prompt`, `oq` e o custo completo nunca saem para o cliente.

Os casos de uso passaram a ser os perfis que o quiz atende (saúde, jurídico, contábil e uma
tarefa da vida, a passagem mais barata) e os temas antigos viraram chips. **Continuam sendo
pedidos, não depoimentos.**

Achado de passagem: a página prometia "cinco perguntas" e o quiz tem 19. Corrigido.

### A planilha, resolvida em 19/08 pelo navegador

O Apps Script foi recolado e **implantado como versão 2 na mesma implantação**, então a URL do
`ANALITICO_URL` continua valendo: trocar de implantação teria quebrado o envio de todas as
páginas.

**O cabeçalho só nasce junto com a aba**, então recolar o código não conserta aba existente. E
acrescentar as três colunas no fim não servia: o cabeçalho antigo tinha `tarefa`, que virou
pergunta de trilha, e a ordem do `appendRow` mudou junto, então o dado novo entraria embaixo do
rótulo errado. A saída foi arquivar: `diagnosticos` → `diagnosticos ate 19-08` (67 linhas) e
`leads` → `leads ate 19-08` (4 linhas). O JSON inteiro de cada linha antiga continua na coluna
`bruto`.

**Conferido com POST real** nos dois tipos: a `diagnosticos` nasceu com 21 colunas, incluindo
`trilha`, `descreveu` e `utm`, e a `presentes` com as 8 dela. As duas linhas de teste foram
apagadas depois, e o arquivo temporário que rodou a arquivagem foi excluído do projeto.

**Armadilha do instrumento:** `curl -L` num Web App do Apps Script devolve a página "Não foi
possível abrir o arquivo", porque o redirect do Google converte o POST em GET. **A gravação
acontece assim mesmo.** Conferir sempre pela planilha, nunca pela resposta do curl.

### A venda dentro da entrega, feita em 19/08

O `/mapa` deixou de ser só entrega e passou a ter três peças novas, todas geradas do
`dados.json` como o resto:

| Peça | O que é | Quando aparece |
|---|---|---|
| Tela pós-compra (2.3) | A oferta inteira do upsell, com a conta R$ 197 menos os R$ 67 já pagos | Uma vez, entre a identificação e o mapa |
| CTA de ascensão (2.4) | O mesmo preço e o mesmo link, em bloco curto | Sempre, no fim da entrega |
| Presente (2.8) | Cinco opções mais uma saída aberta, gravando na aba `presentes` | Sempre, depois do CTA |

**O crédito é do comprador, não da tela.** O texto que estava no `dados.json` prometia R$ 197
"fora desta tela", o que é escassez inventada, proibida no projeto. Quem pagou os R$ 67 tem o
abatimento sempre que voltar. Os R$ 197 valem para quem chega direto no pacote.

**Onde a oferta mora, e por quê.** A entrega da Cakto é URL fixa e não tem redirect
pós-compra, então uma página `/obrigado` exigiria trocar o link dos quatro produtos e deixaria
de fora quem já comprou. Dentro do `/mapa` a oferta sai no fluxo real sem tocar na plataforma.

**A entrega nunca fica atrás da venda:** o botão de abrir o mapa tem o mesmo peso do de
comprar, comprar também libera o mapa (o checkout abre em outra aba) e a tela some para sempre
depois da primeira vez (`qia:oto`).

**O produto na Cakto:** `Sua primeira semana pronta`, R$ 130,00, entrega em `/plano`, checkout
`https://pay.cakto.com.br/j79id6y_1051180`, em `_build/config.py` como `CHECKOUT_UPSELL`.
Conferido campo a campo contra o "Qual IA Usar?" pela API interna: pixel 827402089420392, os
dois gatilhos de `Purchase` ao gerar Pix e boleto desligados (**nascem ligados**), PicPay fora,
Pix em primeiro, produtor "Noah.ai". A página pública do checkout foi aberta e conferida.

**QA, em três voltas contra o build local** (sem gastar chamada de API e com o POST do presente
interceptado, para não sujar a planilha):

| Volta | O que os 15 testes disseram | O que o print mostrou |
|---|---|---|
| 1 | 15/15 | O campo "cola o seu código" ficava de ruído em cima da oferta, e o botão do presente não sumia depois do voto |
| 2 | 15/15 | A seta do CTA de ascensão quebrava sozinha na segunda linha |
| 3 | 16/16 | Aprovado |

### O que a regressão em produção pegou, e que não era da minha mudança

A rodada contra produção deu **24 de 25**, e a única falha foi na entrega paga, não nas peças
novas: o modelo escreveu, dentro de um `PROMPT` que a pessoa copia, *"roteiros que eu mesmo
público publiquei"*. Marca de gênero masculino, e ainda com uma palavra sobrando.

A regra 7 do `SISTEMA` já proíbe isso com todas as letras, inclusive citando "eu mesmo".
**Instrução não é garantia**, então entrou um corte determinístico no cliente, igual ao que já
existia para preço: bloco que traz `eu mesmo` ou `eu mesma` volta ao texto de fábrica, e isso
agora vale também para os prompts, que o guarda de preço não cobria. Fica só o que é
inequívoco: "sozinho" quase sempre é a ferramenta ("ele roda sozinho"), não a pessoa.

**Conferido com stream simulado** por `page.route`, do mesmo jeito que o retry foi conferido:
uma resposta com os oito blocos, o `PROMPT1` contendo "eu mesmo". O prompt volta ao de fábrica,
o botão de copiar continua servível e os outros sete blocos sobrevivem. O regex da regressão
também foi ajustado: ele acusava "ele pesquisa sozinho" como defeito, o que é falso alarme.

**O preço dessa proteção:** quando ela dispara, o prompt de fábrica tem lacuna do tipo
`{sua profissão}`. Genérico é pior que personalizado, e melhor que errado.

**Dois defeitos que só o print pegou, e o porquê:** `hidden` não esconde elemento cujo CSS
declara `display` (é o caso de `.btn`), então o botão continuava lá depois de enviado; e o
`entrar-codigo` só sumia em quem entrava por código ou memória, nunca em quem respondia o quiz
ali mesmo. Os dois eram invisíveis para teste que olha só `hidden`.

### O que a primeira venda ensinou

A compradora respondeu no celular, abriu o e-mail no computador e refez as 23 etapas depois de
pagar. Nenhum QA meu pegava, porque eu sempre testava no mesmo navegador. Daí vieram o código
de acesso e a memória parcial. **Ninguém aqui deve tratar "outro aparelho" como caso de borda.**

### 1b. A entrega, endurecida em 19/08

Três defeitos fechados depois de QA no navegador, em produção:

| Era | Virou |
|---|---|
| O `SISTEMA` chamava a pessoa de "ela" 13 vezes, e o modelo devolvia isso nos prompts em primeira pessoa | Instruções falam de "a pessoa" e "quem respondeu", mais a regra 7 proibindo adjetivo e particípio que concordem com quem fala |
| O relógio do `redigir()` abortava o stream em 45s, e a resposta leva de 34 a 44s: o `CORTE` chegava depois do abort | Teto de 75s, acima do `maxDuration` de 60s da function |
| Resposta incompleta caía direto no texto de fábrica | Uma segunda tentativa antes do fallback; 429 e 503 saem sem insistir |

**O "7 de 8 blocos" não era omissão do modelo, era o relógio do cliente.** Quem mede pela API
direta não vê esse defeito, porque o corte acontece só no navegador. Foi preciso rodar o quiz
inteiro no browser para achar.

**Medido no fim:** 8 de 8 blocos, nenhuma lacuna `{}`, nenhuma marca de gênero, console limpo,
31s até a entrega completa (abertura em 6s, corte em 28s). O retry foi conferido à parte, com
resposta truncada simulada por `page.route`: dispara a segunda chamada e preenche os 8 blocos.

**Armadilha do instrumento, para não repetir:** `waitForFunction` do Playwright roda em
`requestAnimationFrame`, que congela quando a janela perde o foco, e por isso deu "não chegou
em 150s" com o bloco preenchido na tela. Medir stream longo pede polling explícito com
`evaluate`.

### 1c. O caminho do lead, percorrido em 19/08

Rodado no navegador, em mobile (390x844), nas quatro variantes, sem finalizar compra:

| Etapa | Resultado |
|---|---|
| LP carrega com UTM | `PageView` dispara |
| CTA abre o pop-up | `ViewContent` com o `content_name` da variante, que é como o teste de nome se lê |
| Quiz, 18 passos | Sem erro de console em nenhuma das quatro |
| Resultado | Teaser correto: custo à vista, nome e logo ocultos |
| Link de compra | O da própria variante nas quatro, com a UTM anexada |
| Clique | `InitiateCheckout` dispara e abre em aba nova (`target="_blank"`) |
| Checkout | Produto certo nos quatro, R$ 67,00, e a UTM sobrevive até lá |

**A correção da entrega vale para as quatro variantes**, porque `/mapa` é uma página só e
`/api/mapa` é uma function só. As LPs não chamam a IA: nenhuma das quatro referencia
`/api/mapa`, já que a redação só existe depois da compra.

**Três achados que não são defeito, mas devem ser sabidos:**

1. **`SubscribedButtonClick`**: o pixel dispara um por clique de botão, 18 numa sessão de
   quiz. É rastreamento automático nativo do Meta, não vem do código, e não polui `PageView`,
   `ViewContent` nem `InitiateCheckout`. Desliga no painel do pixel, se incomodar.
2. **O checkout destaca o parcelamento**: "12 X de R$ 6,92", com "R$ 67,00 à vista" ao lado.
   Existe ainda uma "Taxa de serviço" de R$ 0,99 no resumo, que fecha em "Total 12x de R$ 7,00".
3. ~~**PicPay ativo na tela de pagamento**~~ **desativado em 19/08, nos quatro produtos.**
   Como a Cakto não expõe o toggle do `fbPicpayPurchaseTrigger`, que dispara `Purchase` ao
   gerar a cobrança em vez de no pagamento, a saída foi tirar o método: Produtos → o produto →
   Configurações → Métodos de pagamento → clicar no card do PicPay → Salvar Produto. Conferido
   nas quatro páginas públicas de checkout: sobraram **PIX, Cartão, Apple Pay e Google Pay**.
   O `fbNubankPurchaseTrigger` continua ligado e agora é inócuo, porque não existe método
   Nubank na lista da Cakto.

### 2. Colar o Apps Script de novo

`_docs/apps-script-captura.js` ganhou três colunas: `trilha` (as perguntas de trilha não têm
coluna fixa, vão como `pid=resposta`), `descreveu` (o que a pessoa escreveu quando nenhuma
opção era a dela, o canal que diz qual opção falta no quiz) e `utm`, que é da sessão passada e
nunca foi colada.

O cabeçalho só é escrito quando a aba nasce, então a aba `diagnosticos` que já existe não
ganha as colunas sozinha: ou renomeia a antiga, ou adiciona na mão. O `bruto` continua
gravando o payload inteiro, então nada se perde no meio tempo.

### 3. Compra de teste de R$ 67

Continua sendo o próximo passo de produto e agora vale mais: além de provar que o e-mail
chega e que a Cakto repassa parâmetros na URL, é a única forma de ver o mapa escrito pela IA
no fluxo real de um comprador, em outro aparelho. Use o checkout da `abas`, `regra` ou
`stack`, que nunca receberam venda.

### 4. A LP, que não foi tocada nesta sessão

- **A seção "as 9 ferramentas"** entrega o catálogo de graça: a pessoa lê os nomes e vai atrás
  sozinha. Com 13 ferramentas e a camada de recursos, agora dá para virar tensão. O desenho:
  manter com nome as 4 que todo mundo já conhece (superestrutura, prova emprestada) e trocar
  as outras 9 por categoria sem nome ("a que narra com a sua voz", "a que monta a
  apresentação", "a que roda a tarefa sem você").
- **Auditoria das 9 seções** pela régua das nove vendas do Makepeace (atenção, visualização,
  credibilidade, autoridade, problema, história, solução, conveniência, valor, mais escassez).
  Seção que não faz nenhuma delas sai. Como variante de teste A/B, nunca por decreto: é o que
  o plano manda.
- **Prova social só real.** O que existe hoje sem depender de aluno: número de diagnósticos
  concluídos (está na planilha), print de conversa verdadeira, e a demonstração na tela, que
  o playbook considera mais forte que depoimento. A IA escrevendo o mapa ao vivo é a
  demonstração mais forte que o produto tem, e não existia antes desta sessão.
- **30 a 50 etapas.** O quiz tem 18 por pessoa. Com a ramificação de pé, dá para chegar a 30
  com mais duas perguntas por trilha, mais dois breaks e o fechamento com loading e espelho
  das respostas, que continua não existindo.

## O que entrou em 19/08

### Diagnóstico ramificado em 10 áreas

De 6 para 10 áreas, cada uma com 3 perguntas da profissão. "Outra área" era um saco onde caíam
médico, advogado, contador e engenheiro; saíram de lá **saúde e consultório**, **jurídico**,
**contábil e financeiro** e **projeto e obra**. Continuam 16 perguntas por pessoa, então o
quiz não ficou mais longo, mas a segunda tela já é sobre a profissão de quem responde.

**Saída aberta:** toda pergunta de tarefa termina com "Nenhuma dessas, a minha é outra", que
abre um campo de uma linha em vez de avançar. O texto não vota no motor (sem informação, sem
voto), vai para a redação da IA delimitado por etiqueta e cai na planilha em `descreveu`. O
servidor só aceita esse texto na pergunta em que a pessoa marcou a última opção, corta em 120
caracteres e tira quebra de linha e colchete.

**Três perguntas perderam o voto** (`tempo_ia`, `generica`, `estilo`). Continuam no quiz como
micro-sim e alimentam a redação, mas nenhuma diz qual ferramenta serve: o voto delas só
empilhava ponto nas quatro generalistas.

### Catálogo de 9 para 13, por categoria ausente

O quiz perguntava sobre apresentação e respondia Gemini, que não monta slide.

| Entrou | Preço, conferido no site oficial em 19/08/2026 |
|---|---|
| **Gemini Notebook** | grátis na conta Google, com limite diário |
| **Gamma** | Free resolve; Plus R$ 30/mês no anual (cobra em real) |
| **ElevenLabs** | Free com 10 mil créditos; Starter US$ 6; Creator US$ 22 |
| **n8n** | grátis se hospedar; Starter €20/mês |

Fechou também a pendência antiga: **Higgsfield** com Plus a US$ 49/mês no anual (1.000
créditos) e Ultra a US$ 129/mês. **Não há mais custo não conferido dentro do produto pago.**

Dois achados da conferência: o **NotebookLM virou Gemini Notebook** em 16/07/2026 e o
**ChatGPT Atlas foi descontinuado em 09/08/2026**. Escrever de cabeça teria colocado erro
dentro da entrega paga.

### A camada de IA, conforme o ADR-0001

`api/mapa.mjs` na Vercel, Claude Opus 5. O motor recalcula a stack **no servidor** e o
navegador manda só índices de resposta, então ninguém escreve o que quiser dentro de uma
chamada paga. A IA escreve por cima do mapa que já está na tela: abertura, o porquê de cada
card, o prompt sob medida e o corte.

- **Fallback é o estado inicial, não um plano B.** Bloco que a IA não escreve fica com o texto
  de fábrica, e bloco que ela não terminou volta para ele.
- **"Terminou" não é o stream fechar, é o último marcador chegar.** A conexão pode cair e o
  navegador dar a leitura por encerrada mesmo assim. Sem isso, um prompt cortado no meio
  ficaria na tela com cara de pronto, e é o prompt que a pessoa copia. Testado cortando o
  stream no meio do prompt.
- **Preço só sai de onde o produto escreveu.** Bloco de justificativa que citar valor é
  descartado.
- **Rate limit** de 6 por IP por hora e 120 por instância, na memória da function.
- **O texto fica guardado no aparelho:** reabrir o mapa não gasta chamada nem espera nova.

### Recursos dentro da ferramenta

Cada card ganhou "Dentro dela, o que quase ninguém usa": Claude com Projects e Cowork, ChatGPT
com modo de voz, deep research e agent mode, Gemini com Deep Research, Canvas e Gems, Gemini
Notebook com o resumo em áudio. Conferido no fabricante em 19/08/2026, e a IA foi instruída a
escolher qual serve para o caso da pessoa e a **nunca citar recurso fora da lista**.

**Por que isso importa mais que o catálogo:** varrendo todas as combinações do motor, os mapas
feitos só de Claude, ChatGPT, Gemini e Perplexity caíram de **69,8% para 49,4%**. Só que,
zerando o tronco inteiro, o piso é **45,8%**: para um advogado que escreve petição, Claude é
mesmo a resposta certa. Abaixo disso só se desce com exotismo mentiroso. Logo, o valor não
pode ser "ferramenta que você nunca ouviu": é a ordem, o corte e o que fazer dentro da que ele
já tem.

### Upsell redesenhado

A IA no front passou a entregar duas das quatro alavancas que o plano reservava para o upsell
de R$ 197. A fronteira nova, em uma frase: **o front escreve para o seu perfil, o upsell roda
no seu material**. Sem VSL e sem aula gravada, por decisão do Alison: os quatro entregáveis
saem do mesmo motor e da mesma function, então o upsell não depende de gravação. Detalhes e o
roteiro da VSL (guardado caso um dia entre) no plano do vault.

### QA

Onze passadas de browser: as 10 trilhas, a saída aberta na LP e no mapa, API caindo, stream
cortado no meio do prompt, cache na segunda visita, injeção pelo campo livre e o fluxo LP →
`/mapa` com a memória. Nenhum erro de console além do 404 do Web Analytics, que é local. O
quiz sai **idêntico byte a byte nas 4 variantes**, então o teste de nome segue limpo.

### O estado de hoje, para não ter que descobrir de novo

| Variante | Produto na Cakto | LP | Checkout |
|---|---|---|---|
| controle | Qual IA Usar? | `/` | `https://pay.cakto.com.br/3fxqxg5_1049811` |
| abas | Método das 3 Abas | `/abas` | `https://pay.cakto.com.br/32hjw7j_1049893` |
| regra | Regra das 3 IAs | `/regra` | `https://pay.cakto.com.br/8t2cigd_1049903` |
| stack | Stack Mínima | `/stack` | `https://pay.cakto.com.br/3dtj6z8_1049909` |

Domínio: **`https://diagnostico.noahai.com.br`** (o `.vercel.app` responde 308 para ele).
Os 4 produtos são idênticos, exceto nome e página de vendas.

**Onde ler o resultado do teste de nome:** planilha `Qual IA Usar? — Diagnósticos e Leads` (nome literal no Drive),
aba `diagnosticos`, coluna `origem` (`site`, `abas`, `regra`, `stack`). Tem 6 linhas de teste
que podem ser apagadas: as com origem `teste` e as do "Teste do Claude".

### Tracking, ligado em 18/08

Pixel do Meta **827402089420392**, o mesmo nos quatro. Um pixel só aprende junto;
quatro pixels separados fragmentariam o aprendizado e não somariam.

| Onde | Evento | Dispara quando |
|---|---|---|
| LP | `PageView` | a página carrega |
| LP | `ViewContent` | o pop-up do diagnóstico abre |
| LP | `InitiateCheckout` | clique em qualquer link do `pay.cakto.com.br` |
| Cakto | `Purchase` | a Cakto dispara, **só no pagamento aprovado** |

`ViewContent` e `InitiateCheckout` levam `content_name` com o nome da variante, e
o `PageView` se separa pela URL. É assim que o teste de nome se lê no Events
Manager sem depender da planilha.

**O que estava errado e foi corrigido:** a Cakto vem de fábrica com "Disparar
evento Purchase ao gerar um pix" e o mesmo para boleto **ligados**. Pix gerado não
é Pix pago: em low ticket com 80% de Pix isso infla Purchase, mente o ROAS para
cima e ensina o algoritmo a comprar quem gera cobrança e some. Desligado nos
quatro produtos.

**Fica pendente:** os gatilhos equivalentes de **PicPay e Nubank** continuam
ligados (`fbPicpayPurchaseTrigger`, `fbNubankPurchaseTrigger`) porque a interface
da Cakto não expõe esses dois toggles, só Pix e boleto. Como é igual nos quatro
produtos, não distorce a comparação entre variantes, apenas infla um pouco o total
se alguém pagar por PicPay.

**Ainda não feito, de propósito:** CAPI (o campo de token existe em cada pixel, na
engrenagem da linha), domínio verificado, e GA4. CAPI sem dedup por `event_id`
conta a mesma venda duas vezes. Entra depois que a compra de teste confirmar que o
`Purchase` do browser chega limpo.

O `/mapa` **não** recebeu pixel: é página de entrega pós-compra, e `PageView` de
comprador ali só sujaria o público.

### Domínio próprio, ligado em 18/08

`diagnostico.noahai.com.br`, apontado no projeto `qual-ia-abrir` da Vercel. O
domínio raiz `noahai.com.br` já era do Alison e o DNS já estava na Vercel, então
não houve compra nem espera de propagação.

**Por que subdomínio e não caminho:** `noahai.com.br/diagnostico` obrigaria o site
principal a rotear o produto, acoplando dois projetos que deployam separado.

**Por que `diagnostico` e não `stack` ou `qual`:** é a única palavra que não
favorece nenhuma das quatro variantes. Subdomínio com o nome de uma delas daria
vantagem de marca a essa variante e o teste passaria a medir nome mais domínio.

**Domínio verificado no Business Manager** da Nutra Seu Marketing, por registro
TXT de DNS (`facebook-domain-verification=...`, criado via `vercel dns add`).
Verificar o raiz cobre o subdomínio, e não exigiu tocar no site principal. A rota
por metatag foi descartada: ela teria que ir no HTML de `noahai.com.br`, que é
outro projeto.

**Sobre o pixel:** ele vive no portfólio **Nutra Seu Marketing** (não no NOAH.AI),
com o nome `Pixel - 001 - FESTIVAL HIT`, criado em 05/03/2024 e sem atividade há
mais de 90 dias. Foi reaproveitado de propósito pelo Alison por já ter vendido. A
conta de anúncios com acesso a ele é a `CA - 001 - INFO` (828815582355498). A
correspondência avançada automática está **desativada** e vale ligar.

### A fila depois dos checkouts

| # | Tarefa | Depende de | Quem |
|---|---|---|---|
| 1 | ~~**3 produtos na Cakto** e os links em `config.py`~~ **feito em 18/08** | nada | Claude conduz no browser |
| 2 | **Compra de teste de R$ 67** em si mesmo | item 1 | Alison paga, Claude confere a entrega e se a Cakto repassa parâmetros na URL |
| 3 | **Unificar a marca** do logo, hoje "qual ia abrir" contra "Qual IA Usar?" no checkout | nada | Claude, 3 minutos |
| 4 | **Custo do Higgsfield** | conferir no site da ferramenta | Alison confere, Claude atualiza `dados.json` |
| 5 | **Conteúdo dos 7 dias** do upsell de R$ 197 | método do Alison | os dois: Claude estrutura, Alison revisa a voz |
| 6 | **Página `/plano`** da entrega do upsell | item 5 | Claude, ~2h |
| 7 | **Ramificação do diagnóstico** por área, com perguntas próprias em cada trilha | nada | Claude, uma sessão inteira |
| 8 | **Recuperação por WhatsApp** (+20% de faturamento na operação de referência) | item 1 (webhook) | Claude no n8n |
| 9 | ~~**domínio próprio**~~ **feito em 18/08**; falta **Web Analytics** da Vercel | painel da Vercel | Alison |
| 10 | **CAPI, domínio verificado e GA4** | item 2 (ver o Purchase chegar) | Claude |

**Não ligar o upsell no funil antes do item 5.** Vender e não conseguir entregar é
reembolso e reclamação, e queima a autoridade que é o ativo do produto.



Atualizado em 19/08/2026, no fim da sessão que ligou a venda dentro da entrega, abriu o quiz para vida pessoal e fez o QA do funil inteiro.

## O que a página é hoje

LP de venda do **Qual IA Usar? (R$ 67, ancorado em R$ 147)**, modelada na LP do meuassessor.com. Nove seções:

1. **Hero** com mockup de iPhone rodando uma conversa de WhatsApp (o produto trabalhando)
2. **Faixa** de argumentos de compra
3. **Problema** em 4 sintomas
4. **Casos de uso**: 4 cards com pedido em áudio e resposta oculta, mais 6 chips
5. **Diagnóstico** (o pop-up), chamada com os 3 passos
6. **Escopo**: as 9 ferramentas, só logo e nome
7. **Órbita** radial das categorias
8. **A conta do erro**: US$ 240 / 399 / 700+ por ano contra R$ 67 uma vez
9. **Oferta** com preço, 5 entregáveis e garantia, depois FAQ e fecho

Decisão do Alison em 18/08: **nada de graça**. Saíram a lista pública das 24 tarefas, os
desempates, os papéis das cinco principais, as descrições das ferramentas e o bloco de captura
gratuita. O resultado do diagnóstico é teaser com silhuetas.

## O que entrou em 18/08 (aplicação do playbook de low ticket)

Derivado de dois podcasts do VTurb (Tiago Filemon sobre funil de VSL, e a mesa de Davi
Meurer, Kauê Puglies e Slender sobre low ticket). O plano completo está no vault, em
`01 - Projects/Qual IA Usar/Qual IA Usar - Plano Low Ticket.md`.

| Mudança | Por quê |
|---|---|
| Oferta cortada de 8 para 5 entregáveis | promessa boa demais pelo preço derruba conversão em low ticket, e "Atualizações inclusas" era o produto do upsell dado de graça no front |
| Preço de R$ 47 para R$ 67, âncora de R$ 97 para R$ 147 | decisão do Alison; a âncora subiu junto porque 47 contra 97 dava só 31% de desconto |
| Diagnóstico de 5 para 16 passos (14 perguntas + 2 breaks) | cada clique é um micro-sim; a operação de referência roda 30 a 50 etapas |
| Mecanismo nomeado "Regra das 3 IAs" | critério FHC (fácil, hype, curioso); o nome do produto segue "Qual IA Usar?" até o teste seco decidir |
| CTA "Receber meu diagnóstico personalizado" | nunca "iniciar quiz"; posicionar como conteúdo de valor |
| Entrega paga em `/mapa` | mesmo diagnóstico sem paywall: custo real, primeiro passo e prompt de cada ferramenta |
| Memória do diagnóstico | o comprador não refaz o quiz dentro do `/mapa`, no mesmo aparelho |
| Analytics anônimo | saber qual perfil responde, sem nome nem WhatsApp |
| Checkout Cakto | Pix a 0% + R$ 2,49 contra 8,99% da Kiwify: R$ 5,35 a mais por venda no bolso, com 80% de Pix |

## Arquitetura depois desta sessão

```
_build/config.py       constantes de deploy (as 4 URLs e o preço), lidas pelos dois geradores
_build/motor.js        cálculo da stack, injetado nas duas páginas (nunca divergem)
_build/sessao.js       memória no navegador + envio anônimo
_build/gerar.py        → public/index.html   (venda, com paywall)
_build/gerar_mapa.py   → public/mapa/index.html (entrega paga, sem paywall)
```

Build: `python3 _build/gerar.py && python3 _build/gerar_mapa.py && vercel deploy --prod --yes`

## Pendências, em ordem de bloqueio

| # | Pendência | Onde | Impacto |
|---|---|---|---|
| 1 | ~~**`ANALITICO_URL` vazia**~~ preenchida em 18/08 | `_build/config.py` | Falta conferir na planilha se as linhas estão chegando |
| 2 | **Produto do upsell não existe** | fora do repo | O bloco `upsell` do `dados.json` promete plano de 7 dias e prompts preenchidos. **Não ligar o upsell no funil antes de o conteúdo existir** |
| 3 | **Compra de teste** | Cakto | Nunca foi feita. Agora que a entrega por e-mail aponta para o `/mapa`, é a única forma de confirmar que o e-mail chega e se a Cakto repassa parâmetros na URL (de que depende o cruzamento em outro aparelho) |
| 4 | **Custo do Higgsfield** | `dados.json` → `diagnostico.acesso` | Único não conferido, e agora aparece **dentro do produto pago** |
| 5 | **`CAPTURA_URL` vazia** | `_build/config.py` | O passo de nome e WhatsApp não aparece. Menos urgente que o item 1, porque o anônimo já responde as perguntas de produto |
| 6 | ~~**Web Analytics**~~ ligado em 19/08 | painel da Vercel | Plano Hobby: 50 mil eventos/mês, **a quebra por UTM é paga** (Web Analytics Plus). Origem do tráfego se lê em Referrers aqui, e por UTM no Events Manager e na planilha |
| 7 | **Ramificação do diagnóstico** | motor JS | Perguntas diferentes por área. É o que falta para a personalização ser real, e a maior mudança estrutural restante |
| 8 | **Seção de autoridade** | seção `#prova` | Decisão do Alison sobre quais credenciais vão para o ar |
| 9 | ~~**Domínio próprio**~~ resolvido em 18/08 | Vercel | `diagnostico.noahai.com.br`, verificado no Meta |

## Código morto conhecido (não tocar sem motivo)

`gerar.py`, linhas 239 a 246: a variável `oferta_cta` é montada e nunca usada no HTML. Por
isso os dois botões de compra da página saem com o mesmo texto, os dois vindos de
`botao_compra`. Já era assim antes desta sessão.

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

## Bug que aconteceu duas vezes nesta sessão

Recortar o template por `t.index(inicio) ... t.index(fim)` apagou tudo que estava no meio.
Aconteceu ao reescrever o rodapé: levou junto o `<dialog>` do diagnóstico **e a seção de
oferta inteira** (preço, entregáveis, botão de compra). Passou porque a bateria de QA
verificava layout, contraste e console, e bloco ausente não gera erro.

**Antes de cortar por índice:** listar os ids que devem sobreviver no intervalo.
**Depois de gerar:** rodar o inventário de peças e o fluxo do pop-up, não só o de layout.

## Comparativo de checkout, medido em 18/08/2026

Custo por venda de R$ 67, no mix de 80% Pix e 20% cartão que é a regra em low ticket:

| Plataforma | Pix | Cartão | Custo médio | Efetivo |
|---|---|---|---|---|
| **Cakto** (escolhida) | 0% | 4,99% | **R$ 3,16** | 4,7% |
| Eduzz | 4,90% | 4,90% | R$ 5,77 | 8,6% |
| Kirvano | 7,49% | 7,49% | R$ 7,02 | 10,5% |
| Ticto | 6,99% | 6,99% | R$ 7,17 | 10,7% |
| Hotmart | 9,9% | 9,9% | R$ 7,63 | 11,4% |
| Kiwify | 8,99% | 8,99% | R$ 8,51 | 12,7% |

Todas cobram R$ 2,49 fixo, menos Kirvano (R$ 2,00) e Hotmart (R$ 1,00). Taxas conferidas nas
centrais de ajuda oficiais. A recomendação anterior deste arquivo (Kiwify, com números que
não batiam) estava errada e foi substituída.

**Ressalva:** a Cakto é a mais nova da lista e tem reclamações de bloqueio de conta no
Reclame Aqui. O índice de solução não foi verificado, o site bloqueia leitura automatizada.

## Origem do tráfego, ligada em 19/08

A UTM que vem na URL é lida uma vez por `origemTrafego()` (`_build/sessao.js`), guardada em
`localStorage` sob `qia:org` e usada em dois lugares: vai no payload anônimo para a planilha e
decora os links do checkout. Regra de last touch: parâmetro novo sobrescreve o antigo, e
visitante sem parâmetro nenhum não ganha query suja no link.

Onde ler cada etapa do funil por origem:

| Etapa | Onde ler | Como |
|---|---|---|
| Visita | Vercel Analytics → Referrers | O YouTube web aparece; no app o referrer some, e aí o Pixel cobre |
| Visita com UTM | Events Manager → PageView | Filtro pela URL do evento, que já carrega a query |
| Diagnóstico completo | Planilha, aba `diagnosticos` | Coluna `utm`, e o JSON da coluna `bruto` como reserva |
| Checkout aberto | Events Manager → InitiateCheckout | Disparado na LP, com a URL de origem |
| Venda | Cakto | **Não confirmado.** A UTM chega na URL do checkout; se ela grava, só a compra de teste (pendência 3) diz |

Para a coluna `utm` aparecer com título na planilha, recolar `_docs/apps-script-captura.js` no
Apps Script. Sem recolar nada se perde: o valor continua indo dentro da coluna `bruto`.

## Próximo passo sugerido

Fazer a compra de teste. É o que falta para fechar o funil de ponta a ponta.
