"""Abstract repository interfaces for data access abstraction"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.entities import PixKeyType, PixKeyStatus, PixKeyAuditOperation


class PixKeyRepository(ABC):
    """Abstract repository for PixKey persistence"""
    
    @abstractmethod
    async def create(
        self,
        user_id: UUID,
        key_type: PixKeyType,
        key_value_hash: str,
        key_value_masked: str,
        alias: Optional[str] = None,
        validation_status: str = "VALID"
    ) -> dict:
        """
        Create and persist a new PixKey
        
        Returns:
            Dictionary with created key data including key_id
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, key_id: UUID) -> Optional[dict]:
        """Get PixKey by primary key"""
        pass
    
    @abstractmethod
    async def get_by_hash(self, user_id: UUID, key_hash: str) -> Optional[dict]:
        """Get PixKey by user and key hash (for duplicate detection)"""
        pass
    
    @abstractmethod
    async def get_all_for_user(self, user_id: UUID) -> List[dict]:
        """Get all PixKeys for a user"""
        pass
    
    @abstractmethod
    async def get_for_user_filtered(
        self,
        user_id: UUID,
        status: Optional[PixKeyStatus] = None,
        key_type: Optional[PixKeyType] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[dict], int]:
        """
        Get filtered PixKeys for user with pagination
        
        Returns:
            Tuple of (keys_list, total_count)
        """
        pass
    
    @abstractmethod
    async def count_for_user(self, user_id: UUID) -> int:
        """Count active PixKeys for user"""
        pass
    
    @abstractmethod
    async def update_status(self, key_id: UUID, status: PixKeyStatus) -> Optional[dict]:
        """Update PixKey status"""
        pass
    
    @abstractmethod
    async def update_alias(self, key_id: UUID, alias: Optional[str]) -> Optional[dict]:
        """Update PixKey alias"""
        pass
    
    @abstractmethod
    async def delete(self, key_id: UUID) -> bool:
        """Delete PixKey permanently"""
        pass
    
    @abstractmethod
    async def verify_ownership(self, user_id: UUID, key_id: UUID) -> bool:
        """Verify that user owns the key"""
        pass


class PixKeyAuditRepository(ABC):
    """Abstract repository for PixKey audit trail"""
    
    @abstractmethod
    async def create_audit_log(
        self,
        key_id: UUID,
        user_id: UUID,
        operation: PixKeyAuditOperation,
        status: str,
        details: Optional[dict] = None
    ) -> dict:
        """Create audit log entry"""
        pass
    
    @abstractmethod
    async def get_audit_trail_for_key(self, key_id: UUID, limit: int = 50) -> List[dict]:
        """Get audit trail for specific key"""
        pass
    
    @abstractmethod
    async def get_audit_trail_for_user(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[dict], int]:
        """Get audit trail for user with pagination"""
        pass
