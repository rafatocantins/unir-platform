#!/usr/bin/env python3
"""Escreve assinatura na Google Sheet UNIR_Assinaturas_Fundacao.
Uso: python3 write_signature.py --nome "Rafael Cabrita" --email "rafael@email.pt" --cc "12345678" --nascimento "1990-01-01" --cp "3000-000" --morada "Rua X" --quota 5 --interesses "Saude,Habitacao"
"""

import json, os, sys, argparse
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SHEET_ID = '1Cva-qRD8Z3CoLSxuJR1sQqv5MnHVtpGuUgt6Exenw20'
TOKEN_PATH = os.path.expanduser('~/.hermes/google_token.json')
RANGE = 'A2:M'  # Append após o cabeçalho

def get_sheets_service():
    with open(TOKEN_PATH) as f:
        creds = Credentials.from_authorized_user_info(json.load(f))
    return build('sheets', 'v4', credentials=creds)

def write_signature(nome, email, cc, nascimento, cp, morada, quota, interesses):
    service = get_sheets_service()

    row = [[
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Timestamp
        nome,                                           # Nome Completo
        email,                                          # Email
        cc,                                             # Número Cartão Cidadão
        nascimento,                                     # Data Nascimento
        cp,                                             # Código Postal
        morada,                                         # Morada
        'Sim',                                          # Consentimento RGPD
        str(quota),                                     # Quota Mensal
        interesses,                                     # Interesses
        'Pendente',                                     # Confirmado (email)
        'Recolhida',                                    # Status Legal
        ''                                              # Notas
    ]]

    result = service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=RANGE,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': row}
    ).execute()

    return result.get('updates', {}).get('updatedRows', 0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nome', required=True)
    parser.add_argument('--email', required=True)
    parser.add_argument('--cc', required=True)
    parser.add_argument('--nascimento', required=True)
    parser.add_argument('--cp', required=True)
    parser.add_argument('--morada', required=True)
    parser.add_argument('--quota', default='0')
    parser.add_argument('--interesses', default='')
    args = parser.parse_args()

    rows = write_signature(args.nome, args.email, args.cc, args.nascimento, args.cp, args.morada, args.quota, args.interesses)
    print(f'OK: {rows} linha(s) escrita(s)')
