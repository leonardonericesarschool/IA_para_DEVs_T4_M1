"""
Handlers de exceções para a API.

Mapeia exceções de domínio → respostas HTTP padronizadas.
Regra: a camada de domínio não sabe de HTTP; este arquivo é a ponte.
"""

import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    ForbiddenError,
    InvalidCPFError,
    ScoreNotFoundError,
    ScoreRateLimitError,
    ScoreServiceUnavailableError,
    TokenExpiredError,
    UnauthorizedError,
)

logger = logging.getLogger(__name__)


def _error_response(
    request: Request,
    status_code: int,
    error: str,
    message: str,
    details: dict | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error,
            "message": message,
            "request_id": request_id,
            "details": details,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registra todos os handlers de exceção na instância FastAPI."""

    @app.exception_handler(InvalidCPFError)
    async def handle_invalid_cpf(request: Request, exc: InvalidCPFError) -> JSONResponse:
        return _error_response(request, 422, "invalid_cpf", exc.message, exc.details)

    @app.exception_handler(ScoreNotFoundError)
    async def handle_not_found(request: Request, exc: ScoreNotFoundError) -> JSONResponse:
        return _error_response(request, 404, "score_not_found", exc.message, exc.details)

    @app.exception_handler(ScoreRateLimitError)
    async def handle_rate_limit(request: Request, exc: ScoreRateLimitError) -> JSONResponse:
        response = _error_response(request, 429, "rate_limit_exceeded", exc.message, exc.details)
        retry_after = exc.details.get("retry_after_seconds", 60)
        response.headers["Retry-After"] = str(retry_after)
        return response

    @app.exception_handler(ScoreServiceUnavailableError)
    async def handle_service_unavailable(
        request: Request, exc: ScoreServiceUnavailableError
    ) -> JSONResponse:
        logger.error("SERASA indisponível: %s", exc.message)
        return _error_response(
            request, 503, "service_unavailable",
            "Serviço SERASA temporariamente indisponível. Tente novamente em instantes.",
            exc.details,
        )

    @app.exception_handler(TokenExpiredError)
    async def handle_token_expired(request: Request, exc: TokenExpiredError) -> JSONResponse:
        return _error_response(request, 401, "token_expired", "Token expirado. Renove seu acesso.")

    @app.exception_handler(UnauthorizedError)
    async def handle_unauthorized(request: Request, exc: UnauthorizedError) -> JSONResponse:
        return _error_response(request, 401, "unauthorized", exc.message)

    @app.exception_handler(ForbiddenError)
    async def handle_forbidden(request: Request, exc: ForbiddenError) -> JSONResponse:
        return _error_response(request, 403, "forbidden", exc.message)

    @app.exception_handler(Exception)
    async def handle_generic(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erro não tratado na request %s", request.url)
        return _error_response(
            request, 500, "internal_error",
            "Erro interno. Nossa equipe foi notificada.",
        )
