/**
 * Recebe os dados do diagnóstico do qual-ia-abrir e grava numa planilha.
 *
 * Grava três coisas em abas diferentes, conforme o campo "tipo" do payload:
 *   - "lead"        → aba 'leads', com nome e WhatsApp (só quando o passo de contato existe)
 *   - "diagnostico" → aba 'diagnosticos', ANÔNIMO, toda vez que alguém termina o quiz
 *   - "presente"    → aba 'presentes', o que o comprador escolheu de próximo produto
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
               (d.stack || []).join(', '), (d.cortar || []).join(', '), bruto])
  );
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
