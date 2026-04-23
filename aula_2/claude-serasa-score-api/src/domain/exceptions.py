"""
Hierarquia de exceções do domínio.

Princípio: exceções de domínio não devem saber nada sobre HTTP.
A camada de API é responsável por mapear para status codes.
"""


class SerasaScoreBaseError(Exception):
    """Base para todas as exceções da aplicação."""

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


# --- CPF / Validação ---


class InvalidCPFError(SerasaScoreBaseError):
    """CPF com formato ou dígitos verificadores inválidos."""


# --- Score ---


class ScoreNotFoundError(SerasaScoreBaseError):
    """Nenhum registro encontrado para o CPF consultado."""


class ScoreServiceUnavailableError(SerasaScoreBaseError):
    """SERASA API indisponível ou com timeout."""


class ScoreRateLimitError(SerasaScoreBaseError):
    """Limite de consultas atingido (SERASA ou interno)."""


# --- Autenticação / Autorização ---


class UnauthorizedError(SerasaScoreBaseError):
    """Token ausente ou inválido."""


class ForbiddenError(SerasaScoreBaseError):
    """Token válido, mas sem permissão para a operação."""


class TokenExpiredError(UnauthorizedError):
    """JWT expirado."""


# --- Auditoria / Consulta ---


class ConsultaNotFoundError(SerasaScoreBaseError):
    """Consulta não encontrada no histórico."""
