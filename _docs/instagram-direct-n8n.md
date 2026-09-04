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

---

## 28/08/2026: botão no Direct e o convite que abre a janela de 24h

### O problema que isso resolve

A Meta permite **UMA** resposta privada por comentário, com teto de 1.000
caracteres. Era essa trava que obrigava a entrega a caber espremida numa
mensagem só, e que já custou uma entrega inteira: o guia dos 5 MCPs saiu com
1.266 caracteres em 24/08 e falhou em silêncio para todo mundo.

O toque num botão `postback` **conta como resposta da pessoa**, então abre a
janela de 24h. Depois disso cabem quantas mensagens forem precisas. Por isso a
resposta privada virou um **convite com botão**, e a entrega de verdade sai
depois do toque.

### O que mudou

**1. `messaging_postbacks` foi inscrito.** Antes o app assinava só
`messages,comments`, e sem esse campo o toque no botão não chega ao n8n:

    POST /me/subscribed_apps?subscribed_fields=messages,comments,messaging_postbacks

⚠️ O POST **substitui** a lista inteira. Sempre repetir os campos anteriores,
senão as DMs ou os comentários param.

**2. `Normalizar evento` trata postback.** Antes tinha um
`if (m.postback) return ignorar(...)`. O toque chega em `messaging[].postback`,
nunca em `messaging[].message`, e sai de lá como `tipo: 'mensagem'` com o
payload em `botao`, de propósito: assim reaproveita o dedup, a busca do lead e
o `Etapa da conversa` inteiros, sem pipeline paralelo.

**3. Ramo do comentário virou convite.** Fluxo novo:

    Montar entrega da cola -> Guardar entrega no Redis -> Responder no privado
      -> Convite passou? -> (sim) Cola entregue
                         -> (não) Entrega em texto (reserva) -> Cola entregue

`Responder no privado` agora manda `template_type: 'button'` com um botão
`postback` de payload `COLA::<campanha>`.

**4. Ramo novo do toque.** `Etapa da conversa` ganhou a saída **`cola`**
(4ª regra, o fallback `revisão` passou a ser a 5ª saída):

    Etapa da conversa [cola] -> Ler entrega da cola -> Montar cola pós-clique
      -> Tem o que enviar? -> (pipeline de envio de sempre)

### Decisões que não são óbvias

**A entrega mora no Redis, não é remontada.** Chave `igdm:cola:<igsid>`, TTL de
7 dias (o mesmo prazo em que a Meta ainda aceita responder o comentário). O
motivo é concreto: a tabela de campanhas vive no `Qual campanha?`, indexada por
`media_id`, e **o evento de postback não traz media_id nenhum**. Sem o Redis, a
tabela teria que ser duplicada.

**A reserva em texto não é enfeite.** A doc da Meta não confirma template em
resposta privada a comentário (só exemplifica texto). Se ela recusar, a entrega
NÃO pode parar: o `Convite passou?` cai no texto puro de sempre e a pessoa
recebe igual, só sem botão.

**O rótulo do botão não pode conter `link`, `cola`, `material` nem `lista`.**
São as palavras que ligam a regra `interesse` do `Etapa da conversa`: o toque
entraria no funil errado. O padrão é `👉 TOQUE AQUI`.

**Status novo: `CONVITE_ENVIADO`.** Diz a verdade sobre o que a pessoa recebeu,
porque no convite o link ainda NÃO foi. `link_enviado_em` fica vazio até o
toque. Quem trava o segundo resgate continua sendo `obs` (por campanha), nunca
essa data. A distância entre `CONVITE_ENVIADO` e `LINK_ENVIADO` no resumo das
20h **é a taxa de toque no botão**.

⚠️ Dois nós liam `status === 'LINK_ENVIADO'` e foram corrigidos junto, senão
quebravam calados: `Cola foi entregue?` (a resposta pública no comentário
pararia de sair) e o `ORDEM` do resumo diário no workflow 2/2.

**A trava do toque repetido é a própria regra do Switch**
(`status !== 'LINK_ENVIADO'`). Tocar duas vezes não entrega duas vezes.

