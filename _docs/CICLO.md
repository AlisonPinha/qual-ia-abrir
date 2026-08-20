# O ciclo de trabalho

Protocolo para atacar a fila sem perguntar a cada passo, e sem inventar trabalho quando ela
acaba. Vale para o Claude, em qualquer sessão.

## Os seis passos, em ordem

**1. Verificar o que falta.** Ler `PLANO-EXECUCAO.md` e listar o que ainda não tem `~~`.
Separar em três pilhas: *só depende do Claude*, *depende do Alison*, *depende de tráfego*.
Trabalhar só na primeira.

**2. Conferir no playbook.** Antes de escrever código, achar o item em
`01 - Projects/Qual IA Usar/Qual IA Usar - Plano Low Ticket.md` (vault) e ler o que ele manda.
Duas coisas saem daí: o desenho certo e o ganho declarado. **Se o item não estiver no playbook,
dizer isso na hora de entregar**: pode ser boa ideia nossa, mas não tem lastro medido.

**3. Fazer.** Regras do repo valem sempre: `dados.json` é a fonte, `public/` é gerado, peso
mexido pede `testar_motor.mjs` com o efeito registrado, e nada de escassez ou prova social
inventada.

**4. Auditar.** Nesta ordem, e nenhuma etapa é opcional:

| Etapa | O que é |
|---|---|
| Critério antes do browser | escrever o que aprova a mudança, antes de abrir o navegador |
| QA local | `playwright-skill` contra o build local, com screenshot salvo no scratchpad |
| Olhar o print | teste verde não vê layout quebrado, botão apagado nem ruído na tela |
| Console | `pageerror` e erro de console fazem parte do critério, não são detalhe |
| Loop | reprovou, corrige e roda de novo. Sem teto de tentativas: o que autoriza rodar longe é ter verificação automática. Escalar só quando duas voltas seguidas derem o mesmo resultado |
| Regressão | antes de publicar mudança grande. Custa 1 chamada ao `/api/mapa` e 3 ao `/api/plano`, e o limite por IP permite ~2 rodadas por hora |

**Quando o teste falha, decidir de quem é o defeito.** Metade das falhas desta bateria foi do
teste, não do produto: contador que "mentia" e estava certo, rótulo que mudou, cálculo com um
`+1` a mais. Corrigir o teste é resultado legítimo, desde que dito.

**5. Registrar.** Marcar `~~feito~~` no `PLANO-EXECUCAO.md` com o critério que passou, escrever
no `STATUS.md` o que foi medido, commitar com conventional commit, e atualizar o playbook do
vault quando o item era de lá. Número medido entra no texto: "582px abaixo da dobra" vale mais
que "melhorei o botão".

**6. Próximo.** Voltar ao passo 1.

## Quando parar

- A pilha *só depende do Claude* esvaziou. **Parar e listar o que sobrou, com o motivo de cada
  um.** Não inventar tarefa para continuar rodando.
- O item precisa de decisão de produto (preço, oferta, o que vender depois). Perguntar, não
  decidir sozinho.
- O item exige credencial, gravação ou verba. Documentar o que falta e seguir para o próximo.
- Duas voltas seguidas de QA sem mudar o resultado. Parar e reportar o ponto exato.

## O que nunca entra, mesmo que o playbook peça

- Prova social, depoimento ou número de resultado que não aconteceram.
- Escassez sem limite real ("só nesta tela" quando não é verdade).
- Promessa na tela sem o código que a garante.
- Nome de ferramenta do produto pago vazando para a página de venda.

## O teto real desta fila

O playbook tem nove frentes. As que sobram dependem de **gravação** (VSL, criativos),
**verba** (teste seco de nome; as duas contas de anúncio já existem), **decisão de produto** (captura de contato,
downsell) ou **tráfego rodando** (todo o bloco de medição e os testes A/B). Nenhuma
delas fecha sem o Alison, e o ciclo não deve fingir que fecha.
