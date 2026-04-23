import pytest
from app.main import app, users_db
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # Limpa o banco de dados após cada teste
    users_db.clear()

def test_cadastro_usuario_sucesso(client):
    """
    Cenário: Cadastrar novo usuário com dados válidos
    """
    data = {
        "nome": "João Silva",
        "cpf": "529.982.247-25",
        "data_nascimento": "1990-01-01",
        "endereco": "Rua Exemplo, 123"
    }
    
    response = client.post('/users',
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 201
    assert response.json['message'] == 'Cadastro realizado com sucesso'
    assert response.json['user']['nome'] == data['nome']
    assert response.json['user']['cpf'] == data['cpf']
    assert response.json['user']['data_nascimento'] == data['data_nascimento']
    assert response.json['user']['endereco'] == data['endereco']

def test_cadastro_campos_vazios(client):
    """
    Cenário: Tentar cadastrar usuário com campos vazios
    """
    # Teste com campos faltando
    data = {
        "nome": "",
        "cpf": "529.982.247-25",
        "data_nascimento": "",
        "endereco": "Rua Exemplo, 123"
    }
    
    response = client.post('/users',
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'missing_fields' in response.json
    assert 'nome' in response.json['missing_fields']
    assert 'data_nascimento' in response.json['missing_fields']

def test_cadastro_cpf_invalido(client):
    """
    Cenário: Tentar cadastrar usuário com CPF inválido
    """
    data = {
        "nome": "João Silva",
        "cpf": "111.111.111-11",  # CPF inválido
        "data_nascimento": "1990-01-01",
        "endereco": "Rua Exemplo, 123"
    }
    
    response = client.post('/users',
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 400
    assert response.json['error'] == 'CPF inválido'

def test_cadastro_cpf_formato_invalido(client):
    """
    Cenário: Tentar cadastrar usuário com formato de CPF inválido
    """
    data = {
        "nome": "João Silva",
        "cpf": "123456",  # Formato inválido
        "data_nascimento": "1990-01-01",
        "endereco": "Rua Exemplo, 123"
    }
    
    response = client.post('/users',
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 400
    assert response.json['error'] == 'Formato de CPF inválido'

def test_cadastro_data_invalida(client):
    """
    Cenário: Tentar cadastrar usuário com data em formato inválido
    """
    data = {
        "nome": "João Silva",
        "cpf": "529.982.247-25",
        "data_nascimento": "data-invalida",
        "endereco": "Rua Exemplo, 123"
    }
    
    response = client.post('/users',
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 400
    assert response.json['error'] == 'Data em formato inválido'