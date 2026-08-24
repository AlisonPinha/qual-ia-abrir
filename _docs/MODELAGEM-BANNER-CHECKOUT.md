# Modelagem do banner do checkout

O checkout da Cakto do `Qual IA Usar?` estava **totalmente pelado até 23/08/2026**: nenhum
componente visual, nenhuma imagem de produto, nenhum selo, nenhum depoimento, nenhum exit
popup, nenhuma notificação. Só o formulário padrão da plataforma, com o preço aparecendo pela
primeira vez como `R$ 66,01` mais `Taxa de serviço R$ 0,99`. Quem chega da LP, onde tudo é
escuro, roxo e nomeado, cai numa tela branca que não parece o mesmo produto.

Esta doc é a peça que fecha esse buraco, e a referência que manda nela.

---

## A referência: o corte do podcast da VTurb

Reel `Dbvj9W6kW09`, dois convidados falando de checkout de low ticket. É a única referência
sobre banner de checkout que tem número atrás, e o número é deles, não do mercado:

> "Banner de checkout de low ticket, meu, já teve teste A/B de banner que nós fizemos, que a
> oferta tava **empatando**, de trocar o banner, subiu pra ROAS muito absurdo."

> "Nossa conversão de checkout é **30, 40%**, mano."

> "Isso daí, cara, a gente já **salvou a oferta** por essa questão."

> "Às vezes é **uma única coisa no funil** que vai aumentar o teu ROI de 1.1 pra 2."

E a régua que o vídeo tira disso, dita como princípio: **nunca mandar a pessoa jogar fora o que
deu perspectiva de resultado.** A oferta que empata não é uma oferta ruim, é uma oferta cuja
última tela não entrega nada.

### O que eles dizem que o banner precisa ter

O mockup que aparece no vídeo (1:03) tem, em ordem de leitura:

| # | Elemento | Como está no vídeo |
|---|---|---|
| 1 | **Preço** | caixa amarela `POR APENAS / R$XX,XX`, e eles insistem: "é ali o preço, bem pequenininho, sei lá, 29,90" |
| 2 | **Mockup do produto** | notebook com a tela, "pra pessoa ficar verossímil" |
| 3 | **Promessa primária** | um campo escrito literalmente `Promessa PRIMÁRIA` |
| 4 | **A principal objeção quebrada** | `SEM PRECISAR (OBJEÇÃO PRINCIPAL)`, na fórmula "você vai conquistar isso sem isso" |
| 5 | **Acesso imediato** | headline `ACESSO IMEDIATO AO (produto)!` |
| 6 | **Garantia** | selo de 30 dias no canto |

Mais o rodapé: `EFETUE A INSCRIÇÃO E RECEBA IMEDIATAMENTE NO SEU E-MAIL!`

"Isso tudo num banner, mano?" "Num banner."

---

## Como isso virou a nossa peça

`_build/gerar_banner.js` monta os seis elementos a partir do `dados.json`, e o `banner` de lá é
o único lugar onde essa copy se edita. Nada disso é digitado no HTML.

| Elemento | De onde sai |
|---|---|
| Preço | `oferta.preco`, ancorado em `oferta.de` |
| Mockup | a tela real do `/mapa`, capturada na hora (ver abaixo) |
| Promessa primária | `banner.promessa` |
| Objeção quebrada | `banner.objecao` |
| Acesso imediato | `banner.headline` e `banner.entrega` |
| Garantia | `banner.garantia` |
| Reforços | `banner.reforcos` |

### Três decisões que não se copiam do vídeo

**A garantia é de 7 dias, não de 30.** O selo do mockup do vídeo diz 30, e o nosso produto
vende 7 (`oferta.garantias`). Copiar o selo seria anunciar uma garantia que a Cakto não
cumpre, ou seja, reembolso pedido no dia 20 com razão de sobra.

**O banner não cita o mecanismo.** O mesmo arquivo sobe nos quatro produtos do teste de nome, e
"Regra das 3 IAs" num checkout de "Método das 3 Abas" contradiz quem acabou de clicar. Mesma
razão pela qual existe `diagnostico.crencaCurta`. Se um dia o teste de nome fechar, aí sim cabe
uma versão por variante.

**O mockup não é desenho.** O gerador sobe as páginas num servidor local, responde o quiz
inteiro pela primeira opção, pula a tela de upsell e fotografa o card da primeira ferramenta do
`#res-stack`. O que a pessoa vê no checkout é literalmente a tela que ela vai receber, com o
logo, o custo real e o "Dentro dela, o que quase ninguém usa". Isso também significa que o
mockup **envelhece junto com o produto**: mudou o catálogo, roda de novo e o banner acompanha.

---

## Como rodar

```bash
python3 _build/gerar_mapa.py                     # escreve o _private/mapa.html que vira mockup
cd ~/.claude/skills/playwright-skill
node ~/Projetos/qual-ia-abrir/_build/gerar_banner.js
```

