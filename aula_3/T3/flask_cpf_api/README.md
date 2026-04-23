# Flask CPF Validation API

Esta API REST valida números de CPF brasileiros.

## Endpoints
- `GET /cpf/<cpf>`: Valida um CPF informado na URL.
- `POST /cpf`: Valida um CPF enviado no corpo da requisição (JSON).

## Como executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o servidor:
   ```bash
   python app/main.py
   ```

## Licença
MIT
