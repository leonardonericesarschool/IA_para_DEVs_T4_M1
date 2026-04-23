"""
Cache Redis para resultados de score.

Regras obrigatórias:
- TTL em TODAS as chaves (nunca cache permanente)
- Chaves nunca contêm CPF completo
- Falha de cache = fallback para SERASA, nunca erro 500
"""

import hashlib
import json
import logging
from datetime import datetime, timezone

import redis.asyncio as aioredis

from src.core.config import Settings

logger = logging.getLogger(__name__)

# Prefixo para namespace e facilitar SCAN em produção
_KEY_PREFIX = "serasa:score:"


def _cache_key(cpf_digits: str) -> str:
    """
    Gera chave de cache sem expor o CPF.

    Usa SHA-256 do CPF como chave — não reversível, mas determinístico.
    """
    digest = hashlib.sha256(cpf_digits.encode()).hexdigest()[:16]
    return f"{_KEY_PREFIX}{digest}"


class ScoreCacheRepository:
    """Repositório de cache para scores no Redis."""

    def __init__(self, redis: aioredis.Redis, settings: Settings) -> None:
        self._redis = redis
        self._ttl = settings.score_cache_ttl_seconds

    async def get(self, cpf_digits: str) -> dict | None:
        """
        Busca score em cache.

        Returns:
            Dict com dados do score ou None se cache miss / erro.
        """
        key = _cache_key(cpf_digits)
        try:
            raw = await self._redis.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            # Falha de cache nunca deve derrubar a aplicação
            logger.warning("Falha ao ler cache Redis (key=%s): %s", key, exc)
            return None

    async def set(self, cpf_digits: str, data: dict) -> bool:
        """
        Armazena score em cache com TTL obrigatório.

        Returns:
            True se gravado com sucesso.
        """
        key = _cache_key(cpf_digits)
        try:
            payload = {
                **data,
                "cached_at": datetime.now(tz=timezone.utc).isoformat(),
            }
            await self._redis.setex(key, self._ttl, json.dumps(payload))
            logger.debug("Score armazenado em cache (key=%s, ttl=%ds)", key, self._ttl)
            return True
        except Exception as exc:
            logger.warning("Falha ao gravar cache Redis (key=%s): %s", key, exc)
            return False

    async def invalidate(self, cpf_digits: str) -> bool:
        """Remove o cache de um CPF específico (ex: após atualização)."""
        key = _cache_key(cpf_digits)
        try:
            deleted = await self._redis.delete(key)
            return deleted > 0
        except Exception as exc:
            logger.warning("Falha ao invalidar cache (key=%s): %s", key, exc)
            return False

    async def health_check(self) -> bool:
        """Verifica conectividade com Redis."""
        try:
            return await self._redis.ping()
        except Exception:
            return False
