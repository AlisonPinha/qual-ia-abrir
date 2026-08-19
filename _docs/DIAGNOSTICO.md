# O diagnóstico, por dentro

**Gerado por `_build/gerar_doc_quiz.py` a partir do `dados.json`. Não editar à mão:
rode o gerador depois de mexer no quiz.**

São **73 passos no banco** e **19 perguntas por pessoa** no caminho mais longo.
Quem nunca usou IA responde menos, porque três perguntas dependem de já ter ferramenta.

## O fluxo, na ordem

| # | Passo | Tipo | Só aparece se |
|---|---|---|---|
| 1 | `area` | pergunta, **vota** no motor | sempre |
| 2 | `s_tarefa` | pergunta, **vota** no motor | `area` = Saúde e consultório |
| 3 | `j_tarefa` | pergunta, **vota** no motor | `area` = Jurídico |
| 4 | `f_tarefa` | pergunta, **vota** no motor | `area` = Contábil e financeiro |
| 5 | `p_tarefa` | pergunta, **vota** no motor | `area` = Projeto e obra |
| 6 | `c_tarefa` | pergunta, **vota** no motor | `area` = Conteúdo e redes sociais |
| 7 | `n_tarefa` | pergunta, **vota** no motor | `area` = Negócio próprio ou gestão |
| 8 | `v_tarefa` | pergunta, **vota** no motor | `area` = Vendas e atendimento |
| 9 | `e_tarefa` | pergunta, **vota** no motor | `area` = Estudos ou docência |
| 10 | `t_tarefa` | pergunta, **vota** no motor | `area` = Técnico e desenvolvimento |
| 11 | `tarefa` | pergunta, **vota** no motor | `area` = Outra área |
| 12 | `l_tarefa` | pergunta, **vota** no motor | `area` = Vida pessoal, fora do trabalho |
| 13 | `tempo_ia` | pergunta, não vota (implicação e espelho) | sempre |
| 14 | `quantas` | pergunta, não vota (implicação e espelho) | sempre |
| 15 | `gasto` | pergunta, não vota (implicação e espelho) | `quantas` = Uma só ou Duas ou três ou Perdi a conta |
| 16 | `break1` | break: conteúdo entre blocos | sempre |
| 17 | `c_ideia` | pergunta, **vota** no motor | `area` = Conteúdo e redes sociais |
| 18 | `c_voz` | pergunta, **vota** no motor | `area` = Conteúdo e redes sociais |
| 19 | `n_dados` | pergunta, **vota** no motor | `area` = Negócio próprio ou gestão |
| 20 | `n_repete` | pergunta, **vota** no motor | `area` = Negócio próprio ou gestão |
| 21 | `v_canal` | pergunta, **vota** no motor | `area` = Vendas e atendimento |
| 22 | `v_pesquisa` | pergunta, **vota** no motor | `area` = Vendas e atendimento |
| 23 | `e_fonte` | pergunta, **vota** no motor | `area` = Estudos ou docência |
| 24 | `e_volume` | pergunta, **vota** no motor | `area` = Estudos ou docência |
| 25 | `t_base` | pergunta, **vota** no motor | `area` = Técnico e desenvolvimento |
| 26 | `t_entrega` | pergunta, **vota** no motor | `area` = Técnico e desenvolvimento |
| 27 | `o_saida` | pergunta, **vota** no motor | `area` = Outra área |
| 28 | `o_contexto` | pergunta, **vota** no motor | `area` = Outra área |
| 29 | `l_preco` | pergunta, **vota** no motor | `area` = Vida pessoal, fora do trabalho |
| 30 | `l_repete` | pergunta, **vota** no motor | `area` = Vida pessoal, fora do trabalho |
| 31 | `s_registro` | pergunta, **vota** no motor | `area` = Saúde e consultório |
| 32 | `s_dado` | pergunta, **vota** no motor | `area` = Saúde e consultório |
| 33 | `j_volume` | pergunta, **vota** no motor | `area` = Jurídico |
| 34 | `j_risco` | pergunta, **vota** no motor | `area` = Jurídico |
| 35 | `f_origem` | pergunta, **vota** no motor | `area` = Contábil e financeiro |
| 36 | `f_carteira` | pergunta, **vota** no motor | `area` = Contábil e financeiro |
| 37 | `p_entrada` | pergunta, **vota** no motor | `area` = Projeto e obra |
| 38 | `p_visual` | pergunta, **vota** no motor | `area` = Projeto e obra |
| 39 | `c_entrega` | pergunta, **vota** no motor | `area` = Conteúdo e redes sociais |
| 40 | `c_ritmo` | pergunta, **vota** no motor | `area` = Conteúdo e redes sociais |
| 41 | `n_entrega` | pergunta, **vota** no motor | `area` = Negócio próprio ou gestão |
| 42 | `n_ritmo` | pergunta, **vota** no motor | `area` = Negócio próprio ou gestão |
| 43 | `v_entrega` | pergunta, **vota** no motor | `area` = Vendas e atendimento |
| 44 | `v_ritmo` | pergunta, **vota** no motor | `area` = Vendas e atendimento |
| 45 | `e_entrega` | pergunta, **vota** no motor | `area` = Estudos ou docência |
| 46 | `e_ritmo` | pergunta, **vota** no motor | `area` = Estudos ou docência |
| 47 | `t_entrega_2` | pergunta, **vota** no motor | `area` = Técnico e desenvolvimento |
| 48 | `t_ritmo` | pergunta, **vota** no motor | `area` = Técnico e desenvolvimento |
| 49 | `s_entrega` | pergunta, **vota** no motor | `area` = Saúde e consultório |
| 50 | `s_ritmo` | pergunta, **vota** no motor | `area` = Saúde e consultório |
| 51 | `j_entrega` | pergunta, **vota** no motor | `area` = Jurídico |
| 52 | `j_ritmo` | pergunta, **vota** no motor | `area` = Jurídico |
| 53 | `f_entrega` | pergunta, **vota** no motor | `area` = Contábil e financeiro |
| 54 | `f_ritmo` | pergunta, **vota** no motor | `area` = Contábil e financeiro |
| 55 | `p_entrega` | pergunta, **vota** no motor | `area` = Projeto e obra |
| 56 | `p_ritmo` | pergunta, **vota** no motor | `area` = Projeto e obra |
| 57 | `o_entrega` | pergunta, **vota** no motor | `area` = Outra área |
| 58 | `o_ritmo` | pergunta, **vota** no motor | `area` = Outra área |
| 59 | `l_entrega` | pergunta, **vota** no motor | `area` = Vida pessoal, fora do trabalho |
| 60 | `l_ritmo` | pergunta, **vota** no motor | `area` = Vida pessoal, fora do trabalho |
| 61 | `break3` | break: conteúdo entre blocos | sempre |
| 62 | `generica` | pergunta, não vota (implicação e espelho) | `quantas` = Uma só ou Duas ou três ou Perdi a conta |
| 63 | `parada` | pergunta, não vota (implicação e espelho) | `quantas` = Uma só ou Duas ou três ou Perdi a conta |
| 64 | `refaz` | pergunta, não vota (implicação e espelho) | `quantas` = Uma só ou Duas ou três ou Perdi a conta |
| 65 | `horas` | pergunta, não vota (implicação e espelho) | sempre |
| 66 | `custo_parado` | pergunta, não vota (implicação e espelho) | `quantas` = Uma só ou Duas ou três ou Perdi a conta |
| 67 | `break2` | break: conteúdo entre blocos | sempre |
| 68 | `nivel` | pergunta, **vota** no motor | sempre |
| 69 | `prazo` | pergunta, não vota (implicação e espelho) | sempre |
| 70 | `estilo` | pergunta, não vota (implicação e espelho) | sempre |
| 71 | `orcamento` | pergunta, não vota (implicação e espelho) | sempre |
| 72 | `onde` | pergunta, **vota** no motor | sempre |
| 73 | `break_espelho` | espelho: repete as respostas antes do resultado | sempre |

