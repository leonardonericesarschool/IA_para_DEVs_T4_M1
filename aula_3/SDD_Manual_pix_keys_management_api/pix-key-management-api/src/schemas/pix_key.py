"""Pydantic schemas for API requests and responses."""
from enum import Enum
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


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


class CriarChavePixRequest(BaseModel):
    """Request to create a Pix key."""

    tipo_chave: TipoChaveEnum = Field(..., description="Tipo da chave Pix")
    valor_chave: str = Field(..., description="Valor da chave Pix", min_length=1, max_length=255)
    conta_id: int = Field(..., description="ID da conta", gt=0)
    cliente_id: int = Field(..., description="ID do cliente", gt=0)


class ChavePixResponse(BaseModel):
    """Response with Pix key details."""

    id: UUID = Field(..., description="ID único da chave")
    tipo_chave: str = Field(..., description="Tipo da chave")
    valor_chave: str = Field(..., description="Valor da chave")
    conta_id: int = Field(..., description="ID da conta")
    cliente_id: int = Field(..., description="ID do cliente")
    status: str = Field(..., description="Status da chave")
    criado_em: datetime = Field(..., description="Data de criação")

    model_config = ConfigDict(from_attributes=True)


class ListaChavesResponse(BaseModel):
    """Response with paginated list of Pix keys."""

    items: list[ChavePixResponse] = Field(..., description="Lista de chaves")
    total: int = Field(..., description="Total de itens", ge=0)
    page: int = Field(..., description="Página atual", ge=1)
    limit: int = Field(..., description="Itens por página", ge=1)


class ErrorResponse(BaseModel):
    """Error response."""

    code: str = Field(..., description="Código de erro")
    message: str = Field(..., description="Mensagem de erro")
