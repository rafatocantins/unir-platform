"""
Servidor local que recebe assinaturas e escreve na Google Sheet UNIR.
Corre em background e é chamado pelo formulário da landing page.

Uso: python3 ~/unir-platform/apps/web/api/signature_server.py &

O servidor fica a escuta em http://localhost:8080
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SHEET_ID = '1Cva-qRD8Z3CoLSxuJR1sQqv5MnHVtpGuUgt6Exenw20'
TOKEN_PATH = os.path.expanduser('~/.hermes/google_token.json')

class SignatureHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)

            # Validar
            required = ['nome', 'email', 'cc', 'nascimento', 'postal', 'morada']
            for field in required:
                if not data.get(field):
                    self._respond(400, {'error': f'Campo obrigatorio: {field}'})
                    return

            # Escrever na Sheet
            with open(TOKEN_PATH) as f:
                creds = Credentials.from_authorized_user_info(json.load(f))

            service = build('sheets', 'v4', credentials=creds)

            row = [[
                self.date_time_string(),
                data['nome'],
                data['email'],
                data['cc'],
                data['nascimento'],
                data['postal'],
                data['morada'],
                data.get('consentimento', 'Sim'),
                data.get('quota', '0'),
                data.get('interesses', ''),
                'Pendente',
                'Recolhida',
                ''
            ]]

            service.spreadsheets().values().append(
                spreadsheetId=SHEET_ID,
                range='A2:M',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': row}
            ).execute()

            self._respond(200, {'success': True, 'message': 'Assinatura registada'})
            print(f"✅ Assinatura: {data['nome']} <{data['email']}>")

        except Exception as e:
            print(f"❌ Erro: {e}")
            self._respond(500, {'error': str(e)})

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = HTTPServer(('0.0.0.0', port), SignatureHandler)
    print(f'🚀 Servidor de assinaturas UNIR a escuta em http://localhost:{port}')
    print(f'📊 Sheet ID: {SHEET_ID}')
    server.serve_forever()
