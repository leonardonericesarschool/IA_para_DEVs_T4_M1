# Especificação Técnica: Desenvolvimento de Sistemas Web com Python

## 1. Introdução

Este documento estabelece os padrões, boas práticas e diretrizes técnicas para o desenvolvimento de sistemas web utilizando Python como linguagem principal. A especificação abrange arquitetura, design patterns, qualidade de código, segurança, performance e implementação de soluções escaláveis e mantíveis.

---

## 2. Ecossistema Python para Web

### 2.1 Frameworks Principais

#### **Django**
- **Uso**: Aplicações web completas, backends complexos, MVT (Model-View-Template)
- **Vantagens**: ORM robusto, admin integrado, segurança built-in, comunidade madura
- **Quando usar**: Projetos de médio a grande porte, monolíticos
- **Versão recomendada**: 4.2 LTS ou superior

#### **FastAPI**
- **Uso**: APIs REST/GraphQL, microsserviços, backends assíncronos
- **Vantagens**: Performance alta, validação automática (Pydantic), documentação automática, async/await nativo
- **Quando usar**: APIs modernas, microserviços, requisitos de alta performance
- **Versão recomendada**: 0.100+ ou superior

#### **Flask**
- **Uso**: Aplicações leves, prototipagem rápida, APIs simples
- **Vantagens**: Minimalista, flexível, curva de aprendizado suave
- **Quando usar**: Projetos pequenos, MVPs, quando máximo controle é necessário
- **Versão recomendada**: 2.3+

#### **Starlette**
- **Uso**: Framework ASGI de baixo nível, base para FastAPI
- **Vantagens**: Minimalista, altamente performático, suporte nativo a async
- **Quando usar**: Quando precisa-se de flexibilidade do FastAPI mas com menos abstrações

### 2.2 Tecnologias Complementares

| Categoria | Tecnologia | Descrição |
|-----------|-----------|-----------|
| **ORM** | SQLAlchemy | ORM agnóstico de DB, suporta async |
| **ORM** | Tortoise ORM | ORM async-first para FastAPI |
| **Validação** | Pydantic | Validação de dados, serialização |
| **Testing** | Pytest | Framework de testes, fixtures poderosas |
| **Async** | AsyncIO | Concorrência nativa em Python |
| **Queue** | Celery | Tasks assincronamente, background jobs |
| **Cache** | Redis | Cache distribuído, sessions, pub/sub |
| **Busca** | Elasticsearch | Busca full-text, análise de dados |
| **API** | GraphQL-core | Implementação de GraphQL |

---

## 3. Arquitetura e Design Patterns

### 3.1 Padrão Arquitetural: Clean Architecture / Hexagonal

```
projeto/
├── domain/                  # Entidades e lógica de negócio
│   ├── models/
│   ├── repositories/
│   └── services/
├── application/             # Casos de uso e orquestração
│   ├── use_cases/
│   ├── dto/
│   └── mappers/
├── infrastructure/          # Implementações externas
│   ├── persistence/
│   ├── http/
│   └── external_services/
├── presentation/            # Controllers, routes, middleware
│   ├── api/
│   ├── web/
│   └── middleware/
└── config/                  # Configurações
```

### 3.2 Design Patterns Recomendados

#### **Repository Pattern**
```python
# Abstração de acesso a dados
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User:
        pass
    
    @abstractmethod
    async def save(self, user: User) -> User:
        pass

class SQLAlchemyUserRepository(UserRepository):
    async def get_by_id(self, user_id: int) -> User:
        # Implementação específica do banco
        pass
```

#### **Dependency Injection**
```python
# Facilita testes e desacoplamento
from fastapi import Depends

def get_user_service(repo: UserRepository = Depends()) -> UserService:
    return UserService(repo)

@app.get("/users/{user_id}")
async def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    return await service.get_user(user_id)
```

#### **Factory Pattern**
```python
# Criação dinâmica de objetos
class DatabaseFactory:
    @staticmethod
    def create_connection(db_type: str) -> Database:
        if db_type == "postgres":
            return PostgresConnection()
        elif db_type == "mysql":
            return MysqlConnection()
```

#### **Strategy Pattern**
```python
# Algoritmos intercambiáveis
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    async def process(self, amount: float) -> str:
        pass

class CreditCardPayment(PaymentStrategy):
    async def process(self, amount: float) -> str:
        # Implementação específica
        pass

class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    async def pay(self, amount: float) -> str:
        return await self.strategy.process(amount)
```

