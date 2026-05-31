"""
Servidor de assinaturas UNIR com suporte HTTPS.
Corre 24/7 na VPS.

Usa certificados SSL do Caddy ou self-signed.
O formulário no GitHub Pages (HTTPS) consegue fazer fetch para este servidor.
"""

import json
import os
import sys
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SHEET_ID = '1Cva-qRD8Z3CoLSxuJR1sQqv5MnHVtpGuUgt6Exenw20'
TOKEN_PATH = os.path.expanduser('~/.hermes/google_token.json')
PORT = 443

class SignatureHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)

            required = ['nome', 'email', 'cc', 'nascimento', 'postal', 'morada']
            for field in required:
                if not data.get(field):
                    self._respond(400, {'erro': f'Campo obrigatorio: {field}'})
                    return

            with open(TOKEN_PATH) as f:
                creds = Credentials.from_authorized_user_info(json.load(f))

            service = build('sheets', 'v4', credentials=creds)
            row = [[
                data.get('timestamp', ''),
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

            self._respond(200, {'successo': True, 'mensagem': 'Assinatura registada'})
            print(f"OK {data['nome']} <{data['email']}>")

        except Exception as e:
            print(f"ERRO: {e}")
            self._respond(500, {'erro': str(e)})

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    
    # Usar certificados do Caddy (que gerámos)
    cert_file = '/etc/caddy/certs/cert.pem'
    key_file = '/etc/caddy/certs/key.pem'
    
    server = HTTPServer(('0.0.0.0', port), SignatureHandler)
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        print(f"HTTPS server on :{port}")
    else:
        print(f"HTTP server on :{port}")
    
    server.serve_forever()