### Formatos com botão que a API aceita

| Formato | Visual | Limites |
|---|---|---|
| `template_type: 'button'` | texto + botões na bolha | 640 caracteres, 1 a 3 botões |
| `template_type: 'generic'` | card com imagem, vira carrossel | 10 cards, 3 botões cada |
| `quick_replies` | chips abaixo do campo | 13 chips, título de 20 caracteres |

Só existem dois tipos de botão: `web_url` (abre o link, não gera evento) e
`postback` (ecoa o rótulo como mensagem dela e devolve o payload ao webhook).
**Nada disso renderiza no Instagram web**, só no app do celular.

### Como foi testado (28/08, sem incomodar ninguém)

Dois POSTs no webhook de produção com IDs inventados, IGSID `7777777777777771`:

1. **Comentário** no media `18128044237766718` (Reel /watch): montou o convite
   com o botão, guardou as 3 mensagens no Redis, mandou o button template e
   falhou só no destinatário (`code 100 / subcode 2534014`). O
   `Convite passou?` roteou para a reserva, que falhou pelo mesmo motivo, e o
   `Cola entregue` gravou `ERRO_NO_ENVIO` com o detalhe. Fallback provado.
2. **Postback** com payload `COLA::reel_watch`: o `Normalizar evento` devolveu
   `botao: COLA::reel_watch`, o Switch roteou para a saída `cola`, o Redis
   devolveu a entrega, o `Separar mensagens` gerou as 3 mensagens com tempo de
   digitação e o `Enviar DM` falhou só no destinatário. Cadeia inteira provada.

A linha de teste foi apagada da planilha (linha 755, via `deleteDimension` da
API do Sheets, que é 0-based e não tem a ambiguidade do node) e a chave do
Redis foi removida.

⚠️ **O que os testes NÃO provam:** se a Meta aceita template em resposta privada
a comentário. Os dois envios falharam no destinatário inventado ANTES de
qualquer validação de corpo. Só um comentário real conclui isso, e é o próximo
passo antes de confiar no caminho principal.

### O truque do IGSID inventado mudou

A nota antiga dizia que um destinatário falso devolvendo `subcode 2534014`
provava permissão. **Isso não vale para validar payload**: com `recipient.id`
de 16 dígitos a Meta hoje devolve `code 2 / "Service temporarily unavailable"`
para qualquer corpo, inclusive para um `template_type: 'xx_nao_existe'` mandado
de propósito como controle. Ela valida o destinatário antes do corpo. Com
`recipient.comment_id` o erro volta como `2534014`, mas pelo mesmo motivo.

### A copy do fluxo (aprovada em 28/08/2026)

A conversa do Reel `/watch`, que é o desenho de todas as sete campanhas:

```
você:  Quer o guia da WATCH?            [ 👉 TOQUE AQUI ]
ela:   👉 TOQUE AQUI                    (abre a janela de 24h)
você:  Boa, {nome}!
você:  {descricao da campanha}
você:  {aviso da campanha}
você:  Tudo que vc precisa está aqui 👇 [ ABRIR OS 3 PROMPTS ]
você:  {fecho da campanha}
```

**A palavra-chave vai em caixa alta no convite**, porque é a mesma que a pessoa
acabou de comentar: ela se reconhece na hora. Sacada copiada do @brun0gpt.

**Três campos novos por campanha** no nó `Qual campanha?`, todos obrigatórios:

| campo | o que é | limite |
|---|---|---|
| `convite` | texto da resposta privada, o único tiro | 640 caracteres |
| `aviso` | por que o resto está numa página | 1.000 caracteres |
| `botao_link` | rótulo do botão que abre o link | **20 caracteres** |

⚠️ **O `aviso` não é texto inventado: ele saiu do fim da `descricao`.** As
descrições terminavam em dois-pontos para emendar na URL crua. Com o botão no
lugar da URL, aquela linha viraria repetição, então ela virou bolha própria. Em
`reel_watch` e `carrossel_dinheiro_watch` o aviso ganhou a razão real na frente
(copiar prompt de dentro do Direct no celular é ruim, por isso a página tem
botão de copiar). Nas outras o texto continua o do Alison, só com o dois-pontos
virando ponto final: ali o link é a matéria ou o diagnóstico, e dizer "montei um
documento" seria prometer uma coisa e entregar outra.

