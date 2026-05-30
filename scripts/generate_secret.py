#!/usr/bin/env python3
"""Gera uma SECRET_KEY segura para a UNIR Platform API.

Uso:
  python3 scripts/generate_secret.py              # só imprime a chave
  python3 scripts/generate_secret.py --write      # escreve no .env
  python3 scripts/generate_secret.py --env-file services/api/.env
"""

import secrets
import os
import sys

def generate():
    return secrets.token_hex(32)

def write_to_env(path="services/api/.env"):
    key = generate()
    env_path = os.path.join(os.path.dirname(__file__) or ".", "..", path)
    env_path = os.path.abspath(env_path)

    if not os.path.exists(env_path):
        print(f"Erro: {env_path} não encontrado")
        sys.exit(1)

    with open(env_path) as f:
        content = f.read()

    # Substituir SECRET_KEY existente ou adicionar
    if "SECRET_KEY=" in content:
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if line.startswith("SECRET_KEY="):
                new_lines.append(f"SECRET_KEY={key}")
            else:
                new_lines.append(line)
        content = "\n".join(new_lines)
    else:
        content += f"\nSECRET_KEY={key}\n"

    with open(env_path, "w") as f:
        f.write(content)

    print(f"SECRET_KEY atualizada em {env_path}")
    print(f"Chave: {key}")

if __name__ == "__main__":
    if "--write" in sys.argv:
        write_to_env()
    elif any(a.startswith("--env-file") for a in sys.argv):
        idx = sys.argv.index("--env-file")
        write_to_env(sys.argv[idx + 1])
    else:
        print(generate())
