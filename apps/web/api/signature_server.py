"""
Servidor UNIR — assinaturas e candidaturas.
Corre 24/7 na VPS, recebe POST e escreve nas respetivas Google Sheets.

Endpoints:
  POST /public/sign       — assinatura para fundar o partido (Sheet principal)
  POST /public/candidatar — candidatura para integrar o partido (Sheet secundária)

Uso em produção:
  python3 /root/unir-platform/apps/web/api/signature_server.py [porta]

Uso com systemd (auto-start):
  systemctl --user enable unir-signatures
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SHEET_ASSINATURAS = '1Cva-qRD8Z3CoLSxuJR1sQqv5MnHVtpGuUgt6Exenw20'
SHEET_CANDIDATURAS = '1EeLxMGSZ5WbMYC_yX6tUILAznqlydpfJcugRdULUgdc'
TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.json')
PORT = 8080


def get_sheets_service():
    """Get authenticated Google Sheets service with token refresh."""
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Token not found at {TOKEN_PATH}")
    with open(TOKEN_PATH) as f:
        creds = Credentials.from_authorized_user_info(json.load(f))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)


class UnirHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        path = self.path.rstrip('/')

        if path == '/public/sign':
            self._handle_sign()
        elif path == '/public/candidatar':
            self._handle_candidatura()
        else:
            self._respond(404, {'erro': 'Endpoint nao encontrado'})

    def _handle_sign(self):
        """Recebe assinatura para fundar o partido."""
        try:
            data = self._parse_body()
            required = ['nome', 'email', 'cc', 'nascimento', 'postal', 'morada']
            for field in required:
                if not data.get(field):
                    self._respond(400, {'success': False, 'erro': f'Campo obrigatorio: {field}'})
                    return

            service = get_sheets_service()
            row = [[
                data.get('timestamp', ''),
                data['nome'],
                data['email'],
                data['cc'],
                data['nascimento'],
                data['postal'],
                data['morada'],
                'Sim',  # consentimento
                'Recolhida',  # estado
                ''
            ]]

            service.spreadsheets().values().append(
                spreadsheetId=SHEET_ASSINATURAS,
                range='A2:J',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': row}
            ).execute()

            self._respond(200, {'success': True, 'mensagem': 'Assinatura registada'})
            print(f"ASSINATURA OK: {data['nome']} <{data['email']}>")

        except Exception as e:
            print(f"ERRO ASSINATURA: {e}")
            self._respond(500, {'success': False, 'erro': str(e)})

    def _handle_candidatura(self):
        """Recebe candidatura para integrar o partido."""
        try:
            data = self._parse_body()
            required = ['email', 'nome', 'area_formacao', 'motivacao']
            for field in required:
                if not data.get(field):
                    self._respond(400, {'success': False, 'erro': f'Campo obrigatorio: {field}'})
                    return

            service = get_sheets_service()
            row = [[
                data.get('timestamp', ''),
                data['nome'],
                data['email'],
                data.get('area_formacao', ''),
                data.get('areas_interesse', ''),
                data['motivacao'],
                data.get('linkedin', ''),
                'Pendente'  # estado: Pendente | Em analise | Aceite | Recusada
            ]]

            service.spreadsheets().values().append(
                spreadsheetId=SHEET_CANDIDATURAS,
                range='A2:H',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': row}
            ).execute()

            self._respond(200, {'success': True, 'mensagem': 'Candidatura recebida'})
            print(f"CANDIDATURA OK: {data['nome']} <{data['email']}>")

        except Exception as e:
            print(f"ERRO CANDIDATURA: {e}")
            self._respond(500, {'success': False, 'erro': str(e)})

    def _parse_body(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        return json.loads(body)

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        pass  # silencioso


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    server = HTTPServer(('0.0.0.0', port), UnirHandler)
    print(f'UNIR server running on :{port}')
    print(f'  POST /public/sign       -> Sheet assinaturas')
    print(f'  POST /public/candidatar -> Sheet candidaturas')
    server.serve_forever()