`reel_grafico_ia` é o único com `aviso` totalmente novo, porque as quatro
variantes de cor têm descrição própria e nenhuma fazia ponte para o link.

**A `intro` saiu da entrega** e vive só no `_texto` (a reserva sem botão): quem
cumprimenta agora é a saudação com o nome.

**O nome vem do nó `Nome dela`**, um `GET /{igsid}?fields=name,username` entre o
Redis e o `Montar cola pós-clique`. Cascata: primeiro nome do perfil → @ dela
(sem o prefixo `ig_`) → "Boa!" sem nome. Nome todo em caixa alta é normalizado,
senão sai "Boa, ALISON!" gritando. O `code 230` da Graph API não derruba nada
porque o nó tem `onError` e o fallback do @ sempre existe.

**São cinco mensagens depois do toque**, medidas em 10,3 segundos de digitação
somada. O link chega na quarta, então quem só quer o link não espera o fim.

Validado em 28/08 com os mesmos dois POSTs de sempre (IGSID `7777777777777772`):
o convite montou o button template certo, o toque devolveu as cinco mensagens na
ordem, o `botao_link` chegou no `Separar mensagens` e o `Enviar DM` montou o
button template de `web_url`. Os dois falharam só no destinatário inventado. A
linha 758 e a chave do Redis foram apagadas.

### 28/08, mais tarde: o corte de texto e o campo `descricao` opcional

A primeira versão saiu com cinco bolhas e o Alison cortou duas, por dois motivos
diferentes e os dois corretos:

**1. O `aviso` deixou de ser bolha e virou o texto da bolha do botão** (campo
renomeado para `chamada`). Como bolha própria ele gastava cinco linhas dizendo
"o material está numa página", que é exatamente o que o botão logo abaixo já
dizia. Duas bolhas seguidas apontando para o mesmo lugar.

**2. `descricao` virou OPCIONAL, e saiu de `reel_watch` e
`carrossel_dinheiro_watch`.** O conteúdo dela (os comandos de instalação do
plugin) já está dentro do próprio documento que o botão abre. Verificado antes de
cortar, lendo os dois artifacts: `Roubar o Hook` tem a seção "Instalar" e
`Pedidos do /watch` tem a "Antes de tudo", ambas com as mesmas duas linhas.

⚠️ **A regra que decide se a campanha tem `descricao`:** o link já contém o que a
DM ia mandar? Se sim, a DM cala. Se não, o texto é a entrega e fica. Por isso as
outras cinco campanhas continuam com quatro bolhas: a /materia não entrega as 11
tarefas nem a lista de IA por tarefa, e o diagnóstico não entrega os 5 comandos
de MCP. Cortar lá seria prometer no post e não entregar.

Isso **revoga em parte** a decisão antiga de manter os comandos na DM para que
"quem não clicar ainda saia com algo na mão": vale a pena repetir conteúdo para
segurar quem desiste apenas quando o conteúdo não está do outro lado do clique.

As constantes `GUIA_WATCH` e `GUIA_ASSISTIR` foram removidas do nó, porque só
essas duas campanhas as usavam. Estão nos backups em `scratchpad/backup-igdm/`.

Quatro fechos foram encurtados (`reel_watch`, `carrossel_dinheiro_watch`,
`reel_tarefa`, `reel_ferramenta`).

**Resultado medido, com os dois formatos testados no mesmo deploy:**

| campanha | bolhas depois do toque | reserva em texto |
|---|---|---|
| `reel_watch` | 3 | 359 caracteres (eram 601) |
| `carrossel_talheres` | 4 | 726 caracteres |

