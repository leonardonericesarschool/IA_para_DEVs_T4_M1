"""
Schemas Pydantic para request/response da API.

Regra: nunca expor entidades de domínio ou models ORM diretamente nas rotas.
Sempre usar schemas explícitos com response_model.
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from src.domain.entities import FaixaScore


# ── Request ──────────────────────────────────────────────────────────────────


class ScoreConsultaRequest(BaseModel):
    """Payload para consulta de score."""

    cpf: str = Field(
        ...,
        description="CPF do titular (aceita formatado ou apenas dígitos)",
        examples=["123.456.789-09", "12345678909"],
    )

    @field_validator("cpf")
    @classmethod
    def normalizar_cpf(cls, v: str) -> str:
        """Remove máscaras — o Value Object faz a validação real."""
        return "".join(filter(str.isdigit, v))

    @model_validator(mode="after")
    def validar_tamanho_cpf(self) -> "ScoreConsultaRequest":
        if len(self.cpf) != 11:
            raise ValueError("CPF deve conter exatamente 11 dígitos")
        return self


# ── Response ─────────────────────────────────────────────────────────────────


class FaixaScoreInfo(BaseModel):
    """Detalhes sobre a faixa do score."""

    codigo: FaixaScore
    descricao: str
    range_minimo: int
    range_maximo: int

    @classmethod
    def from_faixa(cls, faixa: FaixaScore) -> "FaixaScoreInfo":
        _mapa = {
            FaixaScore.MUITO_RUIM: ("Muito Ruim", 0, 300),
            FaixaScore.RUIM: ("Ruim", 301, 500),
            FaixaScore.REGULAR: ("Regular", 501, 700),
            FaixaScore.BOM: ("Bom", 701, 900),
            FaixaScore.MUITO_BOM: ("Muito Bom", 901, 1000),
        }
        descricao, min_, max_ = _mapa[faixa]
        return cls(codigo=faixa, descricao=descricao, range_minimo=min_, range_maximo=max_)


class ScoreConsultaResponse(BaseModel):
    """Resposta de uma consulta de score bem-sucedida."""

    # CPF mascarado — nunca retornar completo na API
    cpf_masked: str = Field(..., description="CPF mascarado para exibição")
    score: int = Field(..., ge=0, le=1000, description="Pontuação de crédito (0–1000)")
    faixa: FaixaScoreInfo
    consultado_em: datetime
    cache_hit: bool = Field(..., description="Indica se veio do cache Redis")
    fonte: str = Field(default="serasa")

    model_config = {"json_schema_extra": {
        "example": {
            "cpf_masked": "***.***789-09",
            "score": 750,
            "faixa": {
                "codigo": "bom",
                "descricao": "Bom",
                "range_minimo": 701,
                "range_maximo": 900,
            },
            "consultado_em": "2024-01-15T10:30:00Z",
            "cache_hit": False,
            "fonte": "serasa",
        }
    }}


# ── Auth ─────────────────────────────────────────────────────────────────────


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Segundos até expiração do access token")


class LoginRequest(BaseModel):
    api_key: str = Field(..., min_length=32, description="Chave de API gerada no portal")


# ── Audit / Histórico ─────────────────────────────────────────────────────────


class ConsultaAuditResponse(BaseModel):
    id: str
    cpf_masked: str
    realizada_em: datetime
    cache_hit: bool
    status: str
    latency_ms: float


class HistoricoConsultasResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ConsultaAuditResponse]


# ── Erros ─────────────────────────────────────────────────────────────────────


class ErrorResponse(BaseModel):
    """Schema padronizado para erros (RFC 7807-like)."""

    error: str
    message: str
    request_id: str | None = None
    details: dict | None = None