#### **Observer Pattern**
```python
# Comunicação event-driven
from typing import Callable, List

class EventBus:
    def __init__(self):
        self._subscribers: dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    async def publish(self, event_type: str, data: dict):
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                await handler(data)
```

#### **Decorator Pattern**
```python
# Adicionar comportamentos dinamicamente
from functools import wraps

def cache_result(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Verificar cache
        result = await func(*args, **kwargs)
        # Armazenar em cache
        return result
    return wrapper

@cache_result
async def get_expensive_data(id: int):
    pass
```

### 3.3 Estrutura de Projeto FastAPI (Recomendada)

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routers
from app.infrastructure.database import lifespan

app = FastAPI(
    title="API Specification",
    version="1.0.0",
    lifespan=lifespan
)

# Middlewares
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Routes
for router in routers:
    app.include_router(router)

# app/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from app.application.use_cases import UserUseCase
from app.presentation.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    use_case: UserUseCase = Depends()
):
    user = await use_case.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## 4. Boas Práticas de Engenharia de Software

### 4.1 Princípios SOLID

#### **S - Single Responsibility Principle**
```python
# ✅ BOM: Cada classe tem uma responsabilidade
class UserRepository:
    async def get_by_id(self, user_id: int) -> User:
        pass

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    async def get_user_with_posts(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        return user

# ❌ RUIM: Mistura responsabilidades
class UserManager:
    async def get_user(self, user_id: int):
        # Acesso a banco
        # Validações
        # Envio de email
        # Logging
        pass
```

#### **O - Open/Closed Principle**
```python
# ✅ BOM: Aberto para extensão, fechado para modificação
class NotificationService:
    def __init__(self, provider: NotificationProvider):
        self.provider = provider
    
    async def notify(self, message: str):
        await self.provider.send(message)

class EmailProvider(NotificationProvider):
    async def send(self, message: str):
        pass

class SMSProvider(NotificationProvider):
    async def send(self, message: str):
        pass
```

#### **L - Liskov Substitution Principle**
```python
# ✅ BOM: Subclasses podem substituir a classe-mãe
class Vehicle(ABC):
    @abstractmethod
    async def start(self):
        pass

class Car(Vehicle):
    async def start(self):
        return "Car started"

# Funcionará para qualquer Vehicle
async def start_vehicle(vehicle: Vehicle):
    return await vehicle.start()
```

#### **I - Interface Segregation Principle**
```python
# ✅ BOM: Interfaces pequenas e específicas
class Readable(ABC):
    @abstractmethod
    async def read(self) -> str:
        pass

class Writable(ABC):
    @abstractmethod
    async def write(self, data: str) -> None:
        pass

class Logger(Readable, Writable):
    async def read(self) -> str:
        pass
    
    async def write(self, data: str) -> None:
        pass

# ❌ RUIM: Interface grande
class Repository(ABC):
    async def create(self): pass
    async def read(self): pass
    async def update(self): pass
    async def delete(self): pass
    async def search(self): pass
    async def export(self): pass
    async def import_data(self): pass
```

#### **D - Dependency Inversion Principle**
```python
# ✅ BOM: Depender de abstrações, não de implementações concretas
class UserService:
    def __init__(self, repository: UserRepository):  # Abstração
        self.repository = repository

# ❌ RUIM: Dependência direta de implementação
class UserService:
    def __init__(self):
        self.repository = PostgresUserRepository()  # Concreção
```

### 4.2 DRY (Don't Repeat Yourself)

```python
# ✅ BOM: Código reutilizável
async def get_paginated_results(
    query,
    skip: int = 0,
    limit: int = 10
):
    return await query.offset(skip).limit(limit).all()

@router.get("/users")
async def list_users(skip: int = 0, limit: int = 10):
    return await get_paginated_results(User.select(), skip, limit)

@router.get("/posts")
async def list_posts(skip: int = 0, limit: int = 10):
    return await get_paginated_results(Post.select(), skip, limit)
```

### 4.3 KISS (Keep It Simple, Stupid)

```python
# ✅ BOM: Simples e legível
def calculate_discount(price: float, discount_percent: float) -> float:
    return price * (1 - discount_percent / 100)

# ❌ RUIM: Overcomplicated
def calculate_discount(p: float, d: float, t: bool = False) -> float:
    return p * (1 - (d * (1.1 if t else 1)) / 100) if p > 0 else 0
```

### 4.4 Code Reviews

```yaml
Checklist de Code Review:
- [ ] Código segue os padrões do projeto
- [ ] Testes unitários inclusós e passando
- [ ] Documentação atualizada
- [ ] Sem código duplicado
- [ ] Performance adequada
- [ ] Tratamento de erros apropriado
- [ ] Logging suficiente
- [ ] Segurança validada
```