A edição do nó `Qual campanha?` foi feita fora do n8n, em Python com `assert` em
cada substituição, e devolvida por `PUT /api/v1/workflows`. Motivo: `reel_tarefa`
e `reel_ferramenta` têm `aviso` e `fecho` idênticos, e um find/replace cego
trocaria só a primeira ocorrência ou as duas sem avisar qual.

### O rótulo dos botões é fixo (28/08, decisão do Alison)

Os rótulos descritivos (`ABRIR OS 3 PROMPTS`, `LER A MATÉRIA`, `VER O GRÁFICO`)
foram substituídos pelo padrão do @brun0gpt, igual em todas as campanhas:

- botão do convite, `postback`: **👉 TOQUE AQUI 👈**
- botão do link, `web_url`: **CLIQUE AQUI 👈**

Como não varia por campanha, o rótulo saiu da tabela do `Qual campanha?` (eram
sete campos `botao_link` repetidos) e virou constante no `Montar entrega da cola`.
Para fugir do padrão numa campanha específica, basta declarar `botao_link` nela:
o código lê `v.botao_link || 'CLIQUE AQUI 👈'`.

⚠️ **`👉 TOQUE AQUI 👈` ocupa 20 dos 20 bytes permitidos**, porque cada emoji
come 4 bytes em UTF-8 (são só 14 caracteres visíveis). É o limite exato: não cabe
mais nada nesse rótulo. O `CLIQUE AQUI 👈` usa 16 e tem folga.

Quem carrega a informação agora é a `chamada`, o texto na mesma bolha do botão.
Isso torna a `chamada` obrigatória e específica: com o rótulo genérico, um texto
vago ali deixaria a pessoa sem saber o que abre.

---

## Auditoria completa de 28/08/2026

Rodada sobre os 66 nós do workflow 1/2, mais os workflows irmãos. Método: análise
estática do grafo, simulação das campanhas fora do n8n, e 12 disparos reais no
webhook de produção com IDs inventados.

### O que passou

- **Grafo íntegro:** zero nós órfãos, zero inalcançáveis a partir dos gatilhos,
  zero conexões apontando para nó inexistente, zero nós desabilitados. Os dois
  webhooks têm fluxos completamente isolados um do outro.
- **49 das 52 referências `$('nó')` são garantidas** por dominância de grafo (o nó
  citado sempre executou antes). As outras 3 estão todas protegidas por try/catch
  ou `isExecuted`: são exatamente as três que a nota do
  `Decidir resposta da dor` já documentava.
- **As 11 combinações de campanha** (7 campanhas + as 4 variantes de cor do
  gráfico) montam dentro de todos os limites da Meta. Simuladas em Node fora do
  n8n, medindo bytes de verdade.
- **100 das 100 últimas execuções** do workflow 1/2 terminaram com sucesso.
- **Estado da API:** token válido (`aalisonaraujo`, MEDIA_CREATOR, 126 posts),
  inscrições corretas (`messages, comments, messaging_postbacks`), e **os 7
  media_id da tabela de campanhas existem** e estão entre os 25 posts mais
  recentes. Nenhuma campanha aponta para post fantasma.
- **Caminhos exercitados com disparo real:** dor por texto livre (a IA classificou
  "pago um monte de assinatura que nem uso" como ASSINATURAS e respondeu certo),
  pedido de link, comentário em post fora da tabela (ignorado em 8 nós), toque sem
  convite, e a trava do toque repetido (com status `LINK_ENVIADO` o segundo toque
  cai em revisão e NÃO reentrega).

### 🔴 Achado 1: o resumo das 20h estava morto há 5 dias

**De 24 a 28/08 o workflow 2/2 falhou todos os dias**, sempre no nó
`Ler vendas da Cakto`, sempre com quota do Google Sheets estourada
(`Read requests per minute per user`). Consequência: nenhuma venda do Direct foi
conciliada e nenhum resumo chegou no Telegram nesses cinco dias.

