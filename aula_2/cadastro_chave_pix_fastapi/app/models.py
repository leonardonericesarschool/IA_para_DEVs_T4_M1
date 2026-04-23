from datetime import datetime, timezone
from sqlalchemy import String, DateTime, UniqueConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ChavePix(Base):
    """
    Modelo para Chave Pix.
    Representa uma chave Pix cadastrada no sistema.
    """
    __tablename__ = "chaves_pix"
    __table_args__ = (
        UniqueConstraint("tipoChave", "valorChave", name="uq_tipo_valor"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipoChave: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Tipo da chave: CPF, CNPJ, EMAIL ou TELEFONE"
    )
    valorChave: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Valor da chave Pix"
    )
    descricao: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Descrição da chave (opcional)"
    )
    criadoEm: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="Data e hora de criação"
    )
    atualizadoEm: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="Data e hora da última atualização"
    )

    def __repr__(self) -> str:
        return f"ChavePix(id={self.id}, tipoChave={self.tipoChave}, valorChave={self.valorChave})"
