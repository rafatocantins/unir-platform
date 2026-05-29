// == PROJETO: UNIR_Assinaturas_Webhook
// Apps Script que recebe dados do formulário e escreve na Sheet UNIR_Assinaturas_Fundacao
//
// COMO USAR:
// 1. Abrir https://script.google.com/home
// 2. Criar novo projeto
// 3. Colar este código
// 4. Fazer deploy → Web app → "Anyone" (ou "Anyone with link")
// 5. Copiar URL e colocar no main.js como SHEET_API_URL
//
// Este script executa como o dono (tu), por isso só TU consegues
// mexer na Sheet. O webhook recebe dados mas não consegue ler nada.

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    
    const sheet = SpreadsheetApp.openById('1Cva-qRD8Z3CoLSxuJR1sQqv5MnHVtpGuUgt6Exenw20')
      .getSheetByName('Sheet1');
    
    const row = [
      new Date(),                       // Timestamp
      data.nome,                        // Nome Completo
      data.email,                       // Email
      data.cc,                          // Cartão Cidadão
      data.nascimento,                  // Data Nascimento
      data.postal,                      // Código Postal
      data.morada,                      // Morada
      data.consentimento || 'Sim',      // Consentimento RGPD
      data.quota || '0',                // Quota Mensal
      data.interesses || '',            // Interesses
      'Pendente',                       // Confirmado (email)
      'Recolhida',                      // Status Legal
      ''                                // Notas
    ];
    
    sheet.appendRow(row);
    
    return ContentService
      .createTextOutput(JSON.stringify({success: true, message: 'Assinatura registada'}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch(err) {
    return ContentService
      .createTextOutput(JSON.stringify({success: false, error: err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Para testar: abrir no browser e colar ?test=1 na URL
function doGet(e) {
  if (e && e.parameter && e.parameter.test) {
    // Teste rápido
    const sheet = SpreadsheetApp.openById('1Cva-qRD8Z3CoLSxuJR1sQqv5MnHVtpGuUgt6Exenw20');
    const data = sheet.getDataRange().getValues();
    return ContentService
      .createTextOutput(JSON.stringify({rows: data.length}))
      .setMimeType(ContentService.MimeType.JSON);
  }
  return HtmlService.createHtmlOutput('<h2>UNIR - Webhook de Assinaturas</h2><p>Este endpoint recebe dados do formulário de assinatura.</p>');
}
