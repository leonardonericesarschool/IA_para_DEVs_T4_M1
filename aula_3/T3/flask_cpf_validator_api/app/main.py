from flask import Flask, request, jsonify

app = Flask(__name__)

# CPF validation function
def validate_cpf(cpf: str) -> bool:
    '''Validate a Brazilian CPF number.
        args:
            cpf (str): The CPF number as a string, which may include formatting characters.
        returns:
            bool: True if the CPF is valid, False otherwise.
    '''

    # Remove any non-numeric characters
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Check if CPF has 11 digits
    if len(cpf) != 11:
        return False
    
    # Check if all digits are the same
    if len(set(cpf)) == 1:
        return False
    
    # Calculate sum of products for first digit
    sum_of_products = 0
    for i in range(9):
        digit = int(cpf[i])
        multiplier = 10 - i
        sum_of_products += digit * multiplier
    expected_digit1 = (sum_of_products * 10 % 11) % 10
    if int(cpf[-2]) != expected_digit1:
        return False
        
    # Calculate second digit
    sum_of_products = sum(int(a) * b for a, b in zip(cpf[:-1], range(11, 1, -1)))
    expected_digit2 = (sum_of_products * 10 % 11) % 10
    if int(cpf[-1]) != expected_digit2:
        return False
        
    return True

@app.route('/validate-cpf/<cpf>', methods=['GET'])
def validate_cpf_get(cpf):
    is_valid = validate_cpf(cpf)
    return jsonify({
        'cpf': cpf,
        'is_valid': is_valid
    })

@app.route('/validate-cpf', methods=['POST'])
def validate_cpf_post():
    data = request.get_json()
    
    if not data or 'cpf' not in data:
        return jsonify({
            'error': 'CPF not provided in request body'
        }), 400
    
    cpf = data['cpf']
    is_valid = validate_cpf(cpf)
    
    return jsonify({
        'cpf': cpf,
        'is_valid': is_valid
    })

if __name__ == '__main__':
    app.run(debug=True)