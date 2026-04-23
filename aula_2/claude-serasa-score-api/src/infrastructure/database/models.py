"""
Modelos ORM SQLAlchemy — camada de persistência.

Regra: models ORM nunca saem desta camada.
A camada de API recebe apenas schemas Pydantic.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


class Base(DeclarativeBase):
    pass


class ConsultaAuditModel(Base):
    """
    Registro de auditoria de cada consulta realizada.

    LGPD: CPF armazenado apenas mascarado. Nunca o valor completo.
    """

    __tablename__ = "consultas_auditoria"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    cpf_masked: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    cpf_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True,
        comment="SHA-256 do CPF — para busca sem expor o dado"
    )
    usuario_id: Mapped[str] = mapped_column(String(100), nullable=False)
    realizada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success|not_found|error
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    detalhes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_consultas_cpf_hash_data", "cpf_hash", "realizada_em"),
        Index("ix_consultas_usuario_data", "usuario_id", "realizada_em"),
    )


class ApiKeyModel(Base):
    """
    Chaves de API para autenticação dos clientes.

    A chave é armazenada como hash bcrypt — nunca em texto plano.
    """

    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    key_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    usuario_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    expira_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ultimo_uso_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
