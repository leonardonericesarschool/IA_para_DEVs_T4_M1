from flask import Flask, request, jsonify
import re

app = Flask(__name__)


def validate_cpf(cpf: str) -> bool:
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        value = sum(int(cpf[num]) * ((i+1) - num) for num in range(0, i))
        check = ((value * 10) % 11) % 10
        if check != int(cpf[i]):
            return False
    return True

# Endpoint to validate CPF
@app.route('/cpf/<cpf>', methods=['GET'])
def get_cpf(cpf):
    is_valid = validate_cpf(cpf)
    return jsonify({"cpf": cpf, "valid": is_valid})

# Endpoint to validate CPF in JSON
@app.route('/cpf', methods=['POST'])
def post_cpf():
    data = request.get_json()
    cpf = data.get('cpf', '')
    is_valid = validate_cpf(cpf)
    return jsonify({"cpf": cpf, "valid": is_valid})

if __name__ == '__main__':
    app.run(debug=True)
