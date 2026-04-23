import pytest
from main import app
from datetime import datetime, timedelta
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_successful_customer_registration(client):
    """
    Scenario: Successfully register a new customer
    Given the user is on the registration page
    When they fill in all required fields
    Then the system should save the customer information
    And display a success message
    """
    data = {
        "name": "John Doe",
        "address": "123 Main St",
        "cpf": "529.982.247-25",  # CPF válido
        "birth_date": "1990-01-01"
    }
    
    response = client.post('/customer',
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == 'Customer registered successfully'
    assert json_data['customer']['name'] == data['name']
    assert json_data['customer']['address'] == data['address']
    assert json_data['customer']['cpf'] == data['cpf']
    assert json_data['customer']['birth_date'] == data['birth_date']
    assert 'registration_date' in json_data['customer']

def test_invalid_cpf_format(client):
    """
    Scenario: Validate CPF format
    Given the user is on the registration page
    When they enter an invalid CPF format
    Then the system should display an error message
    """
    data = {
        "name": "John Doe",
        "address": "123 Main St",
        "cpf": "111.111.111-11",  # CPF inválido
        "birth_date": "1990-01-01"
    }
    
    response = client.post('/customer',
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == 'Invalid CPF format'

def test_underage_customer(client):
    """
    Scenario: Validate customer age
    Given the user is on the registration page
    When they enter a date of birth
    Then the system should validate if the customer is at least 18 years old
    """
    # Calculando uma data que representa alguém com 17 anos
    today = datetime.now()
    underage_date = (today - timedelta(days=17*365)).strftime('%Y-%m-%d')
    
    data = {
        "name": "John Doe Jr",
        "address": "123 Main St",
        "cpf": "529.982.247-25",
        "birth_date": underage_date
    }
    
    response = client.post('/customer',
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == 'Customer must be at least 18 years old'

def test_missing_required_fields(client):
    """
    Additional test: Verify required fields
    Given the user is on the registration page
    When they submit incomplete data
    Then the system should indicate missing fields
    """
    data = {
        "name": "John Doe",
        # address field missing
        "cpf": "529.982.247-25"
    }
    
    response = client.post('/customer',
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == 'Missing required fields'
    assert 'required_fields' in json_data

def test_list_customers(client):
    """
    Additional test: Verify customer listing
    Given customers are registered in the system
    When requesting the customer list
    Then the system should return all customers
    """
    # Primeiro, vamos registrar um cliente
    data = {
        "name": "John Doe",
        "address": "123 Main St",
        "cpf": "529.982.247-25",
        "birth_date": "1990-01-01"
    }
    
    client.post('/customer',
               data=json.dumps(data),
               content_type='application/json')
    
    # Agora vamos verificar a listagem
    response = client.get('/customer')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert isinstance(json_data, list)
    assert len(json_data) > 0
    assert json_data[0]['name'] == data['name']