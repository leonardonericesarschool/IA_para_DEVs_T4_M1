# Cadastro de Chave Pix (API REST)

API REST para **cadastro de chaves Pix** com **Flask + SQLite**, validação com **Pydantic**, versionamento em `/api/v1`, paginação/filtros e documentação Swagger/OpenAPI.

## Requisitos

- Python (mais atual disponível no seu ambiente)
- [`uv`](https://docs.astral.sh/uv/) instalado

## Instalação

Crie e use um ambiente virtual com o **nome da aplicação**:

```bash
cd cadastro_chave_pix
uv venv .venv-cadastro_chave_pix
source .venv-cadastro_chave_pix/bin/activate
uv pip install -r requirements.txt
```

## Executar

```bash
python3 main.py
```

Por padrão o servidor sobe em `http://127.0.0.1:5000`.

## Documentação (Swagger UI / OpenAPI)

Após subir a API, acesse a documentação interativa em:

- Swagger UI: `http://127.0.0.1:5000/openapi/`
- OpenAPI JSON: `http://127.0.0.1:5000/openapi/openapi.json`

Observação: a Swagger UI é fornecida pelo extra `flask-openapi3[swagger]` (já incluído no `requirements.txt`).

## Endpoints (v1)

Base: `/api/v1`

- `POST /api/v1/chaves-pix`
- `GET /api/v1/chaves-pix?page=1&limit=50&tipoChave=cpf&valorChave=...`
- `GET /api/v1/chaves-pix/{id}`
- `PUT /api/v1/chaves-pix/{id}`
- `DELETE /api/v1/chaves-pix/{id}`

## Exemplos (curl)

### Criar chave (CPF)

```bash
curl -X POST "http://127.0.0.1:5000/api/v1/chaves-pix" \
  -H "Content-Type: application/json" \
  -d '{
    "tipoChave": "cpf",
    "valorChave": "12345678901",
    "descricao": "Chave do João"
  }'
```

### Listar com paginação

```bash
curl "http://127.0.0.1:5000/api/v1/chaves-pix?page=1&limit=10"
```

### Filtrar por tipo

```bash
curl "http://127.0.0.1:5000/api/v1/chaves-pix?tipoChave=email"
```

### Buscar por id

```bash
curl "http://127.0.0.1:5000/api/v1/chaves-pix/1"
```

## Códigos de status e erros

- `200 OK`: sucesso
- `201 Created`: criado com sucesso
- `400 Bad Request`: requisição inválida/validação
- `404 Not Found`: recurso não encontrado
- `500 Internal Server Error`: erro inesperado

As mensagens e respostas são retornadas em **Português**.