## As 10 trilhas

Cada área tem 5 perguntas próprias. É o que faz a personalização ser real, e é a
parte do quiz que mais muda a stack.

**0. Conteúdo e redes sociais**
- `c_tarefa` Na sua semana de conteúdo, o que mais rouba tempo?
- `c_ideia` De onde sai a sua próxima ideia de post?
- `c_voz` Quando a IA escreve no seu lugar, sai com a sua voz?
- `c_entrega` Qual peça te dá mais trabalho para entregar pronta?
- `c_ritmo` Com que frequência você publica?

**1. Negócio próprio ou gestão**
- `n_tarefa` O que mais consome o seu dia na operação?
- `n_dados` Onde vivem os números do seu negócio?
- `n_repete` Qual tarefa se repete quase igual toda semana?
- `n_entrega` O que precisa sair pronto para cliente ou sócio ver?
- `n_ritmo` Quanto da sua operação é a mesma coisa toda semana?

**2. Vendas e atendimento**
- `v_tarefa` Onde a sua venda trava hoje?
- `v_canal` Onde a conversa de venda acontece?
- `v_pesquisa` Antes de falar com um cliente novo, você pesquisa sobre ele?
- `v_entrega` O que você manda para o cliente decidir?
- `v_ritmo` Quantas conversas novas você abre por semana?

**3. Estudos ou docência**
- `e_tarefa` O que mais toma o seu tempo de estudo ou de aula?
- `e_fonte` O que acontece quando você pede fonte pra IA?
- `e_volume` Por semana, quanto material você tem que dar conta?
- `e_entrega` O que você precisa produzir no fim?
- `e_ritmo` Você prefere consumir o material lendo ou ouvindo?

**4. Técnico e desenvolvimento**
- `t_tarefa` No trabalho técnico, onde o tempo vai embora?
- `t_base` O código onde você mexe é...
- `t_entrega` O que você precisa entregar mais rápido?
- `t_entrega_2` Fora código, o que você ainda precisa entregar?
- `t_ritmo` Quanto do seu trabalho é tarefa repetida?

**5. Saúde e consultório**
- `s_tarefa` Fora do atendimento, o que mais toma o seu tempo?
- `s_registro` Como o registro do atendimento acontece hoje?
- `s_dado` E dado de paciente, entra na ferramenta?
- `s_entrega` O que precisa sair pronto fora do atendimento?
- `s_ritmo` Quanto do que você escreve fora do atendimento se repete?

