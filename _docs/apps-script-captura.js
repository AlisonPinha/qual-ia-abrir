/**
 * Recebe os leads do diagnóstico do qual-ia-abrir e grava numa planilha.
 *
 * Como ligar (5 minutos):
 *  1. Cria uma planilha no Google Sheets.
 *  2. Extensões → Apps Script, apaga o que estiver lá e cola este arquivo.
 *  3. Implantar → Nova implantação → tipo "App da Web".
 *       Executar como: Eu
 *       Quem tem acesso: Qualquer pessoa
 *  4. Copia a URL que termina em /exec e cola em CAPTURA_URL, no topo de _build/gerar.py.
 *  5. python3 _build/gerar.py && vercel deploy --prod --yes
 *
 * O site envia com mode:"no-cors", então a resposta não é lida: o que importa é gravar.
 */

const ABA = 'leads';

function doPost(e) {
  const planilha = SpreadsheetApp.getActiveSpreadsheet();
  let aba = planilha.getSheetByName(ABA);

  if (!aba) {
    aba = planilha.insertSheet(ABA);
    aba.appendRow(['recebido em', 'nome', 'whatsapp', 'área', 'tarefa',
                   'nível', 'orçamento', 'onde', 'stack', 'cortar', 'bruto']);
    aba.setFrozenRows(1);
  }

  // grava o corpo cru primeiro: se o formato mudar, o lead não se perde
  const bruto = (e && e.postData && e.postData.contents) || '';
  let d = {};
  try { d = JSON.parse(bruto); } catch (err) { d = {}; }

  const r = d.respostas || {};
  aba.appendRow([
    new Date(),
    d.nome || '',
    d.whatsapp ? "'" + d.whatsapp : '',       // apóstrofo: senão o Sheets come o zero à esquerda
    r.area || '', r.tarefa || '', r.nivel || '', r.orcamento || '', r.onde || '',
    (d.stack || []).join(', '),
    (d.cortar || []).join(', '),
    bruto
  ]);

  return ContentService.createTextOutput('ok');
}
