"""
Domain entities e value objects.

Regra: nenhum import de ORM, HTTP ou frameworks aqui.
Entidades são Python puro — testáveis sem infraestrutura.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class FaixaScore(str, Enum):
    """Classificação do score conforme faixas SERASA."""

    MUITO_RUIM = "muito_ruim"      # 0–300
    RUIM = "ruim"                  # 301–500
    REGULAR = "regular"            # 501–700
    BOM = "bom"                    # 701–900
    MUITO_BOM = "muito_bom"        # 901–1000

    @classmethod
    def from_score(cls, score: int) -> "FaixaScore":
        if score <= 300:
            return cls.MUITO_RUIM
        if score <= 500:
            return cls.RUIM
        if score <= 700:
            return cls.REGULAR
        if score <= 900:
            return cls.BOM
        return cls.MUITO_BOM


@dataclass(frozen=True)
class CPF:
    """
    Value Object para CPF.

    Imutável e auto-validado na criação. Nunca armazena formatado —
    apenas os 11 dígitos. A formatação é responsabilidade da camada de apresentação.
    """

    value: str

    def __post_init__(self) -> None:
        digits = "".join(filter(str.isdigit, self.value))
        if len(digits) != 11:
            from src.domain.exceptions import InvalidCPFError
            raise InvalidCPFError(f"CPF deve ter 11 dígitos, recebido: {len(digits)}")

        if not self._validate_check_digits(digits):
            from src.domain.exceptions import InvalidCPFError
            raise InvalidCPFError("Dígitos verificadores do CPF inválidos")

        # Sobrescreve com apenas dígitos (normalizado)
        object.__setattr__(self, "value", digits)

    @staticmethod
    def _validate_check_digits(digits: str) -> bool:
        """Algoritmo oficial de validação dos dígitos verificadores."""
        if len(set(digits)) == 1:
            return False  # 111.111.111-11 etc. são inválidos

        def calc_digit(partial: str, weights: range) -> int:
            total = sum(int(d) * w for d, w in zip(partial, weights))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder

        d1 = calc_digit(digits[:9], range(10, 1, -1))
        d2 = calc_digit(digits[:10], range(11, 1, -1))
        return digits[9] == str(d1) and digits[10] == str(d2)

    @property
    def masked(self) -> str:
        """Retorna CPF mascarado para logs: ***.***.<últimos 3>-<últimos 2>."""
        return f"***.***.{self.value[6:9]}-{self.value[9:]}"

    @property
    def formatted(self) -> str:
        """Retorna CPF formatado: 123.456.789-00."""
        v = self.value
        return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"

    def __str__(self) -> str:
        return self.masked  # Seguro por padrão em logs/repr


@dataclass
class ScoreResult:
    """Resultado de uma consulta de score."""

    cpf: CPF
    score: int
    faixa: FaixaScore
    consultado_em: datetime
    fonte: str = "serasa"
    cache_hit: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 1000:
            raise ValueError(f"Score deve estar entre 0 e 1000, recebido: {self.score}")
        self.faixa = FaixaScore.from_score(self.score)


@dataclass
class ConsultaAudit:
    """Registro de auditoria de uma consulta (sem PII sensível)."""

    id: str
    cpf_masked: str
    usuario_id: str
    realizada_em: datetime
    cache_hit: bool
    status: str  # "success" | "not_found" | "error"
    latency_ms: float = 0.0
    detalhes: dict = field(default_factory=dict)