**6. Jurídico**
- `j_tarefa` Na rotina jurídica, onde o tempo vai embora?
- `j_volume` Qual costuma ser o tamanho do material de um processo seu?
- `j_risco` O que mais te trava pra usar IA no jurídico?
- `j_entrega` O que precisa sair pronto no fim?
- `j_ritmo` Quanto das suas peças nasce de um modelo parecido?

**7. Contábil e financeiro**
- `f_tarefa` No fechamento do mês, o que mais consome?
- `f_origem` De onde vêm os números que você trata?
- `f_carteira` Quantos clientes dependem de você todo mês?
- `f_entrega` O que o cliente recebe de você no fim do mês?
- `f_ritmo` Quanto do fechamento é igual todo mês?

**8. Projeto e obra**
- `p_tarefa` No projeto e na obra, o que mais come tempo?
- `p_entrada` O que o cliente te manda pra você orçar?
- `p_visual` O quanto a sua venda depende de a pessoa ver antes?
- `p_entrega` O que o cliente precisa ver para aprovar?
- `p_ritmo` Quanto do seu orçamento se repete entre projetos?

**9. Outra área**
- `tarefa` O que mais come o seu tempo hoje?
- `o_saida` No fim do dia, o que você entrega?
- `o_contexto` O seu trabalho é mais de lidar com...
- `o_entrega` Em que formato o seu trabalho chega em quem recebe?
- `o_ritmo` Quanto do seu trabalho se repete quase igual?

**10. Vida pessoal, fora do trabalho**
- `l_tarefa` Fora do trabalho, o que você mais quer resolver?
- `l_preco` Quando você vai comprar alguma coisa, o que trava?
- `l_repete` Tem alguma coisa que você fica conferindo toda semana?
- `l_entrega` O que você queria receber pronto?
- `l_ritmo` E com que frequência você precisa disso?

## O tronco, igual para todo mundo

| pid | Pergunta | Vota? |
|---|---|---|
| `area` | Onde a IA entra primeiro pra você? | sim |
| `tempo_ia` | Há quanto tempo você usa IA? | não |
| `quantas` | Quantas ferramentas de IA você tem abertas hoje? | não |
| `horas` | Somando tudo isso, quantas horas por semana você perde? | não |
| `nivel` | Como você usa IA hoje? | sim |
| `prazo` | Em quanto tempo você quer isso resolvido? | não |
| `estilo` | Você prefere dominar uma ferramenta ou saber trocar entre várias? | não |
| `orcamento` | Quanto você pode investir por mês em ferramenta? | não |
| `onde` | Onde você usa IA na maior parte do tempo? | sim |

## O que cada resposta faz com a stack

Só as perguntas que votam. Peso alto manda: 7 é resposta dominante, 1 a 3 é reforço.

### `area` Onde a IA entra primeiro pra você?

| Resposta | Favorece |
|---|---|
| Conteúdo e redes sociais | Higgsfield +3, Poppy AI +3, ChatGPT +2, Claude +2, Gemini +1 |
| Negócio próprio ou gestão | Claude +3, ChatGPT +2, Perplexity +2, Gemini +2, Claude Code +1 |
| Vendas e atendimento | Claude +3, ChatGPT +3, Perplexity +1, Gemini +1 |
| Estudos ou docência | Gemini +3, Perplexity +3, ChatGPT +2, Claude +1 |
| Técnico e desenvolvimento | Claude Code +4, Claude +2, Lovable +2, ChatGPT +1 |
| Saúde e consultório | Claude +3, Gemini +2, Perplexity +2, ChatGPT +2 |
| Jurídico | Claude +3, Gemini +3, Perplexity +2 |
| Contábil e financeiro | Gemini +3, Claude +3, ChatGPT +1 |
| Projeto e obra | Claude +2, Gemini +2, Higgsfield +2, ChatGPT +1 |
| Outra área | ChatGPT +2, Claude +2, Gemini +2, Perplexity +1 |
| Vida pessoal, fora do trabalho | ChatGPT +3, Perplexity +3, Gemini +1 |

### `s_tarefa` Fora do atendimento, o que mais toma o seu tempo?

| Resposta | Favorece |
|---|---|
| Evoluir prontuário e escrever laudo | Claude +4 |
| Estudar caso, artigo e protocolo | Perplexity +4, Gemini Notebook +3, Gemini +2 |
| Responder paciente e organizar agenda | ChatGPT +4, n8n +2 |
| Fazer conteúdo pra atrair paciente | Higgsfield +3, Claude +2, ElevenLabs +2, Poppy AI +1 |
| Faturamento, convênio e planilha | Gemini +4 |
| Treinar e organizar a equipe | Claude +3, Gemini +1 |
| Nenhuma dessas, a minha é outra | não vota |

### `j_tarefa` Na rotina jurídica, onde o tempo vai embora?

| Resposta | Favorece |
|---|---|
| Ler processo e peça longa | Gemini Notebook +7, Gemini +4 |
| Escrever petição e parecer | Claude +4 |
| Pesquisar jurisprudência e legislação | Perplexity +4, Gemini +1 |
| Redigir e revisar contrato | Claude +4, Gemini +1 |
| Explicar pro cliente sem juridiquês | ChatGPT +4 |
| Prazo, agenda e controle de processo | Gemini +3, Claude +1 |
| Nenhuma dessas, a minha é outra | não vota |

