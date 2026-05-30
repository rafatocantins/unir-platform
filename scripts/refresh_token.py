#!/usr/bin/env python3
"""
Refresca o token OAuth do Google antes de expirar.
Corre via cron diariamente para garantir que o servidor de assinaturas
tem sempre um token válido.
"""
import json
import os
from datetime import datetime, timezone

TOKEN_PATH = os.path.expanduser('~/.hermes/google_token.json')

def refresh():
    with open(TOKEN_PATH) as f:
        token = json.load(f)

    # Verificar se está perto de expirar
    expiry = token.get('expiry')
    if expiry:
        exp_date = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        remaining = (exp_date - now).total_seconds()
        print(f"Token expira em: {exp_date}")
        print(f"Tempo restante: {remaining/3600:.1f}h")

        if remaining < 86400:  # menos de 24h
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request

            creds = Credentials.from_authorized_user_info(token)
            creds.refresh(Request())

            # Guardar token refrescado
            refreshed = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes,
                'expiry': creds.expiry.isoformat() if creds.expiry else None,
                'universe_domain': creds.universe_domain,
                'account': token.get('account', '')
            }

            with open(TOKEN_PATH, 'w') as f:
                json.dump(refreshed, f, indent=2)

            print("Token refrescado com sucesso!")
            return True
        else:
            print("Token ainda valido. Nao precisa refrescar.")
            return False
    else:
        print("Token sem data de expiracao. Assumindo valido.")
        return False

if __name__ == '__main__':
    refresh()
