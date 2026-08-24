# Instagram Direct no n8n: máquina de estados

> **Standard Access basta. Confirmado em 21/08/2026.** O envio pela API foi testado
> contra um destinatário inexistente e a Meta respondeu `code 100 / subcode 2534014`
> ("não foi possível encontrar o usuário"), ou seja, falhou no destinatário e **não**
> na autorização. Falta de permissão teria devolvido código 10 ou 200 antes disso.
> **Nada de App Review.**

Responde automaticamente quem já está em conversa com você no Direct, encaminha
para o [Qual IA Usar](https://diagnostico.noahai.com.br/) e concilia a venda de volta.
Criado em 21/08/2026.

## O que está no ar

| Workflow | ID | Estado |
| --- | --- | --- |
| `IG DM | 1/2 · Responder Direct (máquina de estados)` | `jxKgH8EFgHspLnPd` | **ativo** |
| `IG DM | 2/2 · Conciliar vendas e resumo do dia` | `C0byVjlssrzKHxI7` | **ativo** (20h) |
| `IG DM | 0 · DIAGNÓSTICO do acesso à API` | `J5xCChVkyx8vkcPX` | manual |
| `IG DM | 3 · Renovar token do Instagram` | `hb7Cm2hEXr7smnaz` | **ativo** (seg 4h) |

Planilha de estado: **Instagram Direct · Máquina de Estados (Qual IA Usar)**
`1lqwrmR0GHcoyjXbip3_kM-CRgWp2BWT0dJvBZXeEy1k`, aba **`leads`** (id `1356899938`).

> ⚠️ A aba **não** é `gid=0`. Planilha criada por conversão de CSV nasce com id
> aleatório, e o node do n8n quer o **id puro** (`1356899938`), não `gid=1356899938`.
> Os dois erros dão a mesma mensagem enganosa: `Sheet with ID ... not found`. Isso
> teria quebrado o fluxo só na primeira mensagem real.

URL do webhook (produção), a mesma para GET e POST:

```
https://n8n.nsmvps.com.br/webhook/ig-direct-dccfeca99e6634455f57b8374ffd36fc
```

> Essa URL é o segredo do endpoint. Ela tem 128 bits de aleatoriedade e é o que
> impede terceiros de disparar DM em seu nome. Não publique em lugar nenhum. Se
> vazar, troque o path nos dois nós de webhook e reassine no painel da Meta.

## Checklist para ligar

> Passos 1 a 4 concluídos em 21/08/2026, mais a publicação do app. App `noahai Direct` (`1759486621623121`),
> app do Instagram `1739189287302809`, conta `@aalisonaraujo`
> (id `28015783988105112`, user_id `17841400503107410`, tipo MEDIA_CREATOR),
> permissões adicionadas, convite de testador aceito, token gerado e o app **inscrito
> no campo `messages`** (`subscribed_apps` confirmou). **App publicado**, política de
> privacidade no ar em `/privacidade` e as duas URLs salvas no painel (privacidade e
> exclusão de dados, esta apontando para `/privacidade#exclusao`).
> **Fluxo COMPLETO e no ar em 21/08/2026.** Os dois workflows ativos, webhook
> verificado pela Meta (execução `success` às 15:40) e a conta inscrita no campo
> `messages`. Falta só o teste ponta a ponta com uma DM real.

**1. Conferir que a conta é profissional**

No app do Instagram: Configurações → Tipo de conta. Precisa ser **Empresa** ou
**Criador de conteúdo**. Conta pessoal não funciona em nenhuma API da Meta desde
o fim da Basic Display, em dez/2024.

**2. Criar um app próprio** (não reusar o do Clinic.IO)

O webhook do Instagram é configurado **por app**, e só cabe uma callback URL por
app. Apontar o n8n no app `Clinic.IO` sobrescreveria o webhook do Clinic.io e
derrubaria a integração de um cliente em produção. Como o app próprio é
necessário de qualquer jeito, o teste já roda nele, que é mais fiel: app novo
nasce em Standard Access, exatamente o que queremos medir.

developers.facebook.com → Meus apps → Criar app.

- Nome: algo como `noahai Direct`
- Ao escolher o portfólio comercial, **ache pelo ativo, não pelo nome**: você tem
  dezenas de portfólios e os nomes se parecem
- Adicionar produto: **Instagram**

**3. Conectar a conta e gerar o token**

No painel do app: **Instagram → API setup with Instagram login**.

1. *Add an Instagram account* → entrar com `@aalisonaraujo` → autorizar
2. *Generate token* → copiar

O token do painel vale **60 dias**. Se aparecer um de 1 hora, é o de curta
duração e o diagnóstico vai acusar código 190.

> **Isso é automático desde 21/08.** O workflow `IG DM | 3` roda toda segunda às 4h,
> renova o token na Meta e faz `PATCH` na credencial pela própria API do n8n. Você
> recebe no Telegram em caso de falha. Não precisa anotar nada na agenda.

**4. Guardar o token na credencial do n8n**

O token vive na credencial **`Instagram Graph | noahai Direct`** (`H7gnqM8GcSzltGhf`),
do tipo Header Auth, e **não** em variável de ambiente. Isso foi uma correção
deliberada: credencial é lida do banco a cada execução, então **trocar o token não
exige reiniciar o n8n** e não derruba os 43 workflows ativos da VPS. Rotacionar em
60 dias é editar um campo na interface.

O verify token do webhook é uma constante dentro do nó `Conferir verify token`. Ele
não precisa ser segredo forte: quem protege o endpoint é o path de 128 bits.

**5. Rodar o diagnóstico** `IG DM | 0 · DIAGNÓSTICO do acesso à API`
(`J5xCChVkyx8vkcPX`)

- **Primeira execução é só leitura.** Com `igsid_teste` vazio, ele confirma de
  quem é o token e lista as conversas com a janela de 24h ainda aberta.
- **Segunda execução testa o envio.** Copie um IGSID com a janela ABERTA para o
  campo `igsid_teste` do nó Configuração e rode. Isso **manda uma DM real**:
  escolha alguém que não seja lead.

O último nó devolve o `veredito`:

| veredito | o que fazer |
| --- | --- |
| `PASSOU: Standard Access basta` | seguir o checklist, sem App Review |
| `BARROU: falta permissão` | plano B: ManyChat como transporte, n8n como cérebro |
| `INCONCLUSIVO: janela fechada` | escolher outro IGSID, com janela aberta |
| `TOKEN INVÁLIDO` | gerar token de longa duração |

**6. Ativar o workflow 1** (FEITO), antes de assinar o webhook

A ordem importa: a Meta chama a URL de verificação assim que você salva a
inscrição, e o webhook do n8n só responde com o workflow ativo. Ativar depois
significa refazer o passo 7.

**7. Painel da Meta** → app → Instagram → Webhooks (FEITO)

- Callback URL: a URL acima
- Verify token: o mesmo `IG_VERIFY_TOKEN`
- Assinar o campo **messages**

A Meta chama a URL com GET uma vez. O workflow precisa estar **ativo** nessa hora,
senão a verificação falha.

**8. Teste ponta a ponta:** ponha uma linha na planilha com um username seu de
teste e `status = ABERTURA_ENVIADA`, mande `1` daquela conta e veja se a resposta
da dor mais a oferta chegam.

**9. Ativar o workflow 2** (FEITO). Ele roda às 20h e manda o resumo no seu Telegram
(chat `1317291661`).

## Como você opera

Você abre a conversa na mão, como já fazia. Depois põe a linha na planilha:

| coluna | o que pôr |
| --- | --- |
| `username` | o @ da pessoa, sem arroba |
| `status` | `ABERTURA_ENVIADA` |
| `abertura_enviada_em` | data e hora |

Só isso. O resto é do robô. Ele descobre o IGSID sozinho quando a pessoa responde
e grava na linha.

## A conversa, do início ao presente

**Abertura (manual, fora do n8n).** O Alison escreve para a pessoa oferecendo um presente
de boas-vindas e pede que ela escolha entre três situações. Depois anota a linha na
planilha como `ABERTURA_ENVIADA`.

**Ela responde 1, 2 ou 3.** O robô manda duas mensagens: a **implicação** da resposta dela
(estrutura SPIN, não repete o problema, mostra o que ele custa) e o convite para a cola,
com os botões `Quero sim` / `Agora não`.

A ordem espelha a abertura manual e **muda junto com ela**:

**Mudou em 23/08/2026, e a abertura manual tem que mudar junto.** A ponte das três dores
deixou de oferecer a cola e passa a oferecer a `/materia`: a cola media 16 aberturas e **zero**
cliques no CTA dela, porque entregava a resposta e deixava a pessoa servida. Entrou também uma
**quarta dor**, `4 - Peço e a resposta volta genérica`, que é a mais comum segundo a linha nova
e a única que o funil não perguntava. Isso empurrou o veredito de "interesse sem escolher" do
classificador de `4` para `5`. **A abertura que o Alison manda na mão precisa listar as quatro**,
senão a dor 4 só chega pela classificação da IA, nunca pelo dígito.

| resposta | dor gravada |
| --- | --- |
| 1 · Pago ferramentas que quase não uso | `ASSINATURAS` |
| 2 · Não sei qual IA escolher | `ESCOLHER_FERRAMENTA` |
| 3 · Faço quase tudo no ChatGPT | `SO_CHATGPT` |

**Ela toca em Quero sim.** Chegam três mensagens: o texto de entrega, um card com imagem
e o botão `ABRIR A COLA`, e o link em texto puro (o card só renderiza no app; o texto
salva quem abre no navegador).

**A cola faz o resto.** Ela mostra as 11 tarefas, demonstra valor e leva ao diagnóstico.
As 11 são exatamente as marcadas `no_reel` no `dados.json`: as do Reel que trouxe essa
gente, agora em formato consultável.

## A máquina de estados

```
ABERTURA_ENVIADA
   └─ responde 1, 2 ou 3 → resposta da dor + oferta → AGUARDANDO_INTERESSE
   └─ responde outra coisa                          → REVISAO_MANUAL

AGUARDANDO_INTERESSE
   └─ aceita  → link com código na UTM → LINK_ENVIADO
   └─ recusa  → resposta curta         → RECUSOU
   └─ pergunta algo                    → REVISAO_MANUAL

LINK_ENVIADO
   └─ pagou (conciliado às 20h) → COMPROU

qualquer outro estado → REVISAO_MANUAL (o robô não responde)
falha no envio        → ERRO_NO_ENVIO
opt-out               → NAO_CONTATAR
```

## O token não vence mais sozinho

`IG DM | 3 · Renovar token do Instagram` roda **toda segunda às 4h**: lê o token do
Redis, pede um novo à Meta (que estende para mais 60 dias), guarda o novo e faz
`PATCH` na credencial `Instagram Graph | noahai Direct`. Os workflows do Direct usam
essa credencial e nem percebem a troca.

O token vai para o Redis porque o refresh exige mandá-lo como query param, e a API do
n8n nunca devolve o valor de um segredo. Semear é um `POST` no webhook do próprio
workflow com `{"token":"IGAA..."}`, e essa semeadura já roda o ciclo inteiro.

**Se falhar, chega aviso no Telegram.** Token já vencido não pode ser renovado: aí é
gerar outro no painel e semear de novo.

## Testado ponta a ponta em 21/08

Com uma conta real (`@nandapinha`), a conversa inteira funcionou: resposta `3` →
duas mensagens com a implicação e os botões → toque em `Quero sim` (o payload chegou
como `SIM`, sem depender de interpretar texto) → três mensagens com o card → planilha em
`LINK_ENVIADO` com o código `rnjn14` → esse mesmo código chegando ao checkout da Cakto.

**O que ainda não rodou sozinho:** o resumo das 20h nunca disparou pelo agendamento, a
renovação do token só correu no teste manual, e a conciliação nunca viu uma compra real.
Todas dependem de tempo passar ou de dinheiro entrar, não de código.

## A API não enxerga conversa antiga

`GET /me/conversations` devolveu **0 conversas** mesmo com DMs reais na caixa, e
continuou em 0 depois da inscrição. A API só passa a ver uma conversa a partir do
momento em que o app foi conectado à conta.

**Isso não quebra o fluxo**, porque ele nunca depende do histórico: a pessoa responde
a sua abertura, essa resposta é uma mensagem nova, e o webhook a entrega normalmente.
O que fica vazio é só a listagem de conversas do diagnóstico.

**Mas muda o que esperar:** as 57 pessoas da campanha antiga e quem respondeu a
caixinha antes de hoje são invisíveis para o robô. A contagem começa do zero.

## A API não deixa consultar o perfil de quem ainda não escreveu

`GET /v25.0/<igsid>?fields=name,username` responde **500** com
`code 230 / IGApiException: "User consent is required to access user profile"` quando o
único contato até ali foi **você** escrevendo para a pessoa. O consentimento que a Meta
cobra nasce da mensagem **dela**: enquanto ela não responde, o perfil fica fechado, mesmo
com o IGSID em mãos, o app publicado e a conta inscrita em `messages`.

A consequência prática é no cadastro pelo eco. Quando a abertura sai, o webhook entrega o
`is_echo` com o IGSID do destinatário e nada mais. **O @ não existe naquele momento.** Por
isso o cadastro grava `username = ig_<igsid>` e a `obs` "aguardando o @". A linha cumpre o
papel dela, porque a busca do robô é pelo **igsid**, não pelo @. O que fica pendente é a
legibilidade para você.

> **Incidente de 21/08, das 20:40 às 21:13 UTC.** O nó `Montar cadastro` tratava a falha do
> perfil como erro fatal (`não descobri o @ de quem recebeu a abertura`), então **toda
> abertura enviada nessa janela deixou de virar linha**: 20 execuções em `error`. Duas
> pessoas responderam bem nesse intervalo (`maxabreu82` com `1` às 20:48 e
> `alline_marques.adv` com `2` às 21:11). Sem linha na planilha, o robô fez o que o desenho
> manda: gravou `REVISAO_MANUAL` com a `obs` "mandou DM sem abertura registrada" e **não
> respondeu nada**. As duas foram atendidas na mão. Corrigido às 21:13, quando o cadastro
> deixou de depender do perfil.

### Como o @ provisório vira o @ de verdade

Quem entra pelo eco nasce com `username = ig_<igsid>`, e o `Lead conhecido?` **reprova
esse formato de propósito** (`notStartsWith "ig_"`): é o que empurra a conversa para o
`Consultar perfil IG`, que agora funciona, porque a pessoa acabou de escrever. O perfil
devolve o @ real, o `Vincular IGSID à linha` grava, e a conversa segue na mesma execução.

Por isso **`ig_` é a única grafia aceita** para o @ provisório, em qualquer nó que crie
linha. O `Registrar desconhecido` usava `igsid_` (corrigido em 21/08), e uma linha nascida
assim passaria pelo `Lead conhecido?` como se já tivesse um @ de verdade: ela nunca seria
consultada de novo e ficaria com o número no lugar do @ para sempre.

A linha pode ser achada por dois caminhos, e é isso que o desenho precisa aguentar:

| caminho | como a linha nasceu | o que falta nela |
| --- | --- | --- |
| pelo **igsid** | o eco cadastrou (`ig_<igsid>`) | o @ e o nome |
| pelo **username** | você anotou na mão | o igsid |

Por isso o vínculo casa por **`row_number`**, não por igsid nem por username: é a única
chave que existe nos dois casos (a linha do eco ainda não tem o @, a linha anotada na mão
ainda não tem o igsid, e o Sheets não sabe procurar por uma coluna e gravar outro valor
nela ao mesmo tempo). O `row_number` vem de graça na leitura e foi testado antes de subir.

> **Bug corrigido em 21/08, 21:42 UTC.** O nó `Buscar por username` estava com
> `lookupColumn: "igsid"`, cópia não editada do nó anterior. Duas consequências opostas:
> a linha do eco era achada **por acidente** (ela tem igsid, então o lookup errado
> casava), e a linha anotada na mão **nunca** era achada, porque ela não tem igsid. Ou
> seja, o modo de operação que este doc manda usar estava quebrado desde sempre, e o que
> funcionava, funcionava pelo motivo errado. Agora o lookup é por `username` de verdade, o
> IF (renomeado para `Achou a linha dela?`) aceita a linha vinda de qualquer um dos dois
> caminhos, e o `Recuperar linha completa` escolhe a fonte pelo `row_number`.

Se a Graph API falhar bem nessa hora, o `ig_<igsid>` é **preservado** em vez de virar
vazio, e a conversa segue normalmente. O @ entra na próxima mensagem dela.

**A regra operacional que sobra:** não anote na mão ninguém que já recebeu a abertura pelo
robô. Essa pessoa já tem linha, com o igsid dela, e a busca do robô começa pelo igsid. Uma
segunda linha com o @ ficaria órfã, sem nunca receber um status, e a conta do dia sairia
errada. Anotar na mão continua valendo só para quem você abriu **fora** do fluxo.

## A planilha, coluna por coluna

`1lqwrmR0GHcoyjXbip3_kM-CRgWp2BWT0dJvBZXeEy1k`, aba **`leads`**.

Ela não é um relatório: é a **memória do robô**. Cada linha é uma conversa, e o campo
`status` é o que decide como o robô responde na próxima mensagem daquela pessoa. Mexer
nela muda o comportamento do sistema na hora.

### As três que você preenche

| coluna | o que pôr | por que existe |
| --- | --- | --- |
| `username` | o @ da pessoa, **sem arroba** | É a chave que liga o que você fez na mão ao que o robô vê. Você conhece a pessoa pelo @; a API só entrega um número. |
| `status` | `ABERTURA_ENVIADA` | É a autorização. Sem uma linha com este status, o robô **não responde** aquela pessoa, mesmo que ela escreva. |
| `abertura_enviada_em` | data e hora de agora | Só para você saber há quanto tempo abriu. O robô não usa. |

### As que o robô preenche sozinho

| coluna | quem escreve | por que existe |
| --- | --- | --- |
| `igsid` | robô, na 1ª resposta dela | O número que a Meta usa para identificar a pessoa. Com ele preenchido, as próximas mensagens acham a linha direto, sem consultar o perfil. **Está formatada como texto de propósito**: como número, o Sheets a destrói. |
| `nome` | robô, do perfil | Só o primeiro nome é usado, e apenas onde a mensagem pede. |
| `dor` | robô, ao ler 1/2/3 | `ASSINATURAS`, `ESCOLHER_FERRAMENTA` ou `SO_CHATGPT`. É o dado que diz qual argumento funciona com quem. |
| `codigo` | robô, ao entregar o presente | Seis caracteres que viajam na URL. **É o único elo entre a venda e a pessoa.** Sem ele, uma compra chega órfã. |
| `ultima_resposta` | robô | O que ela escreveu por último. É o que você lê para decidir o que fazer nos casos de revisão. |
| `ultimo_message_id` | robô | Rastro para conferência. A proteção real contra mensagem repetida está no Redis, não aqui. |
| `oferta_enviada_em` | robô | Quando o convite da cola saiu. |
| `link_enviado_em` | robô | Quando o presente foi entregue. |
| `janela_expira_em` | robô | **A coluna com prazo.** Depois dela, a API recusa qualquer resposta. É o que alimenta o alerta das 20h. |
| `comprou_em` | conciliação das 20h | Preenchida quando a compra é encontrada pelo `codigo`. |
| `obs` | robô | O motivo, quando algo saiu do script. É a primeira coisa a ler quando alguém está em revisão. |

### A coluna que é sua, mas não é rotina

`nao_contatar`: escrever `sim` aqui faz o robô parar de responder aquela pessoa para
sempre, em qualquer estado. Ele já preenche sozinho quando alguém escreve "sair", mas
você pode marcar na mão se alguém pedir por outro canal.

### As regras que evitam problema

**Anote antes de ela responder.** Se a pessoa escrever antes de a linha existir, o robô
cria uma linha em `REVISAO_MANUAL` e não responde nada. É o comportamento certo, mas
significa que você perdeu o timing daquela conversa.

**Não reformate as colunas.** `igsid`, `codigo`, `ultima_resposta` e `ultimo_message_id`
estão como texto porque o Sheets transforma número longo em notação científica e perde
dígitos. Reformatar como número quebra a busca rápida sem dar erro nenhum.

**Não apague quem pediu para sair.** Apagar a linha faz a pessoa voltar a ser
"desconhecida", e um contato futuro seu recomeçaria o ciclo. O `nao_contatar` existe
justamente para lembrar do "não".

**Para reprocessar alguém**, volte o `status` para a etapa anterior e limpe o que veio
depois. Voltar para `ABERTURA_ENVIADA` faz a próxima mensagem dela ser lida como escolha
de dor de novo.

### O que fazer com cada status

| status | significa | o que você faz |
| --- | --- | --- |
| `ABERTURA_ENVIADA` | esperando a escolha dela | nada, é o robô que age |
| `AGUARDANDO_INTERESSE` | leu a dor, esperando o sim | nada |
| `LINK_ENVIADO` | recebeu o presente | nada, a cola trabalha agora |
| `COMPROU` | pagou, e a venda foi ligada a ela | agradecer, se quiser |
| `RECUSOU` | disse que não | **nada.** Insistir aqui queima o canal |
| `REVISAO_MANUAL` | o robô não entendeu | ler `obs` e `ultima_resposta`, e responder você mesmo |
| `ERRO_NO_ENVIO` | a resposta não saiu | quase sempre a janela de 24h fechou; ver `obs` |
| `NAO_CONTATAR` | opt-out | nunca mais escrever |

Os dois que exigem você são `REVISAO_MANUAL` e `ERRO_NO_ENVIO`, e são exatamente os que
o resumo das 20h lista com nome e motivo.


## Decisões que valem registrar

**O n8n nunca inicia conversa.** A API do Instagram não permite, e não existe
gatilho de novo seguidor (a Meta criou o evento `follow` em out/2025 com o
ManyChat como parceiro exclusivo, em beta privado). A abertura é sempre sua.

**A janela é de 24h**, contada a partir da última mensagem *dela*. Passou disso,
o envio falha com erro #10 e a linha vira `ERRO_NO_ENVIO`. O resumo das 20h
mostra quem tem a janela fechando em menos de 6h, para você agir a tempo.

**Dedup no Redis, não na planilha.** Reusa o `FUNDAÇÃO | 2/8`: a marca nasce
provisória por 5 min e só vira definitiva no commit. Se o envio falhar, o
rollback apaga, e a reentrega da Meta volta a ser aceita. Planilha não serviria:
duas mensagens quase simultâneas leriam a mesma linha.

**Path secreto em vez de HMAC.** Validar o `X-Hub-Signature-256` exige o corpo
cru byte a byte; a alternativa comum (`JSON.stringify`) dá falso negativo com
emoji, e emoji no Direct é garantido. O path aleatório dá proteção equivalente.

**A venda não usa webhook.** O `/api/cakto` já grava toda venda aprovada na aba
`vendas` com o `utm_content` extraído do checkout. O workflow 2 só lê e cruza
pelo código curto. Zero mudança em código de produção que já funciona.

**Quem pede para sair, sai.** A primeira saída do Switch procura "sair", "parar",
"descadastrar" e afins **antes** de olhar a etapa, então o opt-out funciona no meio da
oferta. Confirma uma vez, marca `nao_contatar` e nunca mais responde. Isso está
**prometido na política de privacidade**, então não pode ser removido do workflow.

**A atribuição atravessa três saltos e foi medida.** `Direct → /cola → LP → Cakto`, com o
`utm_content` individual chegando inteiro a `pay.cakto.com.br` (verificado em 21/08 com o
código `rnjn14`). É esse código que a conciliação das 20h usa para marcar `COMPROU`. Se
alguém adicionar um CTA na `/cola` sem repassar a query, a venda passa a chegar órfã e a
conta quebra em silêncio.

**Sem follow-up automático**, de propósito. Quem não respondeu não recebe
cobrança do robô.

**O robô não improvisa.** Fora de 1/2/3 e de um sim/não claro, vira
`REVISAO_MANUAL`. O classificador (Haiku 4.5) cai em DUVIDA quando a chamada
falha, então erro de API nunca vira link enviado por engano.

## Testes

90 casos rodados contra os Code nodes antes de subir, cobrindo is_echo, reação,
recibo de leitura, resposta de story, áudio sem texto, "1 e 3", "10", classificador
fora do ar, reembolso, plural, escape de HTML no Telegram e os cinco vereditos do diagnóstico
(incluindo não confundir token expirado com falta de permissão) e as 20 variações do
opt-out, com os falsos positivos que o `\b` da regex precisa segurar ("sairia caro",
"separar as tarefas"). Todos passaram.

**Dois bugs de encanamento**, ambos silenciosos. O primeiro: o nó de update do Sheets devolve
só os campos que gravou, então o Switch depois dele recebia um item sem `status`
e mandaria **todo primeiro contato** para revisão manual. Resolvido com o nó
`Recuperar linha completa`.

O segundo apareceu depois, ao inserir o nó de "marcar como lida" no meio da cadeia: o
`Separar mensagens` lia `$input`, que passou a ser a resposta da API do Instagram em vez
das mensagens. Resultado: **o robô parou de responder e a execução seguiu marcada como
`success`**. Quem precisa de dado de negócio busca na origem nomeada
(`$('Tem o que enviar?')`), nunca em `$input`. E todo `jsCode` é compilado antes de subir:
um Code node com erro de sintaxe fica ativo e só falha quando alguém usa.

## 23/08/2026: o robô estava respondendo todo mundo

Sintoma: uma amiga respondeu um story meu ("Ele tem mais de 2m") e o robô emendou
o pitch da cola em cima da conversa pessoal. Ela respondeu "a IA tá maluca kkk".
A execução `39882` mostra que foram **duas falhas somadas**, e não uma:

1. **O parser de dígito atropelava o classificador.** A trava de "não pode sobrar
   texto fora dos dígitos" só existia no ramo de dois ou mais dígitos. Com um
   algarismo só, `digitos.length === 1 && soNumeros === digitos[0]` compara os
   dígitos com eles mesmos e sempre casa: `"ele tem mais de 2m"` virava dor 2.
   O Haiku tinha classificado **0** (não corresponde a nenhuma). A `obs` saiu
   vazia, provando que a fonte foi o dígito e não a IA.
2. **A porta estava escancarada.** Não existia filtro de origem: qualquer DM de
   qualquer pessoa era cadastrada como lead e classificada na mesma execução.
   Herança da correção de 22/08 que tirou o robô do mudo.

Não foi só ela. `blankpartners` mandou **um anexo sem texto** e recebeu a pergunta
das 3 opções; `campos_toledo` escreveu **"Sim, pode mandar o link por favor"** e
recebeu silêncio. O espelho exato da reclamação: pitch em quem não pediu, silêncio
em quem pediu.

### O gate que faltava veio do SDR da Dra. Luciana

O `furqHJdPjL4lPMKR` resolve isso com `Check_Origem_Msg` → `Desativa Bot`: quando
um humano responde pelo número, o bot desliga para aquele contato. O equivalente
no Instagram é o **eco**, e ele agora tem ramo próprio (`tipo: 'eco'`).

O que separa "o robô respondeu" de "eu digitei na mão" é o **mid**: o
`message_id` que a Graph API devolve no envio é **idêntico** ao `mid` que volta
no eco (verificado em 23/08 comparando a execução `39882` com o eco `39884`).
Então o `Marcar mid do robô` (Redis, TTL 24h) guarda tudo que o robô manda, e o
`Foi o robô?` consulta na volta. Mid desconhecido significa que fui eu, e a
conversa vira humana: grava `nao_contatar = sim` e o robô cala ali.

⚠️ O `Marcar mid do robô` está pendurado como **ramo paralelo** da saída de
sucesso do `Enviar DM`, não no meio do loop. Inserir nó no meio da cadeia é
exatamente o bug de encanamento que já custou caro duas vezes aqui.

⚠️ **Cinto reserva contra auto-silenciamento.** Se o Redis falhar, o eco do
próprio robô cairia como "humano" e ele se calaria sozinho no meio do funil,
sem ninguém perceber. Por isso o `Montar silenciamento` também olha a planilha:
envio do robô para aquela pessoa há menos de 5 minutos significa que o eco é
dele, e aí não grava nada (`return []`).

### A porta de entrada agora exige sinal de interesse

O `Classificar dor` ganhou um quarto veredito: **4 = não escolheu nenhuma das
três, mas quer falar do assunto** (pede a cola, o link, a lista, pergunta sobre
IA). DM espontânea de quem não tem linha só recebe o acolhimento com veredito 4.
Qualquer outra coisa fica em `REVISAO_MANUAL` **sem receber nada**.

Se a IA estiver fora do ar o veredito vem vazio e ninguém é abordado: calar é o
lado seguro do erro, ao contrário do que valia antes.

### Roteamento: dois furos fechados de passagem

- A regra `abertura` do Switch aceitava `ABERTURA_ENVIADA` **sem checar
  `nao_contatar`** (só o `REVISAO_MANUAL` checava). O silenciamento vazaria por
  ali. Agora o opt-out vence em qualquer status.
- Quem pede o material com todas as letras (`link`, `cola`, `material`, `lista`)
  vai para o ramo do interesse mesmo sem ter escolhido 1, 2 ou 3. É o caso
  `campos_toledo`, que pediu o link e ficou no vácuo.

### Testes (todos em produção, com IGSID inventado)

| # | Entrada | Esperado | Execução |
|---|---------|----------|----------|
| T1 | eco meu, mid desconhecido | silencia a conversa | `39928` ✅ |
| T2 | "Ele tem mais de 2m" de alguém novo | não envia nada | `39929` ✅ |
| T3 | "me manda a lista das IAs" | acolhe (veredito 4) | `39932` ✅ |
| T4 | eco logo após envio do robô | **não** silencia | `39935` ✅ |
| T5 | "2" | resposta da dor 2, como sempre | `39937` ✅ |

Cada teste deixa uma linha na planilha para apagar: `ig_999900777`,
`ig_999900778`, `ig_999900779` e `ig_999900780`.

Backups do workflow em `scratchpad/backup-igdm/` (antes e depois).
