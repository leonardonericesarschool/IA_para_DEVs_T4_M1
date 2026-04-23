from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from validate_docbr import CPF
from datetime import datetime
from dateutil.parser import parse
import re

app = Flask(__name__)
api = Api(app)

# Simula um banco de dados em memória
users_db = []

def validate_cpf(cpf_number):
    cpf_validator = CPF()
    return cpf_validator.validate(cpf_number)

def validate_required_fields(data):
    required_fields = ['nome', 'cpf', 'data_nascimento', 'endereco']
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    return missing_fields

def format_cpf(cpf_number):
    # Remove caracteres não numéricos
    cpf_clean = re.sub(r'[^0-9]', '', cpf_number)
    if len(cpf_clean) != 11:
        return None
    return f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"

class UserResource(Resource):
    def post(self):
        data = request.get_json()

        # Validar campos obrigatórios
        missing_fields = validate_required_fields(data)
        if missing_fields:
            return {
                'error': 'Campos obrigatórios ausentes',
                'missing_fields': missing_fields
            }, 400

        # Formatar e validar CPF
        formatted_cpf = format_cpf(data['cpf'])
        if not formatted_cpf:
            return {'error': 'Formato de CPF inválido'}, 400
        
        if not validate_cpf(formatted_cpf):
            return {'error': 'CPF inválido'}, 400

        # Validar formato da data
        try:
            birth_date = parse(data['data_nascimento'])
            formatted_date = birth_date.strftime('%Y-%m-%d')
        except ValueError:
            return {'error': 'Data em formato inválido'}, 400

        # Criar novo usuário
        new_user = {
            'nome': data['nome'],
            'cpf': formatted_cpf,
            'data_nascimento': formatted_date,
            'endereco': data['endereco']
        }

        users_db.append(new_user)
        
        return {
            'message': 'Cadastro realizado com sucesso',
            'user': new_user
        }, 201

api.add_resource(UserResource, '/users')

if __name__ == '__main__':
    app.run(debug=True)