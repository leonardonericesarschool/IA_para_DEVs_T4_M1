"""SQLAlchemy database models for Pix Keys"""
from sqlalchemy import Column, String, UUID, DateTime, Boolean, Enum, ForeignKey, JSON, Index, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid as uuid_module
from src.database import Base
from src.entities import PixKeyType, PixKeyStatus, PixKeyValidationStatus, PixKeyAuditOperation


class UserModel(Base):
    """User table - reference to auth layer"""
    __tablename__ = "users"
    
    user_id = Column(UUID, primary_key=True, default=uuid_module.uuid4)
    email = Column(String(254), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pix_keys = relationship("PixKeyModel", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, email={self.email})>"


class PixKeyModel(Base):
    """PixKey table - Pix Key identifiers registered by users"""
    __tablename__ = "pix_keys"
    
    key_id = Column(UUID, primary_key=True, default=uuid_module.uuid4)
    user_id = Column(UUID, ForeignKey("users.user_id"), nullable=False)
    key_type = Column(Enum(PixKeyType), nullable=False)
    key_value_hash = Column(String(255), nullable=False)  # SHA-256 hash
    key_value_masked = Column(String(255), nullable=False)  # Masked display
    status = Column(Enum(PixKeyStatus), nullable=False, default=PixKeyStatus.ACTIVE)
    alias = Column(String(50), nullable=True)
    is_preferred = Column(Boolean, nullable=False, default=False)
    validation_status = Column(Enum(PixKeyValidationStatus), nullable=False, default=PixKeyValidationStatus.VALID)
    validation_error = Column(String(255), nullable=True)
    pix_network_id = Column(String(255), nullable=True)  # External ID from Pix network
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    revalidated_at = Column(DateTime, nullable=True)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'key_value_hash', name='uq_user_key_hash'),
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name='ck_status'),
        CheckConstraint("validation_status IN ('PENDING', 'VALID', 'INVALID')", name='ck_validation_status'),
        CheckConstraint("(is_preferred = false OR status = 'ACTIVE')", name='ck_preferred_must_be_active'),
        Index('ix_user_status', 'user_id', 'status'),
        Index('ix_user_type', 'user_id', 'key_type'),
        Index('ix_key_hash', 'key_value_hash'),
    )
    
    # Relationships
    user = relationship("UserModel", back_populates="pix_keys")
    audit_logs = relationship("PixKeyAuditModel", back_populates="pix_key", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<PixKey(key_id={self.key_id}, user_id={self.user_id}, type={self.key_type.value})>"


class PixKeyAuditModel(Base):
    """PixKey audit table - Immutable audit trail"""
    __tablename__ = "pix_key_audits"
    
    audit_id = Column(UUID, primary_key=True, default=uuid_module.uuid4)
    key_id = Column(UUID, ForeignKey("pix_keys.key_id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.user_id"), nullable=False)
    operation = Column(Enum(PixKeyAuditOperation), nullable=False)
    status = Column(String(20), nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        Index('ix_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_key_timestamp', 'key_id', 'timestamp'),
    )
    
    # Relationships
    pix_key = relationship("PixKeyModel", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return f"<PixKeyAudit(audit_id={self.audit_id}, operation={self.operation.value})>"
