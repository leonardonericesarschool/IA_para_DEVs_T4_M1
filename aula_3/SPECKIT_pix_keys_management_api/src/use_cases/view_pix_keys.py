"""View Pix Keys use case for listing user's registered keys"""
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime

from src.entities import PixKeyType, PixKeyStatus
from src.exceptions import InvalidFilterError
from src.repositories import PixKeyRepository
from src.config import get_settings


class ViewPixKeysUseCase:
    """
    Use case for viewing/listing user's Pix Keys
    
    Business logic:
    1. Retrieve all keys for user
    2. Apply filters (status, key_type)
    3. Apply sorting
    4. Apply pagination
    5. Return masked keys (never plaintext)
    """
    
    def __init__(self, pix_key_repository: PixKeyRepository):
        self.pix_key_repo = pix_key_repository
        self.settings = get_settings()
    
    async def execute(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        key_type: Optional[str] = None,
        sort_by: str = "created_at",
        page: int = 1,
        limit: int = 10
    ) -> Dict:
        """
        Execute the view pix keys use case
        
        Args:
            user_id: ID of user
            status: Filter by status (ACTIVE, INACTIVE, or None for all)
            key_type: Filter by key type (CPF, EMAIL, PHONE, RANDOM, or None for all)
            sort_by: Sort field (created_at, updated_at, key_type)
            page: Page number (1-indexed)
            limit: Items per page
            
        Returns:
            Dictionary with:
            - keys: List of PixKey dicts with masked values
            - pagination: Dict with page, limit, total, total_pages
            
        Raises:
            InvalidFilterError: Invalid filter parameter
        """
        
        # Validate inputs
        valid_statuses = {None, "ACTIVE", "INACTIVE"}
        if status not in valid_statuses:
            raise InvalidFilterError(f"Invalid status: {status}. Must be ACTIVE, INACTIVE, or None.")
        
        valid_types = {None, "CPF", "EMAIL", "PHONE", "RANDOM"}
        if key_type not in valid_types:
            raise InvalidFilterError(f"Invalid key_type: {key_type}. Must be CPF, EMAIL, PHONE, RANDOM, or None.")
        
        valid_sorts = {"created_at", "updated_at", "key_type"}
        if sort_by not in valid_sorts:
            raise InvalidFilterError(f"Invalid sort_by: {sort_by}. Must be one of: {valid_sorts}")
        
        # Get all keys for user
        keys = await self.pix_key_repo.get_all_for_user(user_id)
        
        # Apply filters
        if status:
            keys = [
                k for k in keys 
                if self._get_status(k) == status
            ]
        
        if key_type:
            keys = [
                k for k in keys 
                if self._get_key_type(k) == key_type
            ]
        
        # Apply sorting
        keys = self._sort_keys(keys, sort_by)
        
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
                "total_pages": (total_items + limit - 1) // limit if total_items > 0 else 0,
            }
        }
    
    def _get_status(self, key: dict) -> str:
        """Extract status from key (handles dict or object)"""
        if isinstance(key, dict):
            return key.get("status")
        return key.status.value if hasattr(key.status, "value") else str(key.status)
    
    def _get_key_type(self, key: dict) -> str:
        """Extract key_type from key (handles dict or object)"""
        if isinstance(key, dict):
            return key.get("key_type")
        return key.key_type.value if hasattr(key.key_type, "value") else str(key.key_type)
    
    def _get_created_at(self, key: dict) -> datetime:
        """Extract created_at from key (handles dict or object)"""
        if isinstance(key, dict):
            return key.get("created_at", datetime.now())
        return key.created_at if hasattr(key, "created_at") else datetime.now()
    
    def _get_updated_at(self, key: dict) -> datetime:
        """Extract updated_at from key (handles dict or object)"""
        if isinstance(key, dict):
            return key.get("updated_at", datetime.now())
        return key.updated_at if hasattr(key, "updated_at") else datetime.now()
    
    def _sort_keys(self, keys: List, sort_by: str) -> List:
        """Sort keys by specified field"""
        if sort_by == "created_at":
            return sorted(keys, key=lambda k: self._get_created_at(k), reverse=True)
        elif sort_by == "updated_at":
            return sorted(keys, key=lambda k: self._get_updated_at(k), reverse=True)
        elif sort_by == "key_type":
            return sorted(keys, key=lambda k: self._get_key_type(k))
        return keys
