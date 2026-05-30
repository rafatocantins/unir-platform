#!/usr/bin/env python3
"""
Servidor leve para receber assinaturas e escrever na Google Sheet.
Corre como processo separado.

USO:
  python3 server.py

O formulário na landing page envia POST para este servidor.
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SHEET_ID = '1Cva-qRD8Z3CoLSxuJR1sQqv5MnHVtpGuUgt6Exenw20'
TOKEN_PATH = os.path.expanduser('~/.hermes/google_token.json')
PORT = 8080

class SignatureHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except:
            self._respond(400, {'error': 'JSON invalido'})
            return

        # Validar campos
        required = ['nome', 'email', 'cc', 'nascimento', 'postal', 'morada']
        for field in required:
            if not data.get(field):
                self._respond(400, {'error': f'Campo obrigatorio: {field}'})
                return

        # Escrever na Sheet
        try:
            with open(TOKEN_PATH) as f:
                creds = Credentials.from_authorized_user_info(json.load(f))

            service = build('sheets', 'v4', credentials=creds)

            row = [[
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                data['nome'],
                data['email'],
                data['cc'],
                data['nascimento'],
                data['postal'],
                data['morada'],
                'Sim',
                str(data.get('quota', '0')),
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

        except Exception as e:
            self._respond(500, {'error': str(e)})

    def _respond(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        print(f'[SIGNATURE] {args[0]} {args[1]} {args[2]}')

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), SignatureHandler)
    print(f'Servidor de assinaturas a correr em http://0.0.0.0:{PORT}')
    print(f'A escrever na Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServidor parado')
        server.server_close()
