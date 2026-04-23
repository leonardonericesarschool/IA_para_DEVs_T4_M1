from __future__ import annotations

import re
import uuid
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, TypeAdapter, field_validator

TipoChave = Literal["cpf", "cnpj", "email", "telefone", "aleatoria"]

regexSomenteDigitos = re.compile(r"^\d+$")
regexTelefone = re.compile(r"^\+\d{10,15}$")
emailAdapter = TypeAdapter(EmailStr)


def normalizarDigitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


class ChavePixCriarRequest(BaseModel):
    tipoChave: TipoChave = Field(..., description="Tipo da chave Pix")
    valorChave: str = Field(..., min_length=1, max_length=100, description="Valor da chave Pix")
    descricao: str | None = Field(None, max_length=255, description="Descrição opcional")

    @field_validator("valorChave")
    @classmethod
    def validarValorChave(cls, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("valorChave é obrigatório")
        return str(valor).strip()

    @field_validator("tipoChave")
    @classmethod
    def validarTipoChave(cls, valor: str):
        return valor

    @field_validator("descricao")
    @classmethod
    def validarDescricao(cls, valor: str | None):
        if valor is None:
            return None
        texto = str(valor).strip()
        return texto if texto else None

    @field_validator("valorChave")
    @classmethod
    def validarPorTipo(cls, valor: str, info):
        tipoChave = info.data.get("tipoChave")
        if tipoChave in ("cpf", "cnpj"):
            digitos = normalizarDigitos(valor)
            if not regexSomenteDigitos.match(digitos):
                raise ValueError("CPF/CNPJ deve conter apenas números")
            if tipoChave == "cpf" and len(digitos) != 11:
                raise ValueError("CPF deve ter 11 dígitos")
            if tipoChave == "cnpj" and len(digitos) != 14:
                raise ValueError("CNPJ deve ter 14 dígitos")
            return digitos

        if tipoChave == "telefone":
            texto = str(valor).strip()
            if not regexTelefone.match(texto):
                raise ValueError("Telefone deve estar no formato E.164, por exemplo +5511999999999")
            return texto

        if tipoChave == "aleatoria":
            texto = str(valor).strip()
            try:
                uuid.UUID(texto)
            except Exception as exc:
                raise ValueError("Chave aleatória deve ser um UUID válido") from exc
            return texto

        if tipoChave == "email":
            try:
                emailValidado = emailAdapter.validate_python(valor)
            except Exception as exc:
                raise ValueError("Email inválido") from exc
            return str(emailValidado).strip().lower()

        return valor


class ChavePixAtualizarRequest(BaseModel):
    valorChave: str | None = Field(None, min_length=1, max_length=100)
    descricao: str | None = Field(None, max_length=255)

    @field_validator("valorChave")
    @classmethod
    def validarValorChave(cls, valor: str | None):
        if valor is None:
            return None
        texto = str(valor).strip()
        return texto if texto else None

    @field_validator("descricao")
    @classmethod
    def validarDescricao(cls, valor: str | None):
        if valor is None:
            return None
        texto = str(valor).strip()
        return texto if texto else None


class ChavePixResponse(BaseModel):
    id: int
    tipoChave: TipoChave
    valorChave: str
    descricao: str | None
    criadoEm: str


class ListarChavesPixQuery(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(50, ge=1, le=200)
    tipoChave: TipoChave | None = None
    valorChave: str | None = None

    @field_validator("valorChave")
    @classmethod
    def validarValorChave(cls, valor: str | None):
        if valor is None:
            return None
        texto = str(valor).strip()
        return texto if texto else None


class PaginacaoChavesPixResponse(BaseModel):
    itens: list[ChavePixResponse]
    page: int
    limit: int
    total: int


class MensagemResponse(BaseModel):
    mensagem: str
