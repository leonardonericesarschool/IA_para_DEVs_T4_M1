from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ChavePix(Base):
    __tablename__ = "chaves_pix"
    __table_args__ = (UniqueConstraint("tipoChave", "valorChave", name="uq_tipo_valor"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipoChave: Mapped[str] = mapped_column(String(20), nullable=False)
    valorChave: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    criadoEm: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: dt.datetime.now(tz=dt.timezone.utc),
    )
