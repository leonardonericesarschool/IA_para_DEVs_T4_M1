# Flask Phone API

API REST para validação de números de telefone brasileiros.

## Endpoints

- `GET /phone`: Retorna informações sobre a API.
- `POST /phone`: Recebe um JSON com o campo `phone` e retorna se o número é válido.

### Exemplo de requisição POST
```json
{
  "phone": "+55 11 91234-5678"
}
```

## Como executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute a aplicação:
   ```bash
   python app/main.py
   ```

## Licença
MIT