---

## 5. Padrões de Segurança

### 5.1 Autenticação e Autorização

```python
# FastAPI com JWT
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)
        return username
    except JWTError:
        raise HTTPException(status_code=401)

def create_access_token(username: str, expires_delta: timedelta = None):
    if expires_delta is None:
        expires_delta = timedelta(hours=24)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/protected")
async def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello {current_user}"}
```

### 5.2 Validação de Entrada

```python
from pydantic import BaseModel, Field, validator, conint
from typing import Optional

class UserCreate(BaseModel):
    email: str = Field(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(..., min_length=8)
    age: conint(ge=18, le=120)
    name: str = Field(..., min_length=1, max_length=100)
    
    @validator('email')
    def email_must_be_unique(cls, v):
        # Verificar banco de dados
        if user_exists(v):
            raise ValueError('Email already registered')
        return v.lower()

# Uso
user_data = UserCreate(
    email="user@example.com",
    password="secure_password123",
    age=25,
    name="John Doe"
)
```

### 5.3 Proteção contra Ataques Comuns

```python
# CSRF Protection
from fastapi.middleware.csrf import CsrfProtectMiddleware

# SQL Injection Prevention - SQLAlchemy com parametrização
query = select(User).where(User.email == email)  # Parametrizado automaticamente

# XSS Prevention - Sanitização de output
from markupsafe import escape
safe_content = escape(user_input)

# Rate Limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/users")
@limiter.limit("100/minute")
async def get_users(request: Request):
    pass

# CORS Configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trusted-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Environment Variables para Secrets
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
```

---

## 6. Qualidade de Código

### 6.1 Testes

#### **Testes Unitários**
```python
# test_user_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.application.user_service import UserService

@pytest.fixture
def mock_repository():
    return AsyncMock()

@pytest.fixture
def user_service(mock_repository):
    return UserService(mock_repository)

@pytest.mark.asyncio
async def test_get_user_success(user_service, mock_repository):
    # Arrange
    expected_user = {"id": 1, "name": "John"}
    mock_repository.get_by_id.return_value = expected_user
    
    # Act
    result = await user_service.get_by_id(1)
    
    # Assert
    assert result == expected_user
    mock_repository.get_by_id.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_get_user_not_found(user_service, mock_repository):
    # Arrange
    mock_repository.get_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(UserNotFoundException):
        await user_service.get_by_id(999)
```

#### **Testes de Integração**
```python
# test_user_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_user_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/1")
        assert response.status_code == 200
        assert response.json()["id"] == 1

@pytest.mark.asyncio
async def test_create_user_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/users",
            json={"name": "John", "email": "john@example.com"}
        )
        assert response.status_code == 201
        assert "id" in response.json()
```

#### **Cobertura de Testes**
```bash
# pytest com cobertura
pytest --cov=app --cov-report=html

# Coverage mínimo de 80%
# pytest.ini
[pytest]
addopts = --cov=app --cov-fail-under=80
```

### 6.2 Linting e Formatação

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88']

  - repo: https://github.com/PyCQA/pylint
    rev: 2.17.1
    hooks:
      - id: pylint
```

```python
# pyproject.toml
[tool.black]
line-length = 88

[tool.isort]
profile = "black"
line_length = 88

[tool.pylint]
max-line-length = 88
disable = "C0111"  # missing-docstring
```

### 6.3 Type Hints

```python
# ✅ BOM: Type hints completos
from typing import List, Optional, Dict, Tuple, Union
from typing import Callable

async def process_users(
    user_ids: List[int],
    filters: Optional[Dict[str, str]] = None
) -> Dict[int, dict]:
    """
    Processa usuários por IDs.
    
    Args:
        user_ids: Lista de IDs de usuários
        filters: Filtros opcionais
    
    Returns:
        Dicionário com resultado do processamento
    """
    pass

# Union Types
def get_user(identifier: Union[int, str]) -> Optional[User]:
    pass

# Callable
def execute_callback(callback: Callable[[str], int]) -> None:
    result = callback("test")
    pass

# Generics
from typing import TypeVar, Generic

T = TypeVar('T')

class Repository(Generic[T]):
    async def get(self, id: int) -> Optional[T]:
        pass
