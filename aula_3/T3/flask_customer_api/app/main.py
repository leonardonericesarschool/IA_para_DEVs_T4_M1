from flask import Flask, request, jsonify
from datetime import datetime
from dateutil.relativedelta import relativedelta
from validate_docbr import CPF

app = Flask(__name__)

# Simulando um banco de dados com uma lista
customers = []

def validate_cpf(cpf_number):
    cpf = CPF()
    return cpf.validate(cpf_number)

def validate_age(birth_date):
    try:
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        age = relativedelta(datetime.now(), birth_date).years
        return age >= 18
    except ValueError:
        return False

@app.route('/customer', methods=['POST'])
def register_customer():
    data = request.get_json()
    
    # Verificar se todos os campos necessários estão presentes
    required_fields = ['name', 'address', 'cpf', 'birth_date']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields',
            'required_fields': required_fields
        }), 400
    
    # Validar CPF
    if not validate_cpf(data['cpf']):
        return jsonify({
            'error': 'Invalid CPF format'
        }), 400
    
    # Validar idade
    if not validate_age(data['birth_date']):
        return jsonify({
            'error': 'Customer must be at least 18 years old'
        }), 400
    
    # Criar novo cliente
    new_customer = {
        'id': len(customers) + 1,
        'name': data['name'],
        'address': data['address'],
        'cpf': data['cpf'],
        'birth_date': data['birth_date'],
        'registration_date': datetime.now().isoformat()
    }
    
    # Adicionar à lista de clientes
    customers.append(new_customer)
    
    return jsonify({
        'message': 'Customer registered successfully',
        'customer': new_customer
    }), 201

@app.route('/customer', methods=['GET'])
def list_customers():
    return jsonify(customers), 200

if __name__ == '__main__':
    app.run(debug=True)