### `f_tarefa` No fechamento do mês, o que mais consome?

| Resposta | Favorece |
|---|---|
| Conferir e cruzar planilha | Gemini +4 |
| Ler norma, instrução e legislação | Perplexity +4, Gemini Notebook +3, Gemini +1 |
| Explicar o resultado pro cliente | Claude +4 |
| Responder cliente sobre imposto e guia | ChatGPT +4 |
| Montar relatório e apresentação | Gamma +7, Gemini +4, Claude +1 |
| Automatizar o que se repete todo mês | n8n +7, Claude Code +3, Lovable +1 |
| Nenhuma dessas, a minha é outra | não vota |

### `p_tarefa` No projeto e na obra, o que mais come tempo?

| Resposta | Favorece |
|---|---|
| Orçamento e composição de custo | Gemini +4, Claude +1 |
| Memorial, laudo e documento técnico | Claude +4 |
| Ler norma e projeto de terceiro | Gemini +3, Perplexity +2 |
| Montar a proposta que o cliente vê | Gamma +7, Gemini +3, Claude +2 |
| Imagem pra vender a ideia antes de existir | Higgsfield +4, Gemini +1 |
| Falar com cliente, fornecedor e equipe | ChatGPT +4 |
| Nenhuma dessas, a minha é outra | não vota |

### `c_tarefa` Na sua semana de conteúdo, o que mais rouba tempo?

| Resposta | Favorece |
|---|---|
| Escrever roteiro e legenda | Claude +4, ChatGPT +2 |
| Gravar e editar vídeo | ElevenLabs +7, Higgsfield +3, Poppy AI +2, Gemini +1 |
| Criar imagem, capa e thumbnail | Higgsfield +4, Gemini +2 |
| Achar pauta que ainda não saturou | Perplexity +3, Grok +3 |
| Entender por que um post foi e outro não | Poppy AI +4, Claude +2 |
| Responder comentário e direct | ChatGPT +3 |
| Nenhuma dessas, a minha é outra | não vota |

### `n_tarefa` O que mais consome o seu dia na operação?

| Resposta | Favorece |
|---|---|
| Escrever proposta, contrato e e-mail | Claude +4, ChatGPT +1 |
| Olhar número e planilha pra decidir | Gemini +4, Claude +2 |
| Pesquisar mercado, preço e concorrente | Perplexity +4, Gemini +1 |
| Documentar processo e treinar equipe | Claude +3, Gemini +2, ChatGPT +1 |
| Montar apresentação e relatório de reunião | Gamma +7, Gemini +4, Claude +2 |
| Apagar incêndio de sistema que ninguém cuida | n8n +7, Claude Code +3, Lovable +2 |
| Nenhuma dessas, a minha é outra | não vota |

### `v_tarefa` Onde a sua venda trava hoje?

| Resposta | Favorece |
|---|---|
| Achar e qualificar quem vale o tempo | Perplexity +4, ChatGPT +1 |
| Escrever a primeira mensagem sem parecer robô | Claude +4, ChatGPT +2 |
| Responder objeção na hora, no WhatsApp | ChatGPT +4, Claude +2 |
| Montar proposta e fazer follow-up | Claude +3, Gamma +3, ChatGPT +2, Gemini +1 |
| Organizar o que foi conversado com cada um | Gemini +3, n8n +3, Claude +2 |
| Entender por que o cliente sumiu | Claude +3, Perplexity +2 |
| Nenhuma dessas, a minha é outra | não vota |

### `e_tarefa` O que mais toma o seu tempo de estudo ou de aula?

| Resposta | Favorece |
|---|---|
| Ler material longo e denso | Gemini Notebook +7, Gemini +4 |
| Preparar aula, slide e material | Gemini +3, Claude +3, Gemini Notebook +3, Gamma +3 |
| Escrever trabalho, artigo ou relatório | Claude +4, Gemini +1 |
| Corrigir e dar devolutiva | Claude +3, Gemini +2 |
| Achar fonte que dá pra citar | Perplexity +4, Gemini Notebook +3, Gemini +1 |
| Explicar de um jeito que a pessoa entenda | ChatGPT +3, Claude +2 |
| Nenhuma dessas, a minha é outra | não vota |

### `t_tarefa` No trabalho técnico, onde o tempo vai embora?

| Resposta | Favorece |
|---|---|
| Escrever código novo | Claude Code +4 |
| Entender código que não é meu | Claude Code +4, Claude +2 |
| Caçar bug e corrigir | Claude Code +4 |
| Subir protótipo pra validar ideia | Lovable +4, Claude Code +2 |
| Documentar e explicar pra quem não é técnico | Claude +4, ChatGPT +2 |
| Pesquisar erro, biblioteca e documentação | Perplexity +4 |
| Nenhuma dessas, a minha é outra | não vota |

### `tarefa` O que mais come o seu tempo hoje?