```

### 6.4 Documentação

```python
# Docstrings com formato Google Style
def calculate_total_price(
    items: List[Item],
    discount_percent: float = 0
) -> float:
    """
    Calcula o preço total dos itens com desconto.
    
    Args:
        items: Lista de itens com preço
        discount_percent: Percentual de desconto (padrão: 0)
    
    Returns:
        Preço total com desconto aplicado
    
    Raises:
        ValueError: Se discount_percent for negativo
    
    Examples:
        >>> items = [Item(price=100), Item(price=200)]
        >>> calculate_total_price(items, 10)
        270.0
    """
    if discount_percent < 0:
        raise ValueError("Discount cannot be negative")
    
    total = sum(item.price for item in items)
    return total * (1 - discount_percent / 100)

# Comentários úteis (não óbvios)
# ✅ BOM
# Aplicar backoff exponencial para evitar rate limiting
await asyncio.sleep(2 ** attempt)

# ❌ RUIM
# Incrementar contador
counter += 1
```

---

## 7. Performance e Otimização

### 7.1 Async/Await

```python
# ✅ BOM: Operações concorrentes
import asyncio
from httpx import AsyncClient

async def fetch_multiple_users(user_ids: List[int]):
    async with AsyncClient() as client:
        tasks = [
            client.get(f"/api/users/{uid}")
            for uid in user_ids
        ]
        responses = await asyncio.gather(*tasks)
        return responses

# ❌ RUIM: Operações sequenciais (bloqueante)
def fetch_multiple_users(user_ids: List[int]):
    results = []
    for uid in user_ids:
        response = requests.get(f"/api/users/{uid}")
        results.append(response.json())
    return results
```

### 7.2 Caching

```python
# Cache em memória com TTL
from cachetools import TTLCache
from functools import wraps

cache = TTLCache(maxsize=100, ttl=300)  # 5 minutos

def cache_result(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        key = (func.__name__, args, tuple(kwargs.items()))
        if key in cache:
            return cache[key]
        result = await func(*args, **kwargs)
        cache[key] = result
        return result
    return wrapper

@cache_result
async def get_user(user_id: int):
    return await db.get_user(user_id)

# Redis para cache distribuído
import aioredis
from aioredis import Redis

async def get_user_cached(user_id: int, redis: Redis):
    cache_key = f"user:{user_id}"
    
    # Tentar cache
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Carregar do banco
    user = await db.get_user(user_id)
    
    # Armazenar em cache por 1 hora
    await redis.setex(cache_key, 3600, json.dumps(user))
    
    return user
```

### 7.3 Database Optimization

```python
# ✅ BOM: Eager loading para evitar N+1 queries
from sqlalchemy.orm import joinedload

async def get_users_with_posts():
    return await db.query(User).options(
        joinedload(User.posts)
    ).all()

# Pagination
async def get_paginated_users(skip: int = 0, limit: int = 10):
    return await db.query(User).offset(skip).limit(limit).all()

# Índices no banco de dados
# alembic/versions/create_user_email_index.py
def upgrade():
    op.create_index('ix_user_email', 'user', ['email'])

def downgrade():
    op.drop_index('ix_user_email', 'user')
```

### 7.4 Load Testing

```python
# locustfile.py - Teste de carga
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    
    @task
    def index(self):
        self.client.get("/")
    
    @task(3)
    def view_user(self):
        self.client.get("/users/1")

# Executar: locust -f locustfile.py --host=http://localhost:8000
```

---

## 8. CI/CD e DevOps

### 8.1 GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 8.2 Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Usuário não-root
RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/dbname
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  celery:
    build: .
    command: celery -A app.tasks worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/dbname
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

---

## 9. Logging e Monitoramento

### 9.1 Logging Estruturado

```python
# config/logging.py
import logging
import json
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler com JSON
    console_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Uso em aplicação
logger = logging.getLogger(__name__)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    logger.info("Fetching user", extra={"user_id": user_id})
    try:
        user = await db.get_user(user_id)
        logger.info("User fetched successfully", extra={
            "user_id": user_id,
            "status": "success"
        })
        return user
    except Exception as e:
        logger.error("Error fetching user", extra={
            "user_id": user_id,
            "error": str(e)
        })
        raise
```

### 9.2 Monitoramento com Prometheus

```python
# middleware para métricas
from prometheus_client import Counter, Histogram, generate_latest
import time

request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    duration = time.time() - start_time
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest())
```

---

## 10. Estrutura de Projeto Completa

```
projeto-web/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Inicialização FastAPI
│   │
│   ├── domain/                      # Lógica de negócio
│   │   ├── entities/
│   │   │   ├── user.py
│   │   │   └── post.py
│   │   ├── repositories/
│   │   │   └── user_repository.py   # Abstrações
│   │   └── services/
│   │       └── business_service.py  # Lógica de negócio
│   │
│   ├── application/                 # Casos de uso
│   │   ├── dtos/
│   │   │   ├── user_dto.py
│   │   │   └── post_dto.py
│   │   ├── use_cases/
│   │   │   └── create_user_use_case.py
│   │   └── mappers/
│   │       └── user_mapper.py
│   │
│   ├── infrastructure/              # Implementações externas
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── migrations/
│   │   ├── repositories/
│   │   │   └── sqlalchemy_user_repo.py  # Implementação concreta
│   │   ├── external_services/
│   │   │   └── email_service.py
│   │   └── cache/
│   │       └── redis_cache.py
│   │
│   ├── presentation/                # Controllers e schemas
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── users.py
│   │   │   │   └── posts.py
│   │   │   └── dependencies.py      # Dependency injection
│   │   ├── schemas/
│   │   │   ├── user_schema.py
│   │   │   └── post_schema.py
│   │   └── middleware/
│   │       └── auth_middleware.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py              # Configurações
│   │   ├── logging.py
│   │   └── database.py
│   │
│   └── utils/
│       ├── exceptions.py
│       └── validators.py
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_services.py
│   │   └── test_validators.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── conftest.py
│   ├── fixtures/
│   │   └── factories.py
│   └── e2e/
│       └── test_workflows.py
│
├── migrations/                      # Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── docs/                           # Documentação
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── SETUP.md
│
├── scripts/
│   ├── seed_db.py
│   └── backup_db.sh
│
├── .github/
│   └── workflows/
│       ├── test.yml
│       ├── lint.yml
│       └── deploy.yml
│
├── requirements.txt                # Dependências
├── requirements-dev.txt
├── pyproject.toml
├── pytest.ini
├── .pre-commit-config.yaml
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .gitignore
├── README.md
└── CONTRIBUTING.md
```

---

## 11. Checklist de Inicialização de Projeto

```markdown
# Iniciando novo projeto web com Python

