# Sistema de Recolha de Assinaturas UNIR

## Como Correr

No teu computador (onde tenhas sessão do Google autenticada):

```bash
# 1. Iniciar o servidor
python3 ~/unir-platform/apps/web/api/signature_server.py

# 2. Servidor fica a escuta em http://localhost:8080
# O formulário da landing page envia os POST para aqui
# Se o servidor não estiver a correr, os dados ficam no localStorage do browser
```

## Dashboard da Sheet

https://docs.google.com/spreadsheets/d/1Cva-qRD8Z3CoLSxuJR1sQqv5MnHVtpGuUgt6Exenw20

- Na pasta UNIR do teu Drive
- Só tu tens acesso
- Cada linha = uma assinatura
- Coluna L (Status Legal): Recolhida → Validada → Entregue ao TC

## Exportar para o Tribunal Constitucional

Quando tiveres 7.500 assinaturas:
1. Abrir a Sheet
2. File → Download → Microsoft Excel (.xlsx)
3. Imprimir lista de subscritores
4. Submeter ao TC com: lista + estatutos + programa + denominação

## Manutenção

Para ver quantas assinaturas tens:

```bash
python3 ~/unir-platform/apps/web/api/write_signature.py --list
```
