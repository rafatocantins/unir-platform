# Instruções — Recolha de Assinaturas

## 1. Ligar o Formulário à Google Sheet

O formulário na landing page já recolhe todos os dados. Para escrever na Sheet em tempo real:

1. Abrir https://script.google.com/home
2. Criar novo projeto → colar o conteúdo de `api/AppsScript_Webhook.js`
3. Guardar (Ctrl+S) → Dar nome "UNIR Assinaturas Webhook"
4. Deploy → New deployment → Web app
   - Execute as: **Me (rafewebdev@gmail.com)**
   - Who has access: **Anyone**
5. Copiar a URL do webapp
6. Abrir `js/main.js` e colar a URL em `SHEET_API_URL`
7. Fazer commit e push → o deploy automático atualiza o site

## 2. Google Sheet

- **Link:** https://docs.google.com/spreadsheets/d/1Cva-qRD8Z3CoLSxuJR1sQqv5MnHVtpGuUgt6Exenw20
- **Pasta:** UNIR (no teu Drive)
- **Só tu tens acesso** (owner)
- Colunas: Timestamp, Nome Completo, Email, Nº CC, Data Nascimento, CP, Morada, Consentimento, Quota, Interesses, Confirmado, Status, Notas

## 3. Quando chegares às 7.500 assinaturas

Precisas de:
1. Exportar a Sheet para PDF/Excel
2. Submeter ao Tribunal Constitucional com:
   - Lista de subscritores (nome, CC, morada, assinatura)
   - Estatutos do partido
   - Programa político
   - Denominação, sigla e símbolo

## 4. Segurança

- A Sheet só tu vês (owner)
- O webhook do Apps Script só escreve (não lê)
- O ficheiro `localStorage` no browser é apenas cache local
- Para produção: pede aos utilizadores que confirmem o email antes de contar como assinatura válida
