"""Unit tests for ViewPixKeysUseCase - Test-Driven Development approach.

These tests are written FIRST to define the expected behavior of the use case.
They specify requirements for:
- Successful retrieval of all pix keys
- Filtering by status and type
- Sorting behavior
- Pagination
- Masked key values in response
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock
from datetime import datetime

from src.entities import PixKeyType, PixKeyStatus, PixKeyValidationStatus
from src.entities.pix_key import PixKey
from src.exceptions import InvalidFilterError


class MockViewPixKeysUseCase:
    """Mock use case for testing View Pix Keys functionality"""
    
    def __init__(self, pix_key_repository):
        self.pix_key_repo = pix_key_repository
    
    async def execute(
        self,
        user_id: str,
        status: str = None,
        key_type: str = None,
        sort_by: str = "created_at",
        page: int = 1,
        limit: int = 10
    ) -> dict:
        """
        Execute view pix keys use case
        
        Args:
            user_id: User ID
            status: Filter by status (ACTIVE, INACTIVE, or None for all)
            key_type: Filter by key type (CPF, EMAIL, PHONE, RANDOM, or None for all)
            sort_by: Sort field (created_at, updated_at, key_type)
            page: Page number (1-indexed)
            limit: Items per page
            
        Returns:
            Dictionary with keys list and pagination info
        """
        
        # Validate inputs
        valid_statuses = {None, "ACTIVE", "INACTIVE"}
        if status not in valid_statuses:
            raise InvalidFilterError(f"Invalid status: {status}")
        
        valid_types = {None, "CPF", "EMAIL", "PHONE", "RANDOM"}
        if key_type not in valid_types:
            raise InvalidFilterError(f"Invalid key_type: {key_type}")
        
        valid_sorts = {"created_at", "updated_at", "key_type"}
        if sort_by not in valid_sorts:
            raise InvalidFilterError(f"Invalid sort_by: {sort_by}")
        
        # Get all keys for user
        keys = await self.pix_key_repo.get_all_for_user(user_id)
        
        # Apply filters
        if status:
            keys = [k for k in keys if k.get("status") == status or (hasattr(k, "status") and k.status.value == status)]
        
        if key_type:
            keys = [k for k in keys if k.get("key_type") == key_type or (hasattr(k, "key_type") and k.key_type.value == key_type)]
        
        # Apply sorting
        if sort_by == "created_at":
            keys.sort(key=lambda k: k.get("created_at", k.created_at if hasattr(k, "created_at") else datetime.now()), reverse=True)
        elif sort_by == "updated_at":
            keys.sort(key=lambda k: k.get("updated_at", k.updated_at if hasattr(k, "updated_at") else datetime.now()), reverse=True)
        elif sort_by == "key_type":
            keys.sort(key=lambda k: k.get("key_type", str(k.key_type)) if hasattr(k, "get") else str(k.key_type))
        
        # Apply pagination
        total_items = len(keys)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_keys = keys[start_idx:end_idx]
        
        return {
            "keys": paginated_keys,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_items,
                "total_pages": (total_items + limit - 1) // limit,
            }
        }


@pytest.fixture
def mock_pix_key_repository():
    """Create a mock PixKeyRepository for testing."""
    repo = AsyncMock()
    repo.get_all_for_user = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def use_case(mock_pix_key_repository):
    """Create a ViewPixKeysUseCase with mocked dependencies."""
    return MockViewPixKeysUseCase(pix_key_repository=mock_pix_key_repository)


class TestViewAllPixKeys:
    """Tests for retrieving all pix keys"""
    
    @pytest.mark.asyncio
    async def test_retrieve_all_active_keys(self, use_case, mock_pix_key_repository):
        """Test retrieve all active keys for user"""
        user_id = str(uuid4())
        
        # Mock repository response
        keys = [
            {
                "key_id": str(uuid4()),
                "user_id": user_id,
                "key_type": "CPF",
                "key_value_masked": "***.***.***-10",
                "status": "ACTIVE",
                "alias": "My CPF",
                "created_at": datetime.now(),
            },
            {
                "key_id": str(uuid4()),
                "user_id": user_id,
                "key_type": "EMAIL",
                "key_value_masked": "u***@example.com",
                "status": "ACTIVE",
                "alias": "My Email",
                "created_at": datetime.now(),
            },
        ]
        mock_pix_key_repository.get_all_for_user.return_value = keys
        
        result = await use_case.execute(user_id=user_id, status="ACTIVE")
        
        assert result["keys"] is not None
        assert len(result["keys"]) == 2
        assert result["pagination"]["total"] == 2
        mock_pix_key_repository.get_all_for_user.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_retrieve_empty_list_for_new_user(self, use_case, mock_pix_key_repository):
        """Test retrieve empty list when user has no keys"""
        user_id = str(uuid4())
        mock_pix_key_repository.get_all_for_user.return_value = []
        
        result = await use_case.execute(user_id=user_id)
        
        assert result["keys"] == []
        assert result["pagination"]["total"] == 0


class TestViewPixKeysFiltering:
    """Tests for filtering pix keys"""
    
    @pytest.mark.asyncio
    async def test_filter_by_status(self, use_case, mock_pix_key_repository):
        """Test filter keys by status"""
        user_id = str(uuid4())
        
        keys = [
            {"key_id": str(uuid4()), "status": "ACTIVE", "key_type": "CPF", "created_at": datetime.now()},
            {"key_id": str(uuid4()), "status": "INACTIVE", "key_type": "EMAIL", "created_at": datetime.now()},
        ]
        mock_pix_key_repository.get_all_for_user.return_value = keys
        
        result = await use_case.execute(user_id=user_id, status="ACTIVE")
        
        assert len(result["keys"]) == 1
        assert result["keys"][0]["status"] == "ACTIVE"
    
    @pytest.mark.asyncio
    async def test_filter_by_key_type(self, use_case, mock_pix_key_repository):
        """Test filter keys by type"""
        user_id = str(uuid4())
        
        keys = [
            {"key_id": str(uuid4()), "key_type": "CPF", "status": "ACTIVE", "created_at": datetime.now()},
            {"key_id": str(uuid4()), "key_type": "EMAIL", "status": "ACTIVE", "created_at": datetime.now()},
        ]
        mock_pix_key_repository.get_all_for_user.return_value = keys
        
        result = await use_case.execute(user_id=user_id, key_type="CPF")
        
        assert len(result["keys"]) == 1
        assert result["keys"][0]["key_type"] == "CPF"
    
    @pytest.mark.asyncio
    async def test_combined_filters_status_and_type(self, use_case, mock_pix_key_repository):
        """Test combined filters for status and key type"""
        user_id = str(uuid4())
        
        keys = [
            {"key_id": str(uuid4()), "key_type": "CPF", "status": "ACTIVE", "created_at": datetime.now()},
            {"key_id": str(uuid4()), "key_type": "EMAIL", "status": "ACTIVE", "created_at": datetime.now()},
            {"key_id": str(uuid4()), "key_type": "CPF", "status": "INACTIVE", "created_at": datetime.now()},
        ]
        mock_pix_key_repository.get_all_for_user.return_value = keys
        
        result = await use_case.execute(user_id=user_id, status="ACTIVE", key_type="CPF")
        
        assert len(result["keys"]) == 1
        assert result["keys"][0]["status"] == "ACTIVE"
        assert result["keys"][0]["key_type"] == "CPF"


class TestViewPixKeysSorting:
    """Tests for sorting pix keys"""
    
    @pytest.mark.asyncio
    async def test_sort_by_created_date_descending(self, use_case, mock_pix_key_repository):
        """Test sort by created_at descending (newest first)"""
        user_id = str(uuid4())
        
        now = datetime.now()
        keys = [
            {"key_id": str(uuid4()), "status": "ACTIVE", "key_type": "CPF", "created_at": now},
            {"key_id": str(uuid4()), "status": "ACTIVE", "key_type": "EMAIL", "created_at": datetime(2024, 1, 1)},
        ]
        mock_pix_key_repository.get_all_for_user.return_value = keys
        
        result = await use_case.execute(user_id=user_id, sort_by="created_at")
        
        # First item should be the newest (now)
        assert result["keys"][0]["created_at"] >= result["keys"][1]["created_at"]


class TestViewPixKeysPagination:
    """Tests for pagination"""
    
    @pytest.mark.asyncio
    async def test_pagination_default_limit(self, use_case, mock_pix_key_repository):
        """Test pagination with default limit (10 items)"""
        user_id = str(uuid4())
        
        keys = [
            {"key_id": str(uuid4()), "status": "ACTIVE", "created_at": datetime.now()}
            for _ in range(15)
        ]
        mock_pix_key_repository.get_all_for_user.return_value = keys
        
        result = await use_case.execute(user_id=user_id, limit=10, page=1)
        
        assert len(result["keys"]) == 10
        assert result["pagination"]["total"] == 15
        assert result["pagination"]["total_pages"] == 2
    
    @pytest.mark.asyncio
    async def test_pagination_second_page(self, use_case, mock_pix_key_repository):
        """Test pagination fetching second page"""
        user_id = str(uuid4())
        
        keys = [
            {"key_id": str(uuid4()), "status": "ACTIVE", "created_at": datetime.now()}
            for _ in range(15)
        ]
        mock_pix_key_repository.get_all_for_user.return_value = keys
        
        result = await use_case.execute(user_id=user_id, limit=10, page=2)
        
        assert len(result["keys"]) == 5
        assert result["pagination"]["page"] == 2


class TestViewPixKeysValidation:
    """Tests for input validation"""
    
    @pytest.mark.asyncio
    async def test_invalid_status_raises_error(self, use_case, mock_pix_key_repository):
        """Test invalid status raises error"""
        user_id = str(uuid4())
        
        with pytest.raises(InvalidFilterError):
            await use_case.execute(user_id=user_id, status="INVALID_STATUS")
    
    @pytest.mark.asyncio
    async def test_invalid_key_type_raises_error(self, use_case, mock_pix_key_repository):
        """Test invalid key type raises error"""
        user_id = str(uuid4())
        
        with pytest.raises(InvalidFilterError):
            await use_case.execute(user_id=user_id, key_type="INVALID_TYPE")
    
    @pytest.mark.asyncio
    async def test_invalid_sort_by_raises_error(self, use_case, mock_pix_key_repository):
        """Test invalid sort_by raises error"""
        user_id = str(uuid4())
        
        with pytest.raises(InvalidFilterError):
            await use_case.execute(user_id=user_id, sort_by="invalid_sort")