**A causa não é a planilha nem o workflow 2.** Medido: a planilha tem 18 KB e é
lida em 2 segundos quando a quota está livre. O que satura é a credencial
`Google Sheets account` ser compartilhada por **6 workflows ativos**, com o
agendamento (00:00 UTC = 21h BRT) caindo no pico de DM. Na janela medida, o
`IG DM | 1/2` fez 102 execuções e o `SDR - Dra. Luciana` fez 39 em 2 horas, com
picos de 21 execuções no mesmo minuto.

**Corrigido:** retry dos dois nós de leitura passou de 3 tentativas com 5s (15
segundos de janela, que nunca alcançava o reset de 60s) para **5 tentativas com
30s**, ou seja, 2 minutos. O `Marcar COMPROU`, que não tinha retry nenhum e é
quem grava a venda, ganhou 3 tentativas com 15s.

⚠️ **Não trocar o `onError` desses nós para `continueRegularOutput`:** capturar o
erro DESLIGA o retry do n8n, e a espera nunca acontece. Medido nesta auditoria.

Se voltar a falhar, o próximo passo é mudar o horário do agendamento para fora
do pico.

### 🔴 Achado 2: o opt-out não valia para quem não estava na planilha

Quem mandava "sair" **sem ter linha** não era marcado: a regra 0 do
`Etapa da conversa` só alcança quem já está cadastrado, então a pessoa caía em
`Registrar desconhecido` como DM comum, virava `REVISAO_MANUAL` e continuava
contatável. A política de privacidade promete a saída por essa palavra sem
exceção.

**Corrigido em dois lugares**, e o segundo só apareceu no reteste:

1. `Registrar desconhecido` agora repete a checagem de opt-out (mesma lista de
   palavras do Switch) e grava `NAO_CONTATAR` com `nao_contatar: sim`.
2. `Decidir resposta da dor` ganhou uma saída antecipada para quem já está
   marcado. **Sem ela a correção não valia de nada:** esse nó roda depois no mesmo
   caminho e regravava a linha como `REVISAO_MANUAL`, apagando o `nao_contatar`.

Validado ponta a ponta: "sair" de um IGSID desconhecido agora grava
`NAO_CONTATAR` na planilha e não dispara resposta nenhuma.

### 🔴 Achado 3: falha do Redis deixaria a pessoa pendurada

O `Guardar entrega no Redis` tem `onError: continueRegularOutput`. Se o Redis
falhasse, o convite com botão era enviado assim mesmo, e como é do Redis que a
entrega volta no toque, a pessoa tocaria no botão e **não receberia nada**.

**Corrigido:** o `Convite passou?` agora exige as duas coisas, o envio e a
gravação no Redis. Se o Redis falhar, cai na reserva em texto puro, que entrega
tudo de uma vez e não depende de guardar nada.

### 🟡 Observações que não viraram correção

- **`carrossel_5_mcps` usa 970 dos 1.000 caracteres** da reserva em texto. São 30
  de margem: qualquer palavra a mais nessa campanha aciona o corte automático da
  descrição.
- **Quem chega pedindo "me manda o link" sem estar cadastrado recebe a pergunta
  das 3 dores**, não o link. É o desenho atual (a regra `interesse` exige status
  `ABERTURA_ENVIADA` ou `REVISAO_MANUAL`, e quem nasce agora não passa pelo
  Switch), mas vale saber que a palavra-chave não atalha nada na primeira DM.
- **8 nós de Google Sheets estão com `onError: stopWorkflow`.** Não mexi: é
  defensável querer que a execução morra quando a planilha falha, já que ela é a
  fonte da verdade. Mas é o que transforma um soluço do Sheets em execução
  perdida.
- **O `SDR - Dra. Luciana` e o fan-out da Evolution** são os maiores consumidores
  da mesma credencial Google depois do próprio IG DM. Se a quota voltar a
  incomodar, é lá que está a folga.

Todas as linhas de teste foram apagadas da planilha (confirmado com varredura por
prefixo), as chaves de teste do Redis foram removidas e nenhum workflow temporário
ficou para trás. Backups em `scratchpad/backup-igdm/pos-audit-*.json`.

### Correção do achado 1, segunda rodada: o retry não era o problema

