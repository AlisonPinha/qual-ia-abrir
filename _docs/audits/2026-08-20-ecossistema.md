# O ecossistema das IAs principais, 20/08/2026

Segunda parte da varredura. A primeira olhou **preço** das 13 do catálogo
(`2026-08-20-catalogo.md`); esta olha **funcionalidade nomeada** das famílias principais, que é
o que alimenta o bloco "Dentro dela, o que quase ninguém usa" do `/mapa`.

**Por que isso importa mais que preço:** o bloco de recursos é o que faz o mapa valer para quem
**já conhece** a ferramenta, e metade das pessoas recebe pelo menos uma que já usa. Foi medido
no repo: zerando o tronco inteiro, o piso de mapas feitos só das quatro generalistas é 45,8%.
Logo o valor não pode ser "ferramenta que você nunca ouviu", tem que ser o que fazer dentro da
que ela já tem.

**O catálogo só tem esse bloco em 4 das 13.** Claude, ChatGPT, Gemini e Gemini Notebook. As
outras nove entregam nome, custo, primeiro passo e prompt, sem nada de "por dentro".

---

## Família Claude (oficial: claude.com/product/overview)

| Funcionalidade | O que faz | No produto? |
|---|---|---|
| **Projects** | contexto persistente por tópico | **sim** |
| **Cowork** | delega tarefa que roda e devolve documento pronto | **sim** |
| **Claude Code** | o Claude dentro do projeto, por linha de comando | está no catálogo como ferramenta separada |
| **Artifacts** | vira a descrição em ferramenta, visualização ou página compartilhável | não |
| **Skills** | capacidades especializadas que o Claude carrega para a tarefa | não |
| **Claude in Chrome** | o Claude agindo dentro do navegador | não |
| **Claude para Microsoft 365** | dentro do Word e do Excel | não |
| **Voice Mode** | alterna entre digitar e falar | não |

Modelos citados: Mythos, Fable, Opus, Sonnet e Haiku.

## Família ChatGPT (agregador: as páginas da OpenAI respondem 403)

| Funcionalidade | O que faz | No produto? |
|---|---|---|
| **Modo de voz** | conversa falada, forte no deslocamento | **sim** |
| **Deep Research** | agente que lê muitas fontes e devolve relatório com citação | **sim** |
| **Agent Mode** | executa tarefa de várias etapas, controla navegador e preenche formulário | **sim** |
| **Canvas** | escrita e código lado a lado, em vez de chat corrido | não |
| **Projects** | organiza trabalho longo, com até 40 arquivos no Plus | não |
| **Tasks** | lembrete e prompt que se repete sozinho | não |
| **Codex** | agente de código | não |
| **Sora** | geração de vídeo | não |

## Família Gemini (oficial: gemini.google/br/overview)

| Funcionalidade | O que faz | No produto? |
|---|---|---|
| **Deep Research** | varre centenas de páginas e monta o relatório | **sim** |
| **Canvas** | vira o relatório em página, quiz ou infográfico | **sim** |
| **Gems** | assistente configurado para a tarefa que se repete | **sim** |
| **Nano Banana** | cria e edita imagem com texto legível dentro | **sim, entrou em 20/08** |
| **Gemini Live** | conversa em tempo real | não |
| **Gemini Spark** | agente para tarefa específica | não |
| **Personal Intelligence** | personalização com o contexto da pessoa | não |
| **Storybook** | narrativa visual | não |
| **Geração de vídeo e de música** | além da imagem | não |
| **Extensões** | alcança Workspace, Maps e YouTube | não |

## Família Perplexity (agregador)

**Nenhum recurso no produto hoje**, e ele aparece em **27,6%** das stacks. É o maior buraco do
bloco "por dentro".

| Funcionalidade | O que faz |
|---|---|
| **Comet** | navegador com o motor de resposta na barra de endereço, lê a página aberta e executa tarefa. **Gratuito** |
| **Spaces** | organiza projeto de pesquisa, com arquivos e instrução própria |
| **Labs** | investe 10+ minutos e devolve peça acabada, incluindo mini-app |
| **Pages** | publica a pesquisa como página |
| **Model Council** | compara as respostas de GPT, Claude e Gemini lado a lado |
| **Deep Research** | relatório com fonte |

## Família Grok (agregador)

**Nenhum recurso no produto hoje.** Aparece em 1,2% das stacks, então o custo de não ter é baixo.

| Funcionalidade | O que faz |
|---|---|
| **DeepSearch** | quebra a pergunta em sub-buscas na web e no X, até 10 passos |
| **Grok Imagine** | imagem e vídeo, com texto mais nítido desde agosto/2026 |
| **Grok Build** | agente que gera aplicação a partir da descrição |
| **Companions** | personagens 3D com voz, só no celular |

---

## O que dá para fazer com isto, em ordem de retorno

**1. Encher o bloco "por dentro" das nove que não têm.** O Perplexity é o mais urgente pelos
27,6%, e o Comet é o tipo de coisa que ninguém sabe que existe e é gratuita. Não mexe em peso,
não mexe em preço, e é exatamente o que o produto promete entregar.

**2. Completar as quatro que já têm.** Canvas, Projects e Tasks no ChatGPT; Artifacts e Skills
no Claude; Gemini Live e Spark no Gemini. Cada linha nova é uma chance a mais de a IA achar o
recurso que serve para o caso da pessoa, já que ela só pode citar o que está na lista.

**3. Categorias que o catálogo não cobre**, e isso é decisão de produto, não de manutenção:

| Categoria | Quem domina | Observação |
|---|---|---|
| design de marca e social | **Canva, com o Magic Studio** | o mais relevante para o público brasileiro, e não tem equivalente no catálogo |
| edição de vídeo | **Runway** | remoção de fundo, inpainting, troca de fundo verde |
| avatar e dublagem | **HeyGen** | traduz e dubla vídeo em mais de 175 idiomas |
| música | **Suno** | trilha e música com letra |

**A régua para decidir isso já existe no repo** e não se reabre por empolgação: entra no
catálogo o que o Alison usa de verdade, porque a LP promete "onde eu não uso de verdade, eu não
opino", e cada ferramenta nova precisa de peso, custo conferido, primeiro passo e prompt, senão
vira enchimento que dilui a stack.

## Confiança das fontes desta rodada

`oficial`: Claude e Gemini. `agregador`: ChatGPT, Perplexity e Grok, porque as páginas
respondem 403 para leitura automatizada. Recurso não é preço, então o risco de errar é menor,
mas a regra do produto continua: a IA só pode citar o que está na lista, e a lista só recebe o
que foi conferido.
