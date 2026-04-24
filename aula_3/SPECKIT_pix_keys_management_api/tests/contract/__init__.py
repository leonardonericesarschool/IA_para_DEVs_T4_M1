"""Contract tests for the POST /api/v1/pix-keys/register endpoint.

These tests verify the API contract:
- Request/response formats
- HTTP status codes for different scenarios
- Error handling and messages
- Authorization checks
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from src.main import create_app
from src.entities import PixKeyType, PixKeyStatus, PixKeyValidationStatus
from src.entities.pix_key import PixKey


@pytest.fixture
async def client():
    """Create an async HTTP client for testing."""
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_user_id():
    """Fixed user ID for testing."""
    return str(uuid4())


class TestRegisterPixKeyEndpointContract:
    """Contract tests for POST /api/v1/pix-keys/register endpoint."""

    @pytest.mark.asyncio
    async def test_successful_registration_returns_201_created(
        self, client, mock_user_id
    ):
        """Test that successful registration returns 201 Created."""
        request_data = {
            "key_type": "CPF",
            "key_value": "12345678910",
            "alias": "My CPF",
        }

        with patch("src.api.pix_keys_router.RegisterPixKeyUseCase") as mock_use_case:
            # Mock the use case to return a valid key
            mock_key = PixKey(
                key_id=str(uuid4()),
                user_id=mock_user_id,
                key_type=PixKeyType.CPF,
                key_value_hash="hash",
                key_value_masked="***.***.***-10",
                status=PixKeyStatus.ACTIVE,
                validation_status=PixKeyValidationStatus.VALID,
                alias="My CPF",
            )
            mock_use_case.return_value.execute.return_value = (
                mock_key,
                "12345678910",
            )

            response = await client.post(
                "/api/v1/pix-keys/register",
                json=request_data,
                headers={"Authorization": f"Bearer token-{mock_user_id}"},
            )

            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_successful_response_has_required_fields(
        self, client, mock_user_id
    ):
        """Test that successful response includes required fields."""
        request_data = {
            "key_type": "EMAIL",
            "key_value": "user@example.com",
        }

        with patch("src.api.pix_keys_router.RegisterPixKeyUseCase") as mock_use_case:
            mock_key = PixKey(
                key_id=str(uuid4()),
                user_id=mock_user_id,
                key_type=PixKeyType.EMAIL,
                key_value_hash="hash",
                key_value_masked="u***@example.com",
                status=PixKeyStatus.ACTIVE,
                validation_status=PixKeyValidationStatus.VALID,
            )
            mock_use_case.return_value.execute.return_value = (
                mock_key,
                "user@example.com",
            )

            response = await client.post(
                "/api/v1/pix-keys/register",
                json=request_data,
                headers={"Authorization": f"Bearer token-{mock_user_id}"},
            )

            assert response.status_code == 201
            data = response.json()
            assert "data" in data
            assert "message" in data
            assert "success" in data

    @pytest.mark.asyncio
    async def test_response_includes_plaintext_key_value_one_time(
        self, client, mock_user_id
    ):
        """Test that plaintext key_value is included only in registration response."""
        request_data = {
            "key_type": "CPF",
            "key_value": "12345678910",
        }

        with patch("src.api.pix_keys_router.RegisterPixKeyUseCase") as mock_use_case:
            mock_key = PixKey(
                key_id=str(uuid4()),
                user_id=mock_user_id,
                key_type=PixKeyType.CPF,
                key_value_hash="hash",
                key_value_masked="***.***.***-10",
                status=PixKeyStatus.ACTIVE,
                validation_status=PixKeyValidationStatus.VALID,
            )
            mock_use_case.return_value.execute.return_value = (
                mock_key,
                "12345678910",
            )

            response = await client.post(
                "/api/v1/pix-keys/register",
                json=request_data,
                headers={"Authorization": f"Bearer token-{mock_user_id}"},
            )

            assert response.status_code == 201
            data = response.json()
            # Plaintext should be in the response
            assert "key_value" in data["data"]
            assert data["data"]["key_value"] == "12345678910"

    @pytest.mark.asyncio
    async def test_invalid_request_returns_400_bad_request(
        self, client, mock_user_id
    ):
        """Test that invalid request returns 400 Bad Request."""
        request_data = {
            "key_type": "INVALID_TYPE",  # Invalid enum value
            "key_value": "something",
        }

        response = await client.post(
            "/api/v1/pix-keys/register",
            json=request_data,
            headers={"Authorization": f"Bearer token-{mock_user_id}"},
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_duplicate_key_returns_409_conflict(
        self, client, mock_user_id
    ):
        """Test that duplicate key detection returns 409 Conflict."""
        request_data = {
            "key_type": "CPF",
            "key_value": "12345678910",  # Already registered for this user
        }

        with patch(
            "src.api.pix_keys_router.RegisterPixKeyUseCase"
        ) as mock_use_case:
            from src.exceptions import DuplicateKeyError

            mock_use_case.return_value.execute.side_effect = DuplicateKeyError(
                "CPF key already registered"
            )

            response = await client.post(
                "/api/v1/pix-keys/register",
                json=request_data,
                headers={"Authorization": f"Bearer token-{mock_user_id}"},
            )

            assert response.status_code == 409
            data = response.json()
            assert "error" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_max_keys_exceeded_returns_429_too_many_requests(
        self, client, mock_user_id
    ):
        """Test that exceeding max keys limit returns 429 Too Many Requests."""
        request_data = {
            "key_type": "EMAIL",
            "key_value": "user@example.com",
        }

        with patch(
            "src.api.pix_keys_router.RegisterPixKeyUseCase"
        ) as mock_use_case:
            from src.exceptions import MaxKeysExceededError

            mock_use_case.return_value.execute.side_effect = MaxKeysExceededError(
                "Maximum 5 keys per user"
            )

            response = await client.post(
                "/api/v1/pix-keys/register",
                json=request_data,
                headers={"Authorization": f"Bearer token-{mock_user_id}"},
            )

            assert response.status_code == 429
            data = response.json()
            assert "error" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_missing_auth_token_returns_401_unauthorized(
        self, client
    ):
        """Test that missing authentication token returns 401 Unauthorized."""
        request_data = {
            "key_type": "CPF",
            "key_value": "12345678910",
        }

        response = await client.post(
            "/api/v1/pix-keys/register",
            json=request_data,
            # No Authorization header
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_validation_error_returns_400_with_details(
        self, client, mock_user_id
    ):
        """Test that validation errors return 400 with error details."""
        request_data = {
            "key_type": "CPF",
            "key_value": "invalid_cpf",  # Invalid CPF format
        }

        with patch(
            "src.api.pix_keys_router.RegisterPixKeyUseCase"
        ) as mock_use_case:
            from src.exceptions import ValidationError

            mock_use_case.return_value.execute.side_effect = ValidationError(
                "Invalid CPF format"
            )

            response = await client.post(
                "/api/v1/pix-keys/register",
                json=request_data,
                headers={"Authorization": f"Bearer token-{mock_user_id}"},
            )

            assert response.status_code == 400
            data = response.json()
            assert "error" in data or "detail" in data
            assert "CPF" in str(data)

    @pytest.mark.asyncio
    async def test_response_includes_created_key_metadata(
        self, client, mock_user_id
    ):
        """Test that response includes key metadata."""
        request_data = {
            "key_type": "PHONE",
            "key_value": "11987654321",
            "alias": "My Phone",
        }

        with patch("src.api.pix_keys_router.RegisterPixKeyUseCase") as mock_use_case:
            mock_key = PixKey(
                key_id=str(uuid4()),
                user_id=mock_user_id,
                key_type=PixKeyType.PHONE,
                key_value_hash="hash",
                key_value_masked="(11) 9****-4321",
                status=PixKeyStatus.ACTIVE,
                validation_status=PixKeyValidationStatus.VALID,
                alias="My Phone",
                is_preferred=False,
            )
            mock_use_case.return_value.execute.return_value = (
                mock_key,
                "11987654321",
            )

            response = await client.post(
                "/api/v1/pix-keys/register",
                json=request_data,
                headers={"Authorization": f"Bearer token-{mock_user_id}"},
            )

            assert response.status_code == 201
            data = response.json()
            key_data = data["data"]
            assert key_data["key_type"] == "PHONE"
            assert key_data["alias"] == "My Phone"
            assert key_data["status"] == "ACTIVE"
            assert "key_id" in key_data
            assert "created_at" in key_data

    @pytest.mark.asyncio
    async def test_response_doesn_not_expose_key_value_hash(
        self, client, mock_user_id
    ):
        """Test that the key_value_hash (internal) is never exposed in response."""
        request_data = {
            "key_type": "CPF",
            "key_value": "12345678910",
        }

        with patch("src.api.pix_keys_router.RegisterPixKeyUseCase") as mock_use_case:
            mock_key = PixKey(
                key_id=str(uuid4()),
                user_id=mock_user_id,
                key_type=PixKeyType.CPF,
                key_value_hash="sha256_hash_value",  # Internal
                key_value_masked="***.***.***-10",
                status=PixKeyStatus.ACTIVE,
                validation_status=PixKeyValidationStatus.VALID,
            )
            mock_use_case.return_value.execute.return_value = (
                mock_key,
                "12345678910",
            )

            response = await client.post(
                "/api/v1/pix-keys/register",
                json=request_data,
                headers={"Authorization": f"Bearer token-{mock_user_id}"},
            )

            assert response.status_code == 201
            data = response.json()
            # Hash should never be in external API response
            assert "key_value_hash" not in data
            assert "key_value_hash" not in str(data)
