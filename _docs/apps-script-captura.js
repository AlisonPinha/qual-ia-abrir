/**
 * Recebe os dados do diagnóstico do qual-ia-abrir e grava numa planilha.
 *
 * Grava quatro coisas em abas diferentes, conforme o campo "tipo" do payload:
 *   - "lead"        → aba 'leads', com nome e WhatsApp (só quando o passo de contato existe)
 *   - "diagnostico" → aba 'diagnosticos', ANÔNIMO, toda vez que alguém termina o quiz
 *   - "presente"    → aba 'presentes', o que o comprador escolheu de próximo produto
 *   - "funil"       → aba 'abandonos', uma linha por pessoa que ABRIU o quiz, com a
 *                     pergunta em que ela parou. É a única que grava quem não terminou.
 *
 * A aba 'diagnosticos' é a que responde: qual perfil responde mais, qual dor
 * aparece, qual ferramenta o motor mais recomenda e o que ele mais manda cortar.
 *
 * A coluna 'descreveu' é a mais importante para o produto: é o que a pessoa escreveu
 * quando nenhuma opção era a tarefa dela. Tarefa que aparece muito ali é opção que
 * está faltando no quiz e precisa virar alternativa na próxima versão.
 *
 * A aba 'presentes' responde a outra pergunta: o que vender depois. Quem já comprou
 * escolhe o presente que quer, e o mais votado vira o próximo produto. É o único
 * lugar do funil em que a demanda do próximo lançamento é declarada por quem já pagou.
 *
 * Como ligar (5 minutos):
 *  1. Cria uma planilha no Google Sheets.
 *  2. Extensões → Apps Script, apaga o que estiver lá e cola este arquivo.
 *  3. Implantar → Nova implantação → tipo "App da Web".
 *       Executar como: Eu
 *       Quem tem acesso: Qualquer pessoa
 *  4. Copia a URL que termina em /exec e cola em _build/config.py:
 *       ANALITICO_URL para o anônimo (recomendado ligar primeiro)
 *       CAPTURA_URL   para o passo de nome e WhatsApp (opcional)
 *     Pode ser a MESMA URL nas duas: este script separa pelo "tipo".
 *  5. python3 _build/gerar.py && python3 _build/gerar_mapa.py && vercel deploy --prod --yes
 *
 * O site envia com mode:"no-cors", então a resposta não é lida: o que importa é gravar.
 */

const ABA_LEADS = 'leads';
const ABA_DIAG = 'diagnosticos';
const ABA_PRESENTE = 'presentes';
const ABA_FUNIL = 'abandonos';

// colunas de resposta gravadas em coluna própria; o resto vai no bruto
// Só o tronco tem coluna fixa. As perguntas de trilha mudam conforme a área, então
// não cabem em coluna própria: vão todas juntas na coluna 'trilha', no formato
// pid=resposta, e continuam inteiras no 'bruto'.
const PERGUNTAS = ['area', 'tempo_ia', 'quantas', 'gasto', 'generica',
                   'parada', 'refaz', 'horas', 'nivel', 'prazo', 'estilo',
                   'orcamento', 'onde'];

function trilhaDe(r) {
  return Object.keys(r).filter(function (k) { return PERGUNTAS.indexOf(k) < 0; })
               .map(function (k) { return k + '=' + r[k]; }).join(' | ');
}

function doPost(e) {
  // grava o corpo cru primeiro: se o formato mudar, o dado não se perde
  const bruto = (e && e.postData && e.postData.contents) || '';
  let d = {};
  try { d = JSON.parse(bruto); } catch (err) { d = {}; }

  if (d.tipo === 'diagnostico') gravarDiagnostico(d, bruto);
  else if (d.tipo === 'presente') gravarPresente(d, bruto);
  else if (d.tipo === 'funil') gravarFunil(d, bruto);
  else gravarLead(d, bruto);

  return ContentService.createTextOutput('ok');
}

/** Anônimo: nem nome nem WhatsApp entram aqui, de propósito. */
function gravarDiagnostico(d, bruto) {
  const aba = abaOu(ABA_DIAG, ['recebido em', 'origem'].concat(PERGUNTAS)
                              .concat(['trilha', 'descreveu', 'stack', 'cortar', 'bruto', 'utm']));
  const r = d.respostas || {};
  aba.appendRow(
    [new Date(), d.origem || '']
      .concat(PERGUNTAS.map(p => r[p] || ''))
      .concat([trilhaDe(r), d.descreveu || '',
               (d.stack || []).join(', '), (d.cortar || []).join(', '), bruto, d.utm || ''])
  );
}

