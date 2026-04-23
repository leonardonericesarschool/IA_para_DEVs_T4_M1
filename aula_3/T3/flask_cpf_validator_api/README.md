# CPF Validator API

This is a simple Flask API that validates Brazilian CPF numbers.

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

From the project root directory, run:

```bash
python app/main.py
```

The API will start on `http://localhost:5000`

## Endpoints

### GET /validate-cpf/{cpf}

Validates a CPF number passed in the URL.

Example:
```bash
curl http://localhost:5000/validate-cpf/12345678909
```

### POST /validate-cpf

Validates a CPF number passed in the request body.

Example:
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"cpf": "12345678909"}' \
     http://localhost:5000/validate-cpf
```

## Response Format

The API returns a JSON response with the following format:

```json
{
    "cpf": "12345678909",
    "is_valid": true|false
}
```

## Error Handling

If you make a POST request without a CPF number, you'll receive a 400 status code with an error message:

```json
{
    "error": "CPF not provided in request body"
}
```