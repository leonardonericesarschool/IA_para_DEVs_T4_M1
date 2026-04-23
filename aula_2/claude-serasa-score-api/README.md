# 📊 Serasa Score API

API para consulta de score de crédito no SERASA, construída com **FastAPI**, seguindo **Clean Architecture** e boas práticas de segurança para dados sensíveis (CPF/PII).

---

## 🏗️ Arquitetura

```
src/
├── api/v1/routes/      # Controllers HTTP — só roteamento, sem lógica
├── core/               # Config, exceptions, logging, dependencies
├── domain/             # Entidades, enums, value objects
├── schemas/            # Pydantic models (request/response)
├── services/           # Use cases / application logic
├── repositories/       # Data access layer (abstração de persistência)
└── infrastructure/
    ├── cache/          # Redis — TTL obrigatório em todas as chaves
    └── http/           # Cliente HTTP para SERASA API externa
```

## 🚀 Quickstart

```bash
# 1. Clone e entre no projeto
cd serasa-score-api

# 2. Copie o .env
cp .env.example .env

# 3. Suba os serviços
docker-compose up -d

# 4. Acesse a documentação
open http://localhost:8000/docs
```

## 🔐 Segurança

- CPF é **mascarado nos logs** (nunca `123.456.789-00`, sempre `***.***.789-00`)
- Rate limiting por IP e por token de API
- JWT com expiração curta (15 min) + refresh token
- Dados em cache no Redis com TTL de 24h
- Audit log de todas as consultas (sem PII)

## 🧪 Testes

```bash
pytest tests/ --cov=src --cov-report=html --cov-fail-under=80
```

## 📋 Variáveis de Ambiente

| Variável | Descrição | Obrigatório |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `REDIS_URL` | Redis connection string | ✅ |
| `SERASA_API_URL` | URL base da API SERASA | ✅ |
| `SERASA_API_KEY` | Chave de API SERASA | ✅ |
| `SECRET_KEY` | Chave JWT (min 32 chars) | ✅ |
| `SERASA_TIMEOUT_SECONDS` | Timeout para chamadas SERASA | ❌ (default: 10) |
| `SCORE_CACHE_TTL_SECONDS` | TTL do cache de score | ❌ (default: 86400) |
