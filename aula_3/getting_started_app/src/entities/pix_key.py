"""PixKey domain entity - Core business logic"""
from uuid import UUID
from datetime import datetime
from typing import Optional
from src.entities import PixKeyType, PixKeyStatus, PixKeyValidationStatus
from src.exceptions import InvalidStatusTransitionError


class PixKey:
    """
    PixKey domain entity representing a single Pix Key registered for a user
    
    Encapsulates business logic and rules for Pix Keys:
    - Status transitions (ACTIVE ↔ INACTIVE)
    - Validation status tracking
    - Data masking for secure display
    """
    
    def __init__(
        self,
        key_id: UUID,
        user_id: UUID,
        key_type: PixKeyType,
        key_value_hash: str,
        key_value_masked: str,
        status: PixKeyStatus = PixKeyStatus.ACTIVE,
        alias: Optional[str] = None,
        is_preferred: bool = False,
        validation_status: PixKeyValidationStatus = PixKeyValidationStatus.VALID,
        validation_error: Optional[str] = None,
        pix_network_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        revalidated_at: Optional[datetime] = None
    ):
        self.key_id = key_id
        self.user_id = user_id
        self.key_type = key_type
        self.key_value_hash = key_value_hash
        self.key_value_masked = key_value_masked
        self.status = status
        self.alias = alias
        self.is_preferred = is_preferred
        self.validation_status = validation_status
        self.validation_error = validation_error
        self.pix_network_id = pix_network_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.revalidated_at = revalidated_at
    
    def deactivate(self) -> None:
        """
        Deactivate this Pix Key
        
        Business rules:
        - Can only deactivate ACTIVE keys
        - Reset is_preferred if it was set
        - Update timestamp
        
        Raises:
            InvalidStatusTransitionError: if key is not ACTIVE
        """
        if self.status != PixKeyStatus.ACTIVE:
            raise InvalidStatusTransitionError(
                current_status=self.status.value,
                attempted_status=PixKeyStatus.INACTIVE.value
            )
        
        self.status = PixKeyStatus.INACTIVE
        self.is_preferred = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """
        Activate/reactivate this Pix Key
        
        Business rules:
        - Can only activate INACTIVE keys
        - Update timestamp
        
        Raises:
            InvalidStatusTransitionError: if key is not INACTIVE
        """
        if self.status != PixKeyStatus.INACTIVE:
            raise InvalidStatusTransitionError(
                current_status=self.status.value,
                attempted_status=PixKeyStatus.ACTIVE.value
            )
        
        self.status = PixKeyStatus.ACTIVE
        self.updated_at = datetime.utcnow()
    
    def update_alias(self, new_alias: Optional[str]) -> None:
        """Update the alias for this key"""
        if new_alias and len(new_alias) > 50:
            raise ValueError("Alias must be 50 characters or less")
        self.alias = new_alias
        self.updated_at = datetime.utcnow()
    
    def mark_as_preferred(self) -> None:
        """Mark this key as preferred for notifications"""
        if self.status != PixKeyStatus.ACTIVE:
            raise ValueError("Only active keys can be marked as preferred")
        self.is_preferred = True
        self.updated_at = datetime.utcnow()
    
    def unmark_as_preferred(self) -> None:
        """Unmark this key from being preferred"""
        self.is_preferred = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_hash: bool = False) -> dict:
        """
        Convert entity to dictionary for API responses
        
        Args:
            include_hash: Whether to include the key_value_hash (usually False for API)
        """
        data = {
            "key_id": str(self.key_id),
            "user_id": str(self.user_id),
            "key_type": self.key_type.value,
            "key_value_masked": self.key_value_masked,
            "status": self.status.value,
            "alias": self.alias,
            "is_preferred": self.is_preferred,
            "validation_status": self.validation_status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        
        if include_hash:
            data["key_value_hash"] = self.key_value_hash
        
        if self.validation_error:
            data["validation_error"] = self.validation_error
        
        if self.pix_network_id:
            data["pix_network_id"] = self.pix_network_id
        
        if self.revalidated_at:
            data["revalidated_at"] = self.revalidated_at.isoformat()
        
        return data
    
    def __repr__(self) -> str:
        return (
            f"<PixKey(key_id={self.key_id}, user_id={self.user_id}, "
            f"type={self.key_type.value}, status={self.status.value})>"
        )
