# Pix Key Management API

Backend FastAPI para gerenciamento de chaves Pix com operações CRUD, validações de elegibilidade e auditoria estruturada.

## Arquitetura

```
src/
├── main.py              # Aplicação FastAPI
├── config.py            # Configurações com Pydantic Settings
├── db.py                # Engine SQLAlchemy e dependências
├── core/
│   ├── exceptions.py    # Exceções customizadas do domínio
│   └── logging.py       # Logging estruturado (JSON)
├── domain/
│   └── models.py        # Entidades de domínio (PixKey, enums)
├── repositories/
│   ├── abstract.py      # Abstração (Protocol) do repositório
│   └── pix_key_repository.py  # Implementação SQLAlchemy
├── services/
│   └── pix_key_service.py     # Lógica de negócio
├── schemas/
│   └── pix_key.py       # Pydantic request/response models
└── api/
    └── v1/
        └── routes/
            └── pix_keys.py    # Endpoints FastAPI
tests/
├── unit/                # Testes unitários
└── integration/         # Testes de integração
migrations/             # Alembic migrations
```

## Camadas

1. **API Layer** (`src/api/`) — HTTP handlers, validação de input via Pydantic
2. **Service Layer** (`src/services/`) — Lógica de negócio, orquestração
3. **Repository Layer** (`src/repositories/`) — Acesso a dados, abstração do ORM
4. **Domain Layer** (`src/domain/`) — Entidades, enums, regras de negócio
5. **Core** (`src/core/`) — Exceções customizadas, logging, configuração

## Quick Start

### Instalação

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Configuração

1. Copie `.env.example` para `.env`:
```bash
cp .env.example .env
```

2. Configure as variáveis de ambiente (especialmente `DATABASE_URL`):
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/pix_management_db
LOG_LEVEL=INFO
```

### Executar a Aplicação

```bash
python src/main.py
```

Ou com uvicorn direto:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse `http://localhost:8000/docs` para a documentação OpenAPI interativa.

### Testes

```bash
pytest                    # Rodar todos os testes
pytest -v                 # Verbose
pytest --cov=src          # Com cobertura
pytest -m unit            # Apenas unit tests
pytest -m integration     # Apenas integration tests
```

## API Endpoints

### Criar Chave Pix
```
POST /api/v1/pix-keys
{
  "tipo_chave": "CPF",
  "valor_chave": "12345678901",
  "conta_id": 1,
  "cliente_id": 1
}
```

Respostas:
- `201` — Chave criada com sucesso
- `400` — Validação falhou (formato inválido, formato incorreto, conta não elegível)
- `409` — Chave duplicada

### Consultar Chave
```
GET /api/v1/pix-keys/{chave_id}
```

Respostas:
- `200` — Chave encontrada
- `404` — Chave não encontrada

### Listar Chaves por Cliente
```
GET /api/v1/pix-keys/cliente/{cliente_id}?skip=0&limit=10
```

Respostas:
- `200` — Lista com paginação

### Excluir Chave
```
DELETE /api/v1/pix-keys/{chave_id}
```

Respostas:
- `204` — Deletado com sucesso
- `404` — Chave não encontrada

## Validações de Chave

| Tipo | Formato | Validação |
|------|---------|-----------|
| CPF | "12345678901" | 11 dígitos, válido conforme algoritmo CPF |
| CNPJ | "12345678000195" | 14 dígitos, válido conforme algoritmo CNPJ |
| EMAIL | "user@example.com" | Formato de email válido |
| TELEFONE | "11987654321" | 10-11 dígitos |

## Regras de Negócio

1. **Duplicidade**: Uma chave Pix só pode ser cadastrada uma vez por cliente
2. **Elegibilidade**: A conta deve estar ativa e vinculada ao cliente
3. **Status**: Chaves podem estar em status CRIADA, CONFIRMADA ou DELETADA
4. **Auditoria**: Todas as operações são registradas em logs estruturados

## Database

Usa PostgreSQL com SQLAlchemy 2.0 e Alembic para versionamento de schema.

### Migrations

```bash
# Criar migration automática
alembic revision --autogenerate -m "description"

# Aplicar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1
```

## Logging

Logs são estruturados em JSON com os seguintes campos:
- `timestamp` — ISO 8601
- `level` — INFO, WARNING, ERROR, etc.
- `name` — Logger name
- `message` — Log message

Exemplo:
```json
{
  "timestamp": "2026-04-23T10:30:00.123456Z",
  "level": "INFO",
  "name": "src.services.pix_key_service",
  "message": "Chave Pix criada com sucesso",
  "cliente_id": 1,
  "chave_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Testing Strategy

### Unit Tests
Testam lógica de validação e regras de negócio em isolamento.

```python
# Exemplo: test_validar_cpf_invalido
```

### Integration Tests
Testam fluxo completo: API → Service → Repository → DB.

```python
# Exemplo: test_criar_chave_sucesso
```

## Próximas Fases

- [ ] Phase 2: Domain entities e enums
- [ ] Phase 3: SQLAlchemy models e Alembic migrations
- [ ] Phase 4: Repository e Service layer
- [ ] Phase 5: API routes
- [ ] Phase 6: Testes unitários e integração
- [ ] Phase 7: Docker, documentação completa

## Contribuindo

1. Seguir Clean Architecture e SOLID principles
2. Centralizar validações na camada de serviço
3. Adicionar testes antes de integrar (TDD quando possível)
4. Usar type hints em todo o código Python
5. Manter cobertura de testes acima de 70%

## Licença

MIT
