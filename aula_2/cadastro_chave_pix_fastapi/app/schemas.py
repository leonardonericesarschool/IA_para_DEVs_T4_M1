from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class TipoChave(str, Enum):
    """Tipos válidos de chave Pix."""
    CPF = "CPF"
    CNPJ = "CNPJ"
    EMAIL = "EMAIL"
    TELEFONE = "TELEFONE"


class ChavePixCriarRequest(BaseModel):
    """Schema para criar uma nova chave Pix."""
    tipoChave: TipoChave = Field(
        ...,
        description="Tipo da chave Pix",
        examples=["CPF"]
    )
    valorChave: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Valor da chave Pix",
        examples=["12345678901"]
    )
    descricao: str | None = Field(
        default=None,
        max_length=255,
        description="Descrição opcional da chave",
        examples=["Meu email principal"]
    )

    @field_validator("valorChave")
    @classmethod
    def validarValorChave(cls, valor: str) -> str:
        """Valida e normaliza o valor da chave."""
        valor_normalizado = valor.strip()
        if not valor_normalizado:
            raise ValueError("Valor da chave não pode estar vazio")
        return valor_normalizado


class ChavePixAtualizarRequest(BaseModel):
    """Schema para atualizar uma chave Pix."""
    descricao: str | None = Field(
        default=None,
        max_length=255,
        description="Nova descrição da chave",
        examples=["Descrição atualizada"]
    )


class ChavePixResponse(BaseModel):
    """Schema para resposta de operações com chave Pix."""
    id: int = Field(..., description="ID da chave Pix")
    tipoChave: str = Field(..., description="Tipo da chave Pix")
    valorChave: str = Field(..., description="Valor da chave Pix")
    descricao: str | None = Field(None, description="Descrição da chave")
    criadoEm: datetime = Field(..., description="Data de criação")
    atualizadoEm: datetime = Field(..., description="Data da última atualização")

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Schema para resposta paginada."""
    items: list[ChavePixResponse] = Field(..., description="Lista de chaves")
    total: int = Field(..., description="Total de itens")
    page: int = Field(..., description="Página atual")
    limit: int = Field(..., description="Limite de itens por página")
    pages: int = Field(..., description="Total de páginas")


class ErroResponse(BaseModel):
    """Schema para resposta de erro."""
    mensagem: str = Field(..., description="Mensagem de erro")
    detalhes: dict | None = Field(None, description="Detalhes adicionais do erro")