A primeira correção (aumentar `maxTries` e `waitBetweenTries`) **não funcionou**, e
o motivo é uma limitação do n8n: **ele não respeita `waitBetweenTries` acima de
poucos segundos**. Configurado com 5 tentativas de 30s, a execução inteira durou
53 segundos em vez dos 2 minutos esperados.

**O que ficou no lugar** (testado em 4 execuções reais):

```
Ler leads → Ler vendas → As duas leituras vieram?
   sim → Cruzar e resumir → (fluxo de sempre)
   não → Ainda dá pra tentar?   ($runIndex < 4)
            sim → Esperar a quota (Wait de 70s) → volta pro Ler leads
            não → Avisar que não deu → Mandar resumo
```

Os dois nós de leitura passaram para `onError: continueRegularOutput` (para o IF
poder inspecionar o erro) e o `retryOnFail` foi desligado, já que a espera agora
é um nó de verdade. O `$runIndex` serve de contador de voltas sem guardar estado.

⚠️ **O `Mandar resumo` agora atende os dois caminhos:**
`{{ $('Cruzar e resumir').isExecuted ? ... : $json.resumo }}`. Sem isso, o
caminho de falha quebrava na expressão.

**A melhoria que mais vale:** o workflow deixou de falhar calado. Nas quatro
execuções de teste, o Telegram chegou dizendo que não deu, com o erro exato.
Foram cinco dias de silêncio justamente porque ninguém é avisado de um
agendamento que morre.

### ⚠️ A causa raiz NÃO é o workflow: é a planilha do diagnóstico

Depois de 10 tentativas ao longo de meia hora, o padrão é inequívoco:

| planilha | resultado |
|---|---|
| `1lqwrmR0...` (leads do Direct) | passou em **todas** as tentativas |
| `1gPkrK-X...` (Qual IA Usar? — Diagnósticos e Leads) | falhou em **todas** as 10 |

As duas são lidas com a mesma credencial, no mesmo segundo, e uma passa enquanto
a outra recusa. Isso descarta quota de usuário, tamanho de arquivo e forma de
referenciar a aba (trocar `mode: name` por GID **não** resolveu, embora tenha
ficado como melhoria: economiza uma chamada de metadados por leitura).

A leitura como o problema é: **a planilha do diagnóstico está sob carga vinda de
fora do n8n.** Ela tem 8 abas (`vendas`, `leads`, `diagnosticos`, `abandonos`,
`presentes`) alimentadas em tempo real pelo site e pelo `/api/cakto`, e a
campanha está no ar. O 429 é daquele arquivo, não da conta.

**O que isso implica:** enquanto a LP do diagnóstico estiver com tráfego, o
resumo das 20h vai continuar caindo. Os caminhos possíveis, em ordem de esforço:

1. mover o agendamento para uma faixa de baixo tráfego (a hora mais calma medida
   é 03h-05h BRT, com 3 a 8 batidas contra 64 às 21h)
2. o `/api/cakto` gravar as vendas também na planilha do Direct, tirando a
   dependência da planilha do diagnóstico
3. trocar a planilha por um banco de verdade nesse ponto do funil

⚠️ **Uma consequência que apareceu durante a auditoria:** com a quota apertada, o
próprio `IG DM | 1/2` falha. Em 28/08 às 21:52 a **@pamelabraz41 comentou WATCH,
recebeu o convite normalmente, e o `Gravar lead do comentário` morreu com 429**.
A linha dela não existia, então o toque no botão cairia em revisão sem entregar
nada. Foi recuperada na mão (`CONVITE_ENVIADO`, código `jzir7r`), e a entrega já
estava guardada no Redis.

### 🎉 O template FUNCIONA em resposta privada a comentário

A dúvida que ficou em aberto o dia todo foi respondida por acidente, com gente
real: na execução da @pamelabraz41, o nó `Responder no privado` **enviou com
sucesso** o `template_type: 'button'` com botão `postback`.

Ou seja: **o caminho principal está de pé**, a reserva em texto é só rede de
segurança, e o convite com botão chega de verdade no Direct de quem comenta.

---

## As três saídas, executadas em 28/08/2026