| Resposta | Favorece |
|---|---|
| Escrever | Claude +4, ChatGPT +2, Gemini +1 |
| Pesquisar e entender material longo | Perplexity +4, Gemini +3, Grok +1 |
| Criar imagem e vídeo | Higgsfield +4, Gemini +2 |
| Organizar e decidir | Claude +3, ChatGPT +3 |
| Montar apresentação e relatório | Gemini +4, Claude +2, ChatGPT +1 |
| Construir site ou app | Claude Code +4, Lovable +3 |
| Nenhuma dessas, a minha é outra | não vota |

### `l_tarefa` Fora do trabalho, o que você mais quer resolver?

| Resposta | Favorece |
|---|---|
| Viagem: passagem, hospedagem e roteiro | ChatGPT +4, Perplexity +3 |
| Compra grande: pesquisar antes de gastar | Perplexity +4, ChatGPT +2 |
| Estudo por conta: concurso, idioma, curso | Gemini Notebook +4, Gemini +3, Perplexity +1 |
| Papelada: contrato, recurso, carta | Claude +4, Gemini +1 |
| Casa e dinheiro: conta, rotina, planilha | Gemini +4, ChatGPT +1 |
| Foto e vídeo pra guardar ou postar | Higgsfield +4, Gemini +1 |
| Nenhuma dessas, a minha é outra | não vota |

### `c_ideia` De onde sai a sua próxima ideia de post?

| Resposta | Favorece |
|---|---|
| Do que eu vejo no feed na hora | Grok +3, Perplexity +1 |
| De um banco de referências que eu guardo | Poppy AI +4, Gemini Notebook +2 |
| Do que cliente e seguidor perguntam | Claude +3, ChatGPT +2 |
| Do improviso, não tenho fonte fixa | Perplexity +2, Grok +2, ChatGPT +1 |

### `c_voz` Quando a IA escreve no seu lugar, sai com a sua voz?

| Resposta | Favorece |
|---|---|
| Sai genérico, dá pra ver que é IA | Claude +4, ChatGPT +1 |
| Sai perto, mas eu reescrevo tudo | Claude +3, ChatGPT +1 |
| Já ensinei o meu jeito e sai bom | Claude +2, Poppy AI +2 |
| Não deixo a IA escrever, só me ajuda a pensar | Claude +2, ChatGPT +2, ElevenLabs +1 |

### `n_dados` Onde vivem os números do seu negócio?

| Resposta | Favorece |
|---|---|
| Numa planilha que eu mesmo atualizo | Gemini +3 |
| Num sistema que exporta relatório | Gemini +3, Claude +2 |
| Espalhados em vários lugares | Claude +3, Gemini Notebook +3, Gemini +2 |
| Na minha cabeça e no extrato | Claude +2, ChatGPT +2 |

### `n_repete` Qual tarefa se repete quase igual toda semana?

| Resposta | Favorece |
|---|---|
| Relatório pra cliente ou sócio | Gemini +3, Claude +2, n8n +2 |
| Orçamento e proposta | Claude +4, ChatGPT +1 |
| Conteúdo e comunicação do negócio | ElevenLabs +7, ChatGPT +2, Claude +2, Higgsfield +2 |
| Cobrar gente e conferir entrega | n8n +7, Claude +2, ChatGPT +2 |
| Nenhuma, toda semana é diferente | Claude +2, Perplexity +2 |

### `v_canal` Onde a conversa de venda acontece?

| Resposta | Favorece |
|---|---|
| WhatsApp e direct | ChatGPT +3 |
| Reunião e ligação | Gemini +3, Claude +2 |
| E-mail e proposta formal | Claude +3, Gemini +1 |
| Presencial, olho no olho | ChatGPT +2, Claude +2 |

### `v_pesquisa` Antes de falar com um cliente novo, você pesquisa sobre ele?

| Resposta | Favorece |
|---|---|
| Sempre, e leva tempo demais | Perplexity +4, Gemini +1 |
| Só quando a conta é grande | Perplexity +3 |
| Quase nunca, vou pelo feeling | Perplexity +2, ChatGPT +2 |
| Queria, mas não sei o que procurar | Perplexity +3 |

### `e_fonte` O que acontece quando você pede fonte pra IA?

| Resposta | Favorece |
|---|---|
| Ela inventa referência que não existe | Gemini Notebook +7, Perplexity +4, Gemini +1 |
| Ela acha, mas conferir demora | Perplexity +3 |
| Uso só o que a instituição indica | Gemini +3, Gemini Notebook +3 |
| Não uso fonte, o conteúdo é meu | Claude +3, ChatGPT +1 |

### `e_volume` Por semana, quanto material você tem que dar conta?

| Resposta | Favorece |
|---|---|
| Alguns artigos | Perplexity +3 |
| Um livro ou uma apostila inteira | Gemini Notebook +7, Gemini +4 |
| Várias aulas gravadas | Gemini +3, Gemini Notebook +3, Poppy AI +2 |
| Não é volume, é dificuldade do conteúdo | Claude +4, ChatGPT +1 |

### `t_base` O código onde você mexe é...

| Resposta | Favorece |
|---|---|
| Meu, começado do zero | Claude Code +3, Lovable +2 |
| De um time, com histórico e review | Claude Code +4 |
| Legado que ninguém quer abrir | Claude Code +4, Claude +2 |
| Não é código, é sistema e no-code | Lovable +3, ChatGPT +2 |

### `t_entrega` O que você precisa entregar mais rápido?

