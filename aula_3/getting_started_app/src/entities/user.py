"""User entity reference from authentication layer"""
from uuid import UUID
from datetime import datetime
from typing import Optional


class User:
    """
    User entity - Reference to user from authentication layer
    
    This is a reference/value object representing an authenticated user.
    The actual user creation and management is handled by the auth layer.
    This feature only references users by their user_id.
    """
    
    def __init__(
        self,
        user_id: UUID,
        email: str,
        phone: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.user_id = user_id
        self.email = email
        self.phone = phone
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, email={self.email})>"
