# Sistema de Despesas Corporativas

API Flask para registrar e validar despesas corporativas com validação automática de limites de despesa.

## Requisitos

- Python 3.11+
- pip ou pip3

## Instalação

### 1. Clonar o repositório e navegar para o diretório
```bash
cd /home/lvn/IA_para_DEVs_T4_M1/aula_4
```

### 2. Criar ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar dependências
```bash
pip install -r requirements-dev.txt
```

### 4. Configurar variáveis de ambiente
```bash
cp .env.example .env
```

### 5. Inicializar o banco de dados
```bash
python -c "from app.infrastructure.database.connection import init_db; from app.main import app; init_db(app)"
```

## Uso

### Executar a aplicação
```bash
flask run
```

A API estará disponível em `http://localhost:5000`

### Endpoints

#### POST /expenses
Registrar uma nova despesa.

**Request:**
```json
{
  "name": "Almoço de trabalho",
  "type": "alimentação",
  "amount": 80.00
}
```

**Response (201 - Sucesso):**
```json
{
  "id": 1,
  "name": "Almoço de trabalho",
  "type": "alimentação",
  "amount": 80.00,
  "status": "aceita",
  "message": "Despesa registrada com sucesso"
}
```

**Response (400 - Recusa):**
```json
{
  "id": 1,
  "name": "Almoço de trabalho",
  "type": "alimentação",
  "amount": 120.00,
  "status": "recusada",
  "message": "Despesa de alimentação não pode exceder R$ 100,00"
}
```

#### GET /expenses
Listar todas as despesas registradas.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Almoço de trabalho",
    "type": "alimentação",
    "amount": 80.00,
    "status": "aceita"
  }
]
```

## Validações

### Alimentação (alimentação)
- Limite máximo: R$ 100,00
- Valores acima deste limite são automaticamente recusados

### Transporte (transporte)
- Sem limite de valor
- Sempre aceito

## Testes

### Executar testes
```bash
pytest
```

### Executar com cobertura
```bash
pytest --cov=app --cov-report=html
```

A cobertura de testes deve ser >= 80%.

### Testes unitários
```bash
pytest tests/unit -v
```

### Testes de integração
```bash
pytest tests/integration -v
```

## Arquitetura

O projeto segue **Clean Architecture** com as seguintes camadas:

- **domain/**: Entidades e lógica de negócio (sem dependências externas)
- **application/**: Casos de uso e DTOs (orquestração de lógica)
- **infrastructure/**: Implementações de banco de dados e repositórios
- **presentation/**: Controllers, schemas e rotas da API

## Desenvolvimento

### Formatação de código
```bash
black app tests
isort app tests
```

### Linting
```bash
flake8 app tests
pylint app tests
```

### Type checking
```bash
mypy app
```

## Docker (Opcional)

### Build da imagem
```bash
docker-compose build
```

### Executar a aplicação
```bash
docker-compose up
```

A API estará disponível em `http://localhost:5000`

## Estrutura do Projeto

```
projeto/
├── app/
│   ├── domain/                  # Lógica de negócio
│   ├── application/             # Casos de uso
│   ├── infrastructure/          # Banco de dados
│   ├── presentation/            # API routes
│   ├── config/                  # Configurações
│   └── main.py                  # App factory
├── tests/
│   ├── unit/                    # Testes unitários
│   └── integration/             # Testes de integração
├── requirements.txt             # Dependências
├── requirements-dev.txt         # Dev dependencies
├── pytest.ini                   # Configuração pytest
├── docker-compose.yml           # Orquestração Docker
├── Dockerfile                   # Build Docker
└── .env.example                 # Template de variáveis
```

## Próximos Passos

- [ ] Adicionar autenticação JWT
- [ ] Implementar paginação em GET /expenses
- [ ] Adicionar filtros por tipo e data
- [ ] Configurar CI/CD com GitHub Actions
- [ ] Adicionar logging estruturado
- [ ] Implementar relatórios de despesas
