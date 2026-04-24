"""Integration tests for Pix key API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestPixKeyAPI:
    """Integration tests for Pix key API endpoints."""

    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data

    async def test_criar_chave_cpf_sucesso(self, async_client: AsyncClient):
        """Test creating a valid CPF Pix key."""
        request_data = {
            "tipo_chave": "CPF",
            "valor_chave": "11144477735",
            "conta_id": 1,
            "cliente_id": 1,
        }

        response = await async_client.post("/api/v1/pix-keys", json=request_data)

        assert response.status_code == 201
        data = response.json()
        assert data["tipo_chave"] == "CPF"
        assert data["valor_chave"] == "11144477735"
        assert data["status"] == "CRIADA"
        assert "id" in data
        assert "criado_em" in data

    async def test_criar_chave_email_sucesso(self, async_client: AsyncClient):
        """Test creating a valid EMAIL Pix key."""
        request_data = {
            "tipo_chave": "EMAIL",
            "valor_chave": "user@example.com",
            "conta_id": 1,
            "cliente_id": 1,
        }

        response = await async_client.post("/api/v1/pix-keys", json=request_data)

        assert response.status_code == 201
        data = response.json()
        assert data["tipo_chave"] == "EMAIL"
        assert data["valor_chave"] == "user@example.com"

    async def test_criar_chave_telefone_sucesso(self, async_client: AsyncClient):
        """Test creating a valid TELEFONE Pix key."""
        request_data = {
            "tipo_chave": "TELEFONE",
            "valor_chave": "11987654321",
            "conta_id": 1,
            "cliente_id": 1,
        }

        response = await async_client.post("/api/v1/pix-keys", json=request_data)

        assert response.status_code == 201
        data = response.json()
        assert data["tipo_chave"] == "TELEFONE"

    async def test_criar_chave_cnpj_sucesso(self, async_client: AsyncClient):
        """Test creating a valid CNPJ Pix key."""
        request_data = {
            "tipo_chave": "CNPJ",
            "valor_chave": "11222333000181",
            "conta_id": 1,
            "cliente_id": 1,
        }

        response = await async_client.post("/api/v1/pix-keys", json=request_data)

        assert response.status_code == 201
        data = response.json()
        assert data["tipo_chave"] == "CNPJ"

    async def test_criar_chave_cpf_invalido_formato(self, async_client: AsyncClient):
        """Test creating CPF Pix key with invalid format."""
        request_data = {
            "tipo_chave": "CPF",
            "valor_chave": "123",  # Too short
            "conta_id": 1,
            "cliente_id": 1,
        }

        response = await async_client.post("/api/v1/pix-keys", json=request_data)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    async def test_criar_chave_email_invalido_formato(self, async_client: AsyncClient):
        """Test creating EMAIL Pix key with invalid format."""
        request_data = {
            "tipo_chave": "EMAIL",
            "valor_chave": "invalid-email",  # Missing @
            "conta_id": 1,
            "cliente_id": 1,
        }

        response = await async_client.post("/api/v1/pix-keys", json=request_data)

        assert response.status_code == 400

    async def test_criar_chave_duplicada(self, async_client: AsyncClient):
        """Test creating duplicate Pix key for same client."""
        request_data = {
            "tipo_chave": "CPF",
            "valor_chave": "11144477735",
            "conta_id": 1,
            "cliente_id": 1,
        }

        # Create first key
        response1 = await async_client.post("/api/v1/pix-keys", json=request_data)
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = await async_client.post("/api/v1/pix-keys", json=request_data)

        assert response2.status_code == 409
        data = response2.json()
        assert "detail" in data

    async def test_consultar_chave_sucesso(self, async_client: AsyncClient):
        """Test querying an existing Pix key."""
        # Create a key first
        create_request = {
            "tipo_chave": "CPF",
            "valor_chave": "11144477735",
            "conta_id": 1,
            "cliente_id": 1,
        }
        create_response = await async_client.post("/api/v1/pix-keys", json=create_request)
        assert create_response.status_code == 201
        chave_id = create_response.json()["id"]

        # Query the key
        response = await async_client.get(f"/api/v1/pix-keys/{chave_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == chave_id
        assert data["tipo_chave"] == "CPF"

    async def test_consultar_chave_nao_encontrada(self, async_client: AsyncClient):
        """Test querying non-existent Pix key."""
        response = await async_client.get(
            "/api/v1/pix-keys/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    async def test_listar_chaves_cliente_vazio(self, async_client: AsyncClient):
        """Test listing keys for client with no keys."""
        response = await async_client.get("/api/v1/pix-keys/cliente/999")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["limit"] == 10

    async def test_listar_chaves_cliente_com_items(self, async_client: AsyncClient):
        """Test listing keys for client with keys."""
        # Create multiple keys
        for i in range(3):
            request_data = {
                "tipo_chave": "EMAIL",
                "valor_chave": f"user{i}@example.com",
                "conta_id": 1,
                "cliente_id": 1,
            }
            await async_client.post("/api/v1/pix-keys", json=request_data)

        # List keys
        response = await async_client.get("/api/v1/pix-keys/cliente/1")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3
        assert data["page"] == 1
        assert data["limit"] == 10

    async def test_listar_chaves_cliente_paginacao(self, async_client: AsyncClient):
        """Test listing keys with pagination."""
        # Create 15 keys
        for i in range(15):
            request_data = {
                "tipo_chave": "EMAIL",
                "valor_chave": f"user{i}@example.com",
                "conta_id": 1,
                "cliente_id": 2,
            }
            await async_client.post("/api/v1/pix-keys", json=request_data)

        # Get first page
        response1 = await async_client.get("/api/v1/pix-keys/cliente/2?skip=0&limit=10")
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["items"]) == 10
        assert data1["total"] == 15
        assert data1["page"] == 1

        # Get second page
        response2 = await async_client.get("/api/v1/pix-keys/cliente/2?skip=10&limit=10")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["items"]) == 5
        assert data2["total"] == 15
        assert data2["page"] == 2

    async def test_deletar_chave_sucesso(self, async_client: AsyncClient):
        """Test deleting an existing Pix key."""
        # Create a key
        create_request = {
            "tipo_chave": "CPF",
            "valor_chave": "11144477735",
            "conta_id": 1,
            "cliente_id": 1,
        }
        create_response = await async_client.post("/api/v1/pix-keys", json=create_request)
        chave_id = create_response.json()["id"]

        # Delete the key
        response = await async_client.delete(f"/api/v1/pix-keys/{chave_id}")

        assert response.status_code == 204

        # Verify key is deleted (should return 404)
        query_response = await async_client.get(f"/api/v1/pix-keys/{chave_id}")
        assert query_response.status_code == 404

    async def test_deletar_chave_nao_encontrada(self, async_client: AsyncClient):
        """Test deleting non-existent Pix key."""
        response = await async_client.delete(
            "/api/v1/pix-keys/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404

    async def test_listar_chaves_conta(self, async_client: AsyncClient):
        """Test listing keys by account."""
        # Create keys for account 1
        for i in range(2):
            request_data = {
                "tipo_chave": "EMAIL",
                "valor_chave": f"user{i}@example.com",
                "conta_id": 1,
                "cliente_id": i + 1,
            }
            await async_client.post("/api/v1/pix-keys", json=request_data)

        # List keys by account
        response = await async_client.get("/api/v1/pix-keys/conta/1")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