### 1. Horário: de 21h para 4h da manhã

O cron passou de `0 20` para `0 4`, e o fuso do workflow foi **fixado em
`America/Sao_Paulo`** nas settings. Antes o cron era interpretado no fuso do
servidor, e por isso "20h" rodava às 21h de Brasília, o pior horário possível.

Às 4h da manhã são de 3 a 8 batidas no Sheets por hora, contra 64 às 21h. É a
faixa mais calma medida em 1.500 execuções.

O `Cruzar e resumir` passou a datar o relatório com `Date.now() - 6h`: rodando de
madrugada, o dia que interessa é o que acabou, não o que começou há quatro horas.

### 2 e 3 são a mesma saída, e a 3 tornou a 2 desnecessária

A ideia da 2 era o `/api/cakto` gravar as vendas também na planilha do Direct,
para o resumo não depender da planilha do diagnóstico. Ao abrir o código para
implementar, apareceu que **isso já existe de outra forma**: o `/api/cakto` grava
cada pedido na tabela `qia_orders` de um Postgres (Neon), com
`checkout_url` completo, `diagnostic_code`, `status` e `paid_at`. Ver
`api/_access.mjs`.

Ou seja, a fonte sem quota já estava lá. Fazer a 2 seria criar um terceiro
espelho dos mesmos dados. **Ficou só a 3.**

**O que mudou no workflow:**

| antes | depois |
|---|---|
| `Ler vendas da Cakto` (Google Sheets, aba `vendas`) | `Ler vendas no banco` (Postgres) + `Vendas normalizadas` (Code) |

O nó `Vendas normalizadas` traduz a linha do banco para o mesmo formato que a aba
tinha (`status`, `utm_source`, `utm_content` soltos, extraídos do `checkout_url`),
para que o `Cruzar e resumir` continue idêntico. O `utm_content` cai no
`diagnostic_code` quando o checkout não trouxe UTM.

A credencial `Neon | Qual IA Usar (qia_orders)` foi criada no n8n a partir do
`DATABASE_URL` que já estava em `.vercel/.env.production.local`.

⚠️ **`executeOnce` LIGADO no nó Postgres.** Sem isso o n8n roda a query uma vez
por item de entrada, e como entram todos os leads da planilha, eram **781
consultas ao banco por execução**. Com a correção: 1 consulta, e o workflow
inteiro caiu de 4,5s para 1,9s.

### A conferência que autorizou a troca

Antes de trocar, as duas fontes foram lidas lado a lado:

| | banco `qia_orders` | planilha `vendas` |
|---|---|---|
| pedidos | 2 | 2 |
| pagos | 2 | 2 |
| **do Instagram** | **0** | **0** |

São exatamente os mesmos dados, e a troca não perde nada. O único pedido com UTM
é uma compra de homologação (`utm_campaign=homologacao`, de 20/08).

**O que isso revela sobre o funil:** a conciliação nunca marcou ninguém como
COMPROU porque **ainda não houve nenhuma venda vinda do Direct**. Não é bug do
workflow, é o estado do negócio. Bate com o que já estava medido: o quiz é aberto
por 1 em cada 692.

### Resultado

O resumo voltou a chegar no Telegram, em 1,9 segundo, sem uma única volta do
ciclo de espera:

```
Direct do Instagram · 28/08/2026

782 pessoas na planilha:
  32 em ABERTURA_ENVIADA
   3 em AGUARDANDO_INTERESSE
  12 em CONVITE_ENVIADO
 308 em LINK_ENVIADO
 344 em REVISAO_MANUAL
  13 em NAO_CONTATAR
  70 em (SEM STATUS)
```

**12 pessoas já estão em `CONVITE_ENVIADO`**, ou seja, receberam o card com botão
e ainda não tocaram. A distância entre esse número e o `LINK_ENVIADO` é a taxa de
toque, e é o que vale acompanhar nos próximos dias.

A planilha do diagnóstico continua sendo lida por ninguém neste workflow, e voltou
a responder normalmente assim que parou de ser martelada.
