"""PixKey Audit entity - Immutable audit trail"""
from uuid import UUID
from datetime import datetime
from typing import Optional, Any, Dict
from src.entities import PixKeyAuditOperation


class PixKeyAudit:
    """
    PixKeyAudit entity - Immutable record of operations on Pix Keys
    
    Used for compliance, debugging, and audit trail requirements.
    All audit records are immutable once created.
    """
    
    def __init__(
        self,
        audit_id: UUID,
        key_id: UUID,
        user_id: UUID,
        operation: PixKeyAuditOperation,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        self.audit_id = audit_id
        self.key_id = key_id
        self.user_id = user_id
        self.operation = operation
        self.status = status
        self.details = details or {}
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "audit_id": str(self.audit_id),
            "key_id": str(self.key_id),
            "user_id": str(self.user_id),
            "operation": self.operation.value,
            "status": self.status,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
    
    def __repr__(self) -> str:
        return (
            f"<PixKeyAudit(audit_id={self.audit_id}, key_id={self.key_id}, "
            f"operation={self.operation.value}, timestamp={self.timestamp})>"
        )
