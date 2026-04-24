"""SQLAlchemy ORM models for database persistence."""
from sqlalchemy import Column, Integer, String, DateTime, Enum, UniqueConstraint, Index, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.db import Base
from src.domain.models import TipoChaveEnum, StatusChaveEnum


class PixKeyModel(Base):
    """Pix key database model."""

    __tablename__ = "pix_keys"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Attributes
    tipo_chave = Column(Enum(TipoChaveEnum), nullable=False)
    valor_chave = Column(String(255), nullable=False)
    conta_id = Column(Integer, nullable=False)
    cliente_id = Column(Integer, nullable=False)
    status = Column(Enum(StatusChaveEnum), default=StatusChaveEnum.CRIADA, nullable=False)

    # Timestamps
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint(
            "cliente_id",
            "tipo_chave",
            "valor_chave",
            name="uq_cliente_tipo_valor",
        ),
        Index("ix_cliente_id_status", "cliente_id", "status"),
        Index("ix_tipo_valor", "tipo_chave", "valor_chave"),
        Index("ix_cliente_id", "cliente_id"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<PixKeyModel(id={self.id}, cliente_id={self.cliente_id}, tipo_chave={self.tipo_chave})>"


class PixKeyAuditModel(Base):
    """Audit trail for Pix key operations."""

    __tablename__ = "pix_key_audits"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key
    pix_key_id = Column(UUID(as_uuid=True), ForeignKey("pix_keys.id"), nullable=False)

    # Attributes
    acao = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE
    resultado = Column(String(20), nullable=False)  # SUCCESS, FAILURE
    detalhes = Column(Text, nullable=True)  # Additional details (error message, etc.)

    # Timestamps
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index("ix_pix_key_id", "pix_key_id"),
        Index("ix_criado_em", "criado_em"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<PixKeyAuditModel(id={self.id}, pix_key_id={self.pix_key_id}, acao={self.acao})>"