| Resposta | Favorece |
|---|---|
| Feature em produção | Claude Code +4 |
| Protótipo pra mostrar pro cliente | Lovable +4 |
| Análise ou parecer técnico | Claude +4, Gemini +2 |
| Automação interna que ninguém quer fazer | n8n +7, Claude Code +3, Claude +2 |

### `o_saida` No fim do dia, o que você entrega?

| Resposta | Favorece |
|---|---|
| Texto e documento | Claude +4, Gamma +2, ChatGPT +1 |
| Decisão e resposta pra alguém | Claude +3, ChatGPT +2 |
| Material visual | Higgsfield +4, ElevenLabs +2, Gemini +1 |
| Atendimento e serviço | ChatGPT +3 |
| Sistema, planilha ou ferramenta | Claude Code +3, Gemini +2, n8n +2, Lovable +1 |

### `o_contexto` O seu trabalho é mais de lidar com...

| Resposta | Favorece |
|---|---|
| Gente | ChatGPT +3, Claude +2 |
| Documento, norma e regra | Claude +4, Gemini +2, Gemini Notebook +2 |
| Número e sistema | Gemini +3, Claude Code +1 |
| Coisa física, no mundo real | ChatGPT +2, Gemini +2, Perplexity +1 |

### `l_preco` Quando você vai comprar alguma coisa, o que trava?

| Resposta | Favorece |
|---|---|
| Não sei se o preço está bom mesmo | Perplexity +4, ChatGPT +2 |
| A IA me responde preço velho ou inventado | Perplexity +7, Grok +2 |
| Perco a noite abrindo dez abas | ChatGPT +4, Perplexity +2 |
| Compro e depois vejo mais barato | n8n +4, ChatGPT +2 |
| Não é preço, é decidir entre as opções | Claude +4, Perplexity +1 |

### `l_repete` Tem alguma coisa que você fica conferindo toda semana?

| Resposta | Favorece |
|---|---|
| Preço de passagem, produto ou aluguel | n8n +7, ChatGPT +2 |
| Notícia ou assunto que eu acompanho | Grok +4, Perplexity +3 |
| Prazo, boleto e vencimento | n8n +4, Gemini +2 |
| Nada, é sempre coisa diferente | não vota |

### `s_registro` Como o registro do atendimento acontece hoje?

| Resposta | Favorece |
|---|---|
| Digito durante ou logo depois da consulta | Claude +3 |
| Gravo e transcrevo depois | Gemini +4, Claude +1 |
| No sistema da clínica, com campo fixo | Claude +2, Gemini +2 |
| Escrevo à mão e passo a limpo | ChatGPT +3, Claude +1 |

### `s_dado` E dado de paciente, entra na ferramenta?

| Resposta | Favorece |
|---|---|
| Entra, e isso me preocupa | Claude +3, Perplexity +1 |
| Só entra dado sem identificação | Claude +2, Perplexity +2 |
| Nunca entra, uso só pra estudo e texto | Perplexity +3, Gemini +1 |
| Sinceramente, não sei o que pode | Claude +2, Perplexity +2 |

### `j_volume` Qual costuma ser o tamanho do material de um processo seu?

| Resposta | Favorece |
|---|---|
| Poucas páginas | Claude +3 |
| Centenas de páginas | Gemini Notebook +7, Gemini +4 |
| Áudio e vídeo de audiência | Gemini +4, Gemini Notebook +3, Claude +1 |
| Varia demais, nunca sei | Gemini +2, Claude +2 |

### `j_risco` O que mais te trava pra usar IA no jurídico?

| Resposta | Favorece |
|---|---|
| Ela inventa jurisprudência que não existe | Gemini Notebook +7, Perplexity +4, Gemini +1 |
| Sigilo do cliente e dado sensível | Claude +3, Perplexity +1 |
| O texto não sai com a minha técnica | Claude +4 |
| Nada, já uso todo dia | Claude +2, Gemini +2 |

### `f_origem` De onde vêm os números que você trata?

| Resposta | Favorece |
|---|---|
| Do sistema contábil, em relatório | Gemini +3, Claude +1 |
| Da planilha do cliente, cada uma de um jeito | Gemini +3, Claude +2 |
| De PDF e extrato | Gemini +4 |
| Digitado na mão, um por um | n8n +3, Gemini +2, Claude Code +2 |

### `f_carteira` Quantos clientes dependem de você todo mês?

| Resposta | Favorece |
|---|---|
| Um ou dois | Claude +3 |
| Até dez | Claude +2, Gemini +2 |
| Dezenas | Gemini +3, Claude +1 |
| Mais de cem | Gemini +3, n8n +3, Claude Code +2 |

### `p_entrada` O que o cliente te manda pra você orçar?

| Resposta | Favorece |
|---|---|
| Planta e projeto | Gemini +4 |
| Foto e medida no WhatsApp | ChatGPT +3, Gemini +2 |
| Só a ideia, na conversa | Claude +3, ChatGPT +2 |
| Cada um manda de um jeito | Claude +2, Gemini +2 |

### `p_visual` O quanto a sua venda depende de a pessoa ver antes?