O playwright não é dependência do projeto: ele vive na skill, e é de lá que o script roda, do
mesmo jeito que o `_build/regressao.js`.

Saída em `_private/checkout/`:

| Arquivo | Tamanho | Onde vai |
|---|---|---|
| `banner-desktop.png` | 1640x600 | componente Imagem na linha do topo, visão desktop |
| `banner-mobile.png` | 1080x1212 | mesma linha, visão mobile |
| `mockup.png` | recorte do card | insumo dos dois, não sobe sozinho |

---

## Como subir na Cakto

Painel → **Produtos** → o produto → aba **Checkout** → os três pontos do `Checkout Principal` →
**Personalizar**. Abre o Checkout Builder, com o alternador desktop/mobile no topo e a linha
vazia "Arraste componentes aqui" acima do formulário.

Arrastar **Imagem** para essa linha, subir o arquivo, esticar pelo canto inferior direito até a
largura da linha, alinhamento centralizado, e **Salvar**. Sem URL de redirecionamento: o banner
não é para ser clicado, ele é para ser lido.

**Desktop e mobile são duas telas independentes**, não uma responsiva. A visão mobile começa
vazia e tem um botão "Copiar Do Desktop" que a preenche com a peça deitada, que é justamente o
que não se quer aqui. Cada visão recebe o seu arquivo.

**A Cakto não impõe dimensão nenhuma.** Aceita JPG e PNG até 10 MB, o componente é
redimensionável e a imagem escala para a largura do container. As medidas acima foram escolhidas
por nós, não por ela. **Ela reprocessa o arquivo:** o PNG de 1640x600 chega ao CDN como
1599x585, e é servido em `cdn-checkout.cakto.com.br`.

**São cinco produtos, então são cinco vezes.** Controle, abas, regra, stack e o upsell. O banner
é o mesmo nos quatro do teste de nome; o upsell pede peça própria, com a copy do
`dados.json > upsell`, e ela ainda não existe.

### O que ficou no ar em 23/08/2026

Os **quatro produtos do teste de nome**, desktop e mobile, conferidos em produção pela imagem
que o navegador realmente carregou, não por screenshot:

| Produto | Checkout | Desktop | Mobile |
|---|---|---|---|
| Qual IA Usar? (controle) | `3fxqxg5_1049811` | OK | OK |
| Método das 3 Abas | `32hjw7j_1049893` | OK | OK |
| Regra das 3 IAs | `8t2cigd_1049903` | OK | OK |
| Stack Mínima | `3dtj6z8_1049909` | OK | OK |

Oito de oito. No desktop o banner renderiza em **720x263** no topo do card; no celular, em
**390x438**, colado no topo da tela.

**Cuidado ao validar por screenshot:** a imagem vem do CDN e demora a decodificar, então uma
captura logo depois do load mostra a faixa vazia e parece que o banner não subiu. Medir pela
`naturalWidth` da imagem é a leitura confiável; o screenshot só depois.

---

## O que medir depois de subir

A visita do checkout já é contada pela Cakto (26 até 23/08, quase todas de QA). O que muda com
o banner é a razão entre **visita do checkout** e **venda**, e essa é a única leitura que
interessa aqui. Não é view, não é tempo na página.

**A leitura só existe com tráfego real.** Até 23/08 o projeto tem zero visita paga, então subir
o banner hoje não prova nada sozinho: ele entra como parte da montagem, e o teste A/B dele vem
depois que a oferta tiver volume, exatamente na ordem que o vídeo descreve (a oferta empatando
primeiro, o banner depois).

**No celular o banner empurra o formulário, e o número real é 534.** Medido em produção numa
tela de 390x844: o banner ocupa 438 px e o campo de nome começa em **534 px de 844**, ou seja,
ainda na primeira tela, com o botão abaixo dela. É consequência conhecida da receita, não
defeito, mas é o primeiro lugar para cortar se a conversão mobile cair.

**O checkout no celular é escuro**, e o banner escuro entrou como continuação da tela em vez de
bloco colado. No desktop o checkout é claro e o banner aparece como um painel dentro do card.
As duas leituras funcionam, mas foi sorte, não projeto: se a Cakto trocar o tema, a peça mobile
é a que sente primeiro.

---

## O que este documento não resolve

- **O banner do upsell** (`j79id6y_1051180`, R$ 130). O gerador não tem variante dele.
- **Os outros componentes que a Cakto oferece e o checkout não usa:** Depoimento (não temos
  nenhum: `prova.depoimentos` está vazio), Cronômetro (seria escassez inventada, proibida no
  projeto), Exit Popup, Notificação e Chat, todos desligados. Cada um é uma decisão à parte.
- **A Imagem do Produto** na aba Geral (300x250, para a área de membros e o programa de
  afiliados) também está vazia, e não é este arquivo.
