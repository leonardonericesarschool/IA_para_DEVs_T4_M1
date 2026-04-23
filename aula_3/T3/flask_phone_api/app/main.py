from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# Regex para validar telefones brasileiros (formato simples)
PHONE_REGEX = re.compile(r"^(\+?55)?\s?\(?\d{2}\)?\s?\d{4,5}-?\d{4}$")

@app.route('/phone', methods=['GET'])
def get_info():
    return jsonify({
        "message": "API para validação de telefones. Use o endpoint POST /phone para validar um número."
    })

@app.route('/phone', methods=['POST'])
def validate_phone():
    data = request.get_json()
    phone = data.get('phone')
    if not phone:
        return jsonify({"valid": False, "error": "Campo 'phone' é obrigatório."}), 400
    is_valid = bool(PHONE_REGEX.match(phone))
    return jsonify({"valid": is_valid, "phone": phone})

if __name__ == '__main__':
    app.run(debug=True)