| Resposta | Favorece |
|---|---|
| Muito, sem imagem não fecha | Higgsfield +4, Gemini +1 |
| Ajuda, mas não é o que decide | Higgsfield +2, Claude +2 |
| Nada, é decisão técnica | Claude +3, Gemini +1 |
| Hoje eu mostro foto de obra antiga | Higgsfield +3, Claude +1 |

### `c_entrega` Qual peça te dá mais trabalho para entregar pronta?

| Resposta | Favorece |
|---|---|
| Vídeo editado | Higgsfield +7, ElevenLabs +3 |
| Carrossel e imagem | Higgsfield +7, Gamma +2 |
| Texto longo, roteiro ou newsletter | Claude +5, ChatGPT +2 |
| Narração e áudio | ElevenLabs +7 |
| Apresentação para marca ou cliente | Gamma +7 |

### `c_ritmo` Com que frequência você publica?

| Resposta | Favorece |
|---|---|
| Todo dia | n8n +5, ChatGPT +3 |
| Umas três vezes por semana | ChatGPT +2, Claude +2 |
| Uma vez por semana | Claude +3 |
| Quando dá, sem ritmo fixo | Claude +2 |

### `n_entrega` O que precisa sair pronto para cliente ou sócio ver?

| Resposta | Favorece |
|---|---|
| Apresentação e relatório visual | Gamma +7 |
| Proposta e contrato | Claude +5 |
| Planilha e número consolidado | Gemini +5 |
| Mensagem e e-mail do dia a dia | ChatGPT +4 |

### `n_ritmo` Quanto da sua operação é a mesma coisa toda semana?

| Resposta | Favorece |
|---|---|
| Quase tudo, muda só o nome do cliente | n8n +7 |
| Metade | n8n +4, Gemini +2 |
| Pouca coisa, cada semana é diferente | Claude +3 |

### `v_entrega` O que você manda para o cliente decidir?

| Resposta | Favorece |
|---|---|
| Proposta ou apresentação | Gamma +7 |
| Mensagem escrita | ChatGPT +4, Claude +3 |
| Áudio | ElevenLabs +7 |
| Planilha com preço e condição | Gemini +5 |

### `v_ritmo` Quantas conversas novas você abre por semana?

| Resposta | Favorece |
|---|---|
| Mais de 30 | n8n +7 |
| Entre 10 e 30 | n8n +4, ChatGPT +2 |
| Menos de 10 | Claude +3, Perplexity +2 |

### `e_entrega` O que você precisa produzir no fim?

| Resposta | Favorece |
|---|---|
| Aula ou apresentação | Gamma +7 |
| Resumo e fichamento | Gemini Notebook +5, Claude +2 |
| Texto autoral, artigo ou TCC | Claude +5 |
| Exercício, prova ou correção | ChatGPT +4 |

### `e_ritmo` Você prefere consumir o material lendo ou ouvindo?

| Resposta | Favorece |
|---|---|
| Lendo | Gemini Notebook +3, Claude +2 |
| Ouvindo, aproveito o deslocamento | Gemini Notebook +5, ElevenLabs +4 |
| Tanto faz, o que for mais rápido | Perplexity +2 |

### `t_entrega_2` Fora código, o que você ainda precisa entregar?

| Resposta | Favorece |
|---|---|
| Tela ou protótipo que dá para clicar | Lovable +7 |
| Documentação e explicação para outra equipe | Claude +5, Gamma +3 |
| Integração entre sistemas | n8n +7 |
| Só código, o resto não é comigo | Claude Code +4 |

### `t_ritmo` Quanto do seu trabalho é tarefa repetida?

| Resposta | Favorece |
|---|---|
| Muita coisa, é sempre o mesmo caminho | n8n +7 |
| Alguma coisa | n8n +3, Claude Code +2 |
| Quase nada, cada problema é novo | Claude +3 |

### `s_entrega` O que precisa sair pronto fora do atendimento?

| Resposta | Favorece |
|---|---|
| Laudo, evolução e documento clínico | Claude +5 |
| Material de orientação para o paciente | Gamma +7 |
| Áudio de orientação | ElevenLabs +7 |
| Resumo de artigo e protocolo | Gemini Notebook +5 |

### `s_ritmo` Quanto do que você escreve fora do atendimento se repete?

| Resposta | Favorece |
|---|---|
| Quase tudo, muda só o paciente | n8n +5, Claude +3 |
| Metade | Claude +3 |
| Cada caso é bem diferente | Claude +4 |

### `j_entrega` O que precisa sair pronto no fim?

| Resposta | Favorece |
|---|---|
| Petição e peça processual | Claude +7 |
| Parecer e memorando | Claude +5 |
| Resumo do caso para o cliente entender | Gamma +5, Claude +2 |
| Contrato e minuta | Claude +5 |

### `j_ritmo` Quanto das suas peças nasce de um modelo parecido?

| Resposta | Favorece |
|---|---|
| Quase todas | n8n +4, Claude +4 |
| Metade | Claude +3 |
| Cada caso do zero | Claude +4, Gemini Notebook +2 |

### `f_entrega` O que o cliente recebe de você no fim do mês?

| Resposta | Favorece |
|---|---|
| Relatório visual | Gamma +7 |
| Planilha e demonstrativo | Gemini +5 |
| Explicação escrita do que aconteceu | Claude +4, ChatGPT +2 |
| Guia, obrigação e prazo | ChatGPT +3 |