/**
 * O presente escolhido por quem já comprou. Anônimo como o resto: o que interessa é a
 * contagem por opção, não quem votou. A coluna 'outro' é a que abre produto que não
 * está na lista, do mesmo jeito que 'descreveu' abre pergunta que falta no quiz.
 */
function gravarPresente(d, bruto) {
  const aba = abaOu(ABA_PRESENTE,
    ['recebido em', 'escolha', 'outro', 'area', 'stack', 'origem', 'utm', 'bruto']);
  aba.appendRow([new Date(), d.escolha || '', d.outro || '', d.area || '',
                 (d.stack || []).join(', '), d.origem || '', d.utm || '', bruto]);
}

function gravarLead(d, bruto) {
  const aba = abaOu(ABA_LEADS, ['recebido em', 'nome', 'whatsapp'].concat(PERGUNTAS)
                               .concat(['trilha', 'descreveu', 'stack', 'cortar', 'bruto', 'utm']));
  const r = d.respostas || {};
  aba.appendRow(
    [new Date(),
     d.nome || '',
     d.whatsapp ? "'" + d.whatsapp : '']    // apóstrofo: senão o Sheets come o zero à esquerda
      .concat(PERGUNTAS.map(p => r[p] || ''))
      .concat([trilhaDe(r), d.descreveu || '',
               (d.stack || []).join(', '), (d.cortar || []).join(', '), bruto, d.utm || ''])
  );
}

/**
 * O funil do quiz: uma linha por pessoa, com onde ela parou.
 *
 * A aba 'diagnosticos' só recebe quem TERMINA, então ela é o numerador sem denominador:
 * não dá para saber se as 19 perguntas seguram ou derrubam. Aqui entra todo mundo que
 * abriu o quiz, e a coluna 'concluiu' separa os dois grupos na mesma aba.
 *
 * Atualiza a linha em vez de acrescentar: cada saída da pessoa manda um sinal novo, e
 * sem o upsert quem troca de aba cinco vezes viraria cinco linhas. A chave é sid+origem,
 * porque a mesma pessoa passa pelo quiz do site e depois pelo do /mapa, e os dois
 * abandonos são coisas diferentes.
 *
 * O sid é sorteado no navegador e não identifica ninguém: existe só para a mesma pessoa
 * não virar várias linhas.
 */
function gravarFunil(d, bruto) {
  const aba = abaOu(ABA_FUNIL,
    ['primeiro sinal', 'último sinal', 'sid', 'origem', 'concluiu', 'parou em', 'pergunta',
     'posição', 'respondidas', 'total', 'area', 'utm', 'bruto']);
  // sem trava, dois sinais quase juntos da mesma pessoa acham a linha vazia e gravam duas
  const trava = LockService.getScriptLock();
  try { trava.waitLock(20000); } catch (err) { return; }
  try {
    const linha = acharLinha(aba, d.sid || '', d.origem || '');
    const agora = new Date();
    // quem já concluiu está congelado: se ela refizer o quiz, a linha voltaria a dizer
    // 'parou na pergunta 1' com 'concluiu sim' ao lado, e a conversão do quiz sumiria
    if (linha && aba.getRange(linha, 5).getValue() === 'sim') {
      aba.getRange(linha, 2).setValue(agora);
      return;
    }
    const dados = [agora, d.sid || '', d.origem || '', d.concluiu || '', d.pid || '',
                   d.pergunta || '', d.posicao || '', d.respondidas || 0, d.total || 0,
                   d.area || '', d.utm || '', bruto];
    // a coluna 1 é o primeiro sinal e nunca é reescrita: é a hora em que a pessoa chegou
    if (linha) aba.getRange(linha, 2, 1, dados.length).setValues([dados]);
    else aba.appendRow([agora].concat(dados));
  } finally {
    trava.releaseLock();
  }
}

/** A linha desta pessoa nesta origem, ou 0. De trás para frente: quem manda sinal agora
 *  quase sempre chegou há pouco. */
function acharLinha(aba, sid, origem) {
  const n = aba.getLastRow();
  if (n < 2 || !sid) return 0;
  const vals = aba.getRange(2, 3, n - 1, 2).getValues();
  for (let i = vals.length - 1; i >= 0; i--)
    if (vals[i][0] === sid && vals[i][1] === origem) return i + 2;
  return 0;
}

function abaOu(nome, cabecalho) {
  const planilha = SpreadsheetApp.getActiveSpreadsheet();
  let aba = planilha.getSheetByName(nome);
  if (!aba) {
    aba = planilha.insertSheet(nome);
    aba.appendRow(cabecalho);
    aba.setFrozenRows(1);
  }
  return aba;
}