## Setup inicial
- [ ] Criar ambiente virtual: `python -m venv venv`
- [ ] Ativar ambiente: `source venv/bin/activate`
- [ ] Instalar dependências: `pip install -r requirements.txt`

## Configuração
- [ ] Copiar `.env.example` para `.env`
- [ ] Configurar variáveis de ambiente
- [ ] Inicializar banco de dados: `alembic upgrade head`
- [ ] Criar super usuário (se aplicável)

## Desenvolvimento
- [ ] Instalar pre-commit hooks: `pre-commit install`
- [ ] Rodar testes: `pytest`
- [ ] Validar cobertura: `pytest --cov=app`
- [ ] Rodar linters: `black . && isort . && flake8`

## Deploy (CI/CD)
- [ ] Configurar GitHub Actions
- [ ] Configurar Docker
- [ ] Configurar variáveis de ambiente no CI/CD
- [ ] Testar pipeline localmente
```

---

## 12. Dependências Recomendadas

```txt
# requirements.txt

# Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9

# Validação
pydantic==2.5.0
pydantic-settings==2.1.0

# Segurança
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# Async
aioredis==2.0.1
httpx==0.25.1

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-env==1.1.3
faker==20.0.0

# Code Quality
black==23.12.0
isort==5.13.2
flake8==6.1.0
pylint==3.0.3
mypy==1.7.0

# Logging
python-json-logger==2.0.7

# Monitoring
prometheus-client==0.19.0

# Others
celery==5.3.4
redis==5.0.1
```

---

## 13. Referências e Recursos

### Documentação Oficial
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Pytest](https://docs.pytest.org/)

### Design Patterns
- "Clean Code" - Robert C. Martin
- "Clean Architecture" - Robert C. Martin
- "Design Patterns" - Gang of Four

### Python Best Practices
- [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [PEP 20](https://www.python.org/dev/peps/pep-0020/)

---

## 14. Conclusão

Esta especificação técnica fornece um framework abrangente para o desenvolvimento de sistemas web de alta qualidade com Python. A aplicação consistente desses princípios, padrões e práticas resulta em:

- ✅ Código mantível e escalável
- ✅ Segurança robusta
- ✅ Performance otimizada
- ✅ Qualidade consistente
- ✅ Facilidade de onboarding

O sucesso depende de aderência consistente aos princípios SOLID, design patterns apropriados e cultura de qualidade no time.

---

**Versão:** 1.0  
**Data:** 2026-04-28  
**Autor:** Arquitetura de Software  
**Status:** Ativo
