"""
Dependency injection para FastAPI.

Centraliza a criação de dependências reutilizáveis.
Todas as rotas recebem o que precisam via Depends() — sem instanciar diretamente.
"""

import logging
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from src.core.config import Settings, get_settings
from src.infrastructure.cache.score_cache import ScoreCacheRepository
from src.infrastructure.http.serasa_client import SerasaHTTPClient
from src.services.score_service import ScoreService

logger = logging.getLogger(__name__)

# ── Settings ──────────────────────────────────────────────────────────────────


def get_settings_dep() -> Settings:
    return get_settings()


SettingsDep = Annotated[Settings, Depends(get_settings_dep)]


# ── Redis ─────────────────────────────────────────────────────────────────────


async def get_redis(settings: SettingsDep) -> aioredis.Redis:
    """Redis client com connection pool."""
    return aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
    )


RedisDep = Annotated[aioredis.Redis, Depends(get_redis)]


# ── Repositórios / Infraestrutura ─────────────────────────────────────────────


async def get_score_cache(
    redis: RedisDep,
    settings: SettingsDep,
) -> ScoreCacheRepository:
    return ScoreCacheRepository(redis=redis, settings=settings)


async def get_serasa_client(settings: SettingsDep) -> SerasaHTTPClient:
    return SerasaHTTPClient(settings=settings)


# ── Services ──────────────────────────────────────────────────────────────────


async def get_score_service(
    serasa_client: Annotated[SerasaHTTPClient, Depends(get_serasa_client)],
    cache: Annotated[ScoreCacheRepository, Depends(get_score_cache)],
) -> ScoreService:
    return ScoreService(serasa_client=serasa_client, cache=cache)


ScoreServiceDep = Annotated[ScoreService, Depends(get_score_service)]


# ── Autenticação via API Key ───────────────────────────────────────────────────

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
    api_key: Annotated[str | None, Security(_api_key_header)],
    settings: SettingsDep,
) -> str:
    """
    Valida a API key e retorna o ID do usuário/sistema.

    Em produção, buscar no banco de dados. Aqui usamos uma validação
    simples contra a settings para demonstração.

    Returns:
        user_id (string) para uso em auditoria.

    Raises:
        HTTPException 401 se a key estiver ausente ou inválida.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key ausente. Use o header X-API-Key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # TODO: buscar no banco — validar hash, verificar status ativo, retornar user_id
    # Por ora, valida contra a chave da config (apenas para demo/dev)
    if api_key != settings.serasa_api_key:
        logger.warning("Tentativa de acesso com API key inválida")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida ou revogada.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return "system"  # Em produção: retornar user_id real do banco


CurrentUserDep = Annotated[str, Depends(get_current_user)]
