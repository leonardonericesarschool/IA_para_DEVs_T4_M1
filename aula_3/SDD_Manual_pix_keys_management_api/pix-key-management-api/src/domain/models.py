"""Domain models for Pix Key management."""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class TipoChaveEnum(str, Enum):
    """Enum for Pix key types."""

    CPF = "CPF"
    CNPJ = "CNPJ"
    EMAIL = "EMAIL"
    TELEFONE = "TELEFONE"


class StatusChaveEnum(str, Enum):
    """Enum for Pix key status."""

    CRIADA = "CRIADA"
    CONFIRMADA = "CONFIRMADA"
    DELETADA = "DELETADA"


@dataclass
class PixKey:
    """Pix key domain entity."""

    id: UUID | None
    tipo_chave: TipoChaveEnum | str
    valor_chave: str
    conta_id: int
    cliente_id: int
    status: StatusChaveEnum | str = StatusChaveEnum.CRIADA
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None

    def dict(self) -> dict:
        """Convert to dictionary for ORM."""
        return {
            "id": self.id,
            "tipo_chave": self.tipo_chave,
            "valor_chave": self.valor_chave,
            "conta_id": self.conta_id,
            "cliente_id": self.cliente_id,
            "status": self.status,
            "criado_em": self.criado_em,
            "atualizado_em": self.atualizado_em,
        }
