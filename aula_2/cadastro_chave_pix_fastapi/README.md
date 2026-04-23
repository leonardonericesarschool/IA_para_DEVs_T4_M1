# Cadastro de Chave Pix (API REST - FastAPI)

API REST para **cadastro de chaves Pix** com **FastAPI + SQLite**, validação automática com **Pydantic**, versionamento em `/api/v1`, paginação, filtros e documentação **Swagger UI/OpenAPI** nativa.

## 🎯 Características

- ✅ **Framework**: FastAPI (moderno, rápido, com Swagger/OpenAPI nativo)
- ✅ **Banco de Dados**: SQLite com SQLAlchemy ORM 2.0+
- ✅ **Validação**: Pydantic com validadores customizados
- ✅ **Versionamento**: URLs versionadas em `/api/v1`
- ✅ **Paginação**: Suporte a `?page=1&limit=10`
- ✅ **Tratamento de Erros**: Códigos HTTP apropriados (200, 201, 400, 404, 500) com mensagens em português
- ✅ **Documentação**: Swagger UI em `/docs` e ReDoc em `/redoc`
- ✅ **Código**: camelCase em português, estrutura modular com factory pattern

## 📋 Requisitos

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) instalado

## 🚀 Instalação

### 1. Criar e ativar ambiente virtual

```bash
cd cadastro_chave_pix_fastapi
uv venv .venv-cadastro_chave_pix_fastapi
source .venv-cadastro_chave_pix_fastapi/bin/activate  # Linux/Mac
# ou
.venv-cadastro_chave_pix_fastapi\Scripts\activate  # Windows
```

### 2. Instalar dependências

```bash
uv pip install -r requirements.txt
```

## ▶️ Executar

### Modo Produção (sem reload)

```bash
python main.py
```

Por padrão o servidor sobe em `http://127.0.0.1:8000`.

### Modo Desenvolvimento (com hot-reload)

Para recarregar a aplicação automaticamente ao fazer mudanças no código:

```bash
uvicorn main:app --reload
```

Ou customizando host e porta:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## 📚 Documentação (Swagger UI / OpenAPI)

Acesse a documentação interativa em:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔌 Endpoints

### Base URL
```
http://127.0.0.1:8000/api/v1
```

### 1. Criar Chave Pix

**POST** `/chaves-pix`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chaves-pix \
  -H "Content-Type: application/json" \
  -d '{
    "tipoChave": "CPF",
    "valorChave": "12345678901",
    "descricao": "Chave pessoal"
  }'
```

**Respostas**:
- `201 Created`: Chave criada com sucesso
- `400 Bad Request`: Validação falhou ou chave duplicada
- `500 Internal Server Error`: Erro no servidor

### 2. Listar Chaves Pix (com paginação)

**GET** `/chaves-pix?page=1&limit=10`

```bash
curl http://127.0.0.1:8000/api/v1/chaves-pix
curl http://127.0.0.1:8000/api/v1/chaves-pix?page=2&limit=50
```

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "tipoChave": "CPF",
      "valorChave": "12345678901",
      "descricao": "Chave pessoal",
      "criadoEm": "2026-04-15T10:30:00Z",
      "atualizadoEm": "2026-04-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

### 3. Obter Chave Pix por ID

**GET** `/chaves-pix/{id}`

```bash
curl http://127.0.0.1:8000/api/v1/chaves-pix/1
```

**Respostas**:
- `200 OK`: Retorna a chave
- `404 Not Found`: Chave não encontrada

### 4. Atualizar Chave Pix

**PUT** `/chaves-pix/{id}`

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/chaves-pix/1 \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Nova descrição"
  }'
```

**Response**: Chave atualizada (200 OK) ou não encontrada (404)

### 5. Deletar Chave Pix

**DELETE** `/chaves-pix/{id}`

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/chaves-pix/1
```

**Respostas**:
- `204 No Content`: Deletada com sucesso
- `404 Not Found`: Chave não encontrada

## 🏥 Health Check

**GET** `/health`

```bash
curl http://127.0.0.1:8000/health
```

```json
{
  "status": "ok",
  "aplicacao": "cadastro_chave_pix"
}
```

## 📁 Estrutura do Projeto

```
cadastro_chave_pix_fastapi/
├── main.py                          # Entry point - inicia a aplicação
├── requirements.txt                 # Dependências (FastAPI, SQLAlchemy, etc.)
├── LICENSE                          # Licença MIT
├── README.md                        # Este arquivo
├── .gitignore                       # Git ignore patterns
├── cadastro_chave_pix.db           # Banco SQLite (criado automaticamente)
├── .venv-cadastro_chave_pix_fastapi/  # Ambiente virtual (criado por uv venv)
└── app/
    ├── __init__.py                  # Factory pattern: criarApp()
    ├── config.py                    # Configurações: host, port, database URL
    ├── db.py                        # SQLAlchemy: Engine, SessionLocal, context managers
    ├── models.py                    # Modelos ORM: ChavePix
    ├── schemas.py                   # Schemas Pydantic: ChavePixCriarRequest, Response, etc.
    ├── errors.py                    # Tratamento de erros: ErroApi, dataclass
    ├── routes/
    │   ├── __init__.py
    │   └── chavesPix.py            # Endpoints CRUD: POST, GET, PUT, DELETE
    └── test_main.py                # Testes pytest (opcional)
```

## 🛠️ Configuração via Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

```env
NOME_APP=cadastro_chave_pix
DEBUG=True
DATABASE_URL=sqlite:///cadastro_chave_pix.db
HOST=127.0.0.1
PORT=8000
```

## ✅ Testes

Para rodar testes:

```bash
source .venv-cadastro_chave_pix_fastapi/bin/activate
pytest app/test_main.py -v
```

## 📝 Padrões de Código

- **Nomes**: camelCase em Português (ex: `tipoChave`, `validarValorChave()`)
- **Classes**: PascalCase (ex: `ChavePix`, `ErroApi`)
- **Enums**: MAIÚSCULAS (ex: `TipoChave.CPF`)
- **Funções**: verbo + camelCase (ex: `serializarChavePix()`, `criarChavePix()`)

## 🔒 Validações Implementadas

| Campo | Validação |
|-------|-----------|
| `tipoChave` | Enum: CPF, CNPJ, EMAIL, TELEFONE |
| `valorChave` | String, 1-100 caracteres |
| `descricao` | String opcional, máx 255 caracteres |
| **Constraint Única** | (tipoChave, valorChave) não podem ser duplicadas |

## 🐛 Tratamento de Erros

Todos os erros retornam JSON com estrutura:

```json
{
  "mensagem": "Descrição do erro em português",
  "detalhes": {
    "campo_adicional": "valor"
  }
}
```

### Códigos HTTP

- `200 OK`: Sucesso (GET, PUT)
- `201 Created`: Recurso criado (POST)
- `204 No Content`: Deletado com sucesso (DELETE)
- `400 Bad Request`: Validação falhou, chave duplicada
- `404 Not Found`: Recurso não encontrado
- `422 Unprocessable Entity`: Erro de validação Pydantic
- `500 Internal Server Error`: Erro no servidor

## 🚦 Próximos Passos (Optionais)

1. **Autenticação**: Adicionar JWT com FastAPI Security
2. **Validação de Domínio**: Validar formatos específicos (ex: email válido, CPF válido)
3. **Testes Completos**: Expandir suite de testes pytest
4. **Docker**: Containerizar a aplicação
5. **CORS**: Configurar CORS se necessário

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido com ❤️ em FastAPI**
