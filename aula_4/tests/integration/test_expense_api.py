"""Integration tests for expense API endpoints."""
import json

import pytest


class TestExpenseAPI:
    """Test suite for expense API endpoints."""

    def test_create_expense_valid_alimentacao(self, client):
        """Test POST /expenses with valid alimentação (R$ 80,00)."""
        # Cenário 1: Registrar despesa válida de alimentação
        # Dado que o funcionário envia um registro de despesa com nome,
        # tipo de despesa `alimentação` e valor de R$ 80,00
        data = {
            "name": "Almoço de trabalho",
            "type": "alimentação",
            "amount": 80.0,
        }

        # Quando o sistema processar a solicitação
        response = client.post("/expenses", data=json.dumps(data), content_type="application/json")

        # Então a despesa deve ser aceita e o endpoint deve retornar uma mensagem de sucesso
        assert response.status_code == 201
        body = response.get_json()
        assert body["status"] == "aceita"
        assert body["name"] == "Almoço de trabalho"
        assert body["type"] == "alimentação"
        assert body["amount"] == 80.0
        assert body["message"] == "Despesa registrada com sucesso"
        assert body["id"] is not None

    def test_create_expense_invalid_alimentacao_over_limit(self, client):
        """Test POST /expenses with invalid alimentação (R$ 120,00)."""
        # Cenário 2: Recusar despesa de alimentação acima do limite
        # Dado que o funcionário envia um registro de despesa com nome,
        # tipo de despesa `alimentação` e valor de R$ 120,00
        data = {
            "name": "Almoço caro",
            "type": "alimentação",
            "amount": 120.0,
        }

        # Quando o sistema processar a solicitação
        response = client.post("/expenses", data=json.dumps(data), content_type="application/json")

        # Então a despesa deve ser recusada automaticamente e o endpoint deve indicar a recusa
        assert response.status_code == 400
        body = response.get_json()
        assert body["status"] == "recusada"
        assert body["name"] == "Almoço caro"
        assert body["type"] == "alimentação"
        assert body["amount"] == 120.0
        assert "não pode exceder R$ 100,00" in body["message"]
        assert body["id"] is not None

    def test_create_expense_valid_transporte(self, client):
        """Test POST /expenses with valid transporte (R$ 150,00)."""
        # Cenário 3: Registrar despesa de transporte sem limite adicional
        # Dado que o funcionário envia um registro de despesa com nome,
        # tipo de despesa `transporte` e valor de R$ 150,00
        data = {
            "name": "Passagem aérea",
            "type": "transporte",
            "amount": 150.0,
        }

        # Quando o sistema processar a solicitação
        response = client.post("/expenses", data=json.dumps(data), content_type="application/json")

        # Então a despesa deve ser aceita e o endpoint deve retornar uma mensagem de sucesso
        assert response.status_code == 201
        body = response.get_json()
        assert body["status"] == "aceita"
        assert body["name"] == "Passagem aérea"
        assert body["type"] == "transporte"
        assert body["amount"] == 150.0
        assert body["message"] == "Despesa registrada com sucesso"

    def test_create_expense_missing_field(self, client):
        """Test POST /expenses with missing required field."""
        data = {
            "name": "Almoço",
            "type": "alimentação",
            # Missing amount
        }

        response = client.post("/expenses", data=json.dumps(data), content_type="application/json")

        assert response.status_code == 422

    def test_create_expense_invalid_type(self, client):
        """Test POST /expenses with invalid expense type."""
        data = {
            "name": "Teste",
            "type": "invalido",
            "amount": 50.0,
        }

        response = client.post("/expenses", data=json.dumps(data), content_type="application/json")

        assert response.status_code == 422

    def test_create_expense_negative_amount(self, client):
        """Test POST /expenses with negative amount."""
        data = {
            "name": "Teste",
            "type": "alimentação",
            "amount": -50.0,
        }

        response = client.post("/expenses", data=json.dumps(data), content_type="application/json")

        assert response.status_code == 422

    def test_create_expense_zero_amount(self, client):
        """Test POST /expenses with zero amount."""
        data = {
            "name": "Teste",
            "type": "alimentação",
            "amount": 0.0,
        }

        response = client.post("/expenses", data=json.dumps(data), content_type="application/json")

        assert response.status_code == 422

    def test_list_expenses_empty(self, client):
        """Test GET /expenses with no expenses."""
        response = client.get("/expenses")

        assert response.status_code == 200
        body = response.get_json()
        assert body == []

    def test_list_expenses_multiple(self, client):
        """Test GET /expenses with multiple expenses."""
        # Create some expenses first
        expenses_data = [
            {"name": "Almoço 1", "type": "alimentação", "amount": 80.0},
            {"name": "Uber", "type": "transporte", "amount": 50.0},
            {"name": "Almoço 2", "type": "alimentação", "amount": 120.0},
        ]

        for data in expenses_data:
            client.post(
                "/expenses", data=json.dumps(data), content_type="application/json"
            )

        # Get all expenses
        response = client.get("/expenses")

        assert response.status_code == 200
        body = response.get_json()
        assert len(body) == 3
        # Verify they're in reverse order (newest first)
        assert body[0]["name"] == "Almoço 2"
        assert body[1]["name"] == "Uber"
        assert body[2]["name"] == "Almoço 1"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/expenses/health")

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "healthy"

    def test_alimentacao_at_limit_accepted(self, client):
        """Test alimentação at exactly R$ 100 limit is accepted."""
        data = {
            "name": "Almoço limite",
            "type": "alimentação",
            "amount": 100.0,
        }

        response = client.post("/expenses", data=json.dumps(data), content_type="application/json")

        assert response.status_code == 201
        body = response.get_json()
        assert body["status"] == "aceita"

    def test_alimentacao_just_over_limit_rejected(self, client):
        """Test alimentação just over R$ 100 limit is rejected."""
        data = {
            "name": "Almoço",
            "type": "alimentação",
            "amount": 100.01,
        }

        response = client.post("/expenses", data=json.dumps(data), content_type="application/json")

        assert response.status_code == 400
        body = response.get_json()
        assert body["status"] == "recusada"

    def test_transporte_high_amount_accepted(self, client):
        """Test transporte with high amount is accepted."""
        data = {
            "name": "Passagem aérea internacional",
            "type": "transporte",
            "amount": 5000.0,
        }

        response = client.post("/expenses", data=json.dumps(data), content_type="application/json")

        assert response.status_code == 201
        body = response.get_json()
        assert body["status"] == "aceita"
        assert body["amount"] == 5000.0

    def test_empty_name(self, client):
        """Test creating expense with empty name."""
        data = {
            "name": "",
            "type": "alimentação",
            "amount": 50.0,
        }

        response = client.post("/expenses", data=json.dumps(data), content_type="application/json")

        assert response.status_code == 422

    def test_whitespace_name(self, client):
        """Test creating expense with whitespace-only name."""
        data = {
            "name": "   ",
            "type": "alimentação",
            "amount": 50.0,
        }

        response = client.post("/expenses", data=json.dumps(data), content_type="application/json")

        # Should be stripped and then rejected as empty
        assert response.status_code == 422

    def test_no_json_body(self, client):
        """Test POST without JSON body."""
        response = client.post("/expenses", data=None, content_type="application/json")

        assert response.status_code == 400
        body = response.get_json()
        assert "Request body must be JSON" in body["error"]