### `f_ritmo` Quanto do fechamento é igual todo mês?

| Resposta | Favorece |
|---|---|
| Quase tudo | n8n +7 |
| Metade | n8n +4 |
| Muda bastante de mês para mês | Gemini +3 |

### `p_entrega` O que o cliente precisa ver para aprovar?

| Resposta | Favorece |
|---|---|
| Imagem ou render do resultado | Higgsfield +7 |
| Proposta e apresentação | Gamma +7 |
| Planilha de orçamento | Gemini +5 |
| Vídeo do projeto | Higgsfield +7 |

### `p_ritmo` Quanto do seu orçamento se repete entre projetos?

| Resposta | Favorece |
|---|---|
| Quase tudo, muda a metragem | n8n +7 |
| Metade | n8n +3, Gemini +2 |
| Cada projeto é um caso | Claude +3 |

### `o_entrega` Em que formato o seu trabalho chega em quem recebe?

| Resposta | Favorece |
|---|---|
| Documento ou texto | Claude +4 |
| Apresentação | Gamma +7 |
| Planilha e número | Gemini +5 |
| Áudio ou vídeo | ElevenLabs +5, Higgsfield +4 |
| Conversa, não vira arquivo | ChatGPT +4 |

### `o_ritmo` Quanto do seu trabalho se repete quase igual?

| Resposta | Favorece |
|---|---|
| Quase tudo | n8n +7 |
| Metade | n8n +3 |
| Quase nada | Claude +3 |

### `l_entrega` O que você queria receber pronto?

| Resposta | Favorece |
|---|---|
| Um roteiro de viagem fechado, com preço | ChatGPT +4, Perplexity +2 |
| Um resumo do que eu tenho que estudar | Gemini Notebook +7, Gemini +2 |
| O material pra ouvir enquanto faço outra coisa | ElevenLabs +7, Gemini Notebook +3 |
| Um texto pronto pra enviar, tipo carta ou recurso | Claude +4 |
| Uma planilha que se atualiza sozinha | n8n +4, Gemini +3 |
| Um aplicativo simples, só pra mim | Lovable +7, Claude Code +2 |
| Uma imagem ou um vídeo bem feito | Higgsfield +7, Gemini +1 |

### `l_ritmo` E com que frequência você precisa disso?

| Resposta | Favorece |
|---|---|
| Toda semana | n8n +3 |
| Algumas vezes por mês | não vota |
| Só quando surge | Claude +2 |

### `nivel` Como você usa IA hoje?

| Resposta | Favorece |
|---|---|
| Quase nunca abro | ChatGPT +2, Gemini +1 |
| Abro um chat de vez em quando | ChatGPT +1, Claude +1, Gemini +1 |
| Uso todo dia, mas sem método | Claude +2, Perplexity +1, Higgsfield +1 |
| Uso pra trabalhar e quero avançar | Claude Code +2, Claude +2, Higgsfield +1, Poppy AI +1 |

### `onde` Onde você usa IA na maior parte do tempo?

| Resposta | Favorece |
|---|---|
| No celular | ChatGPT +1, Gemini +1 |
| No computador | Claude +1, Claude Code +1 |

## As regras do motor, que valem depois dos pesos

Estão em `_build/motor.js`, e é aqui que a maior parte das surpresas mora.

**Teto por orçamento.** A faixa declarada tira da mesa o que não cabe nela:

| Orçamento | Aceita |
|---|---|
| Nada, quero só o que é grátis | só o que tem camada gratuita de verdade |
| Até R$ 150, uma assinatura | ferramenta de faixa até 1 |
| De R$ 150 a R$ 400, duas ou três | ferramenta de faixa até 2 |
| Acima de R$ 400, sem restrição | ferramenta de faixa até 3 |

**Quantas entram já:** `cabem` = [0, 1, 3, 3], uma posição por faixa de orçamento.
Quem responde "Dominar uma a fundo" recebe uma só na primeira camada.

**No celular** saem Claude Code, Lovable, n8n, que não se opera pelo telefone.

**A stack nunca volta com menos de três.** Se o filtro esvaziar o ranking, entra
especialista antes de generalista, porque quem paga não paga para ouvir as quatro óbvias.

## Onde mexer, por tipo de mudança

| Quero | Mexo em |
|---|---|
| Trocar texto de pergunta ou opção | `_build/dados.json`, bloco `diagnostico.perguntas` |
| Mudar o que uma resposta favorece | os pesos da opção, no mesmo bloco |
| Criar pergunta de trilha | mesma lista, com `{"area": [n]}` no fim. **As 10 trilhas precisam ficar do mesmo tamanho**, ou o build para |
| Criar pergunta condicional | mesmo formato, com a condição que não seja de área |
| Mudar preço, custo ou camada gratuita | `diagnostico.acesso` |
| Mudar regra de bolso, celular ou ordem | `_build/motor.js` mais as constantes em `diagnostico` |
| Mudar o que o espelho repete | `diagnostico.espelho` |

**Depois de qualquer mudança:** `node _build/testar_motor.mjs`, que pega peso apontando
para ferramenta inexistente, trilha de tamanho errado e ferramenta que virou peso morto.
E rode este gerador de novo, senão este documento passa a mentir.
