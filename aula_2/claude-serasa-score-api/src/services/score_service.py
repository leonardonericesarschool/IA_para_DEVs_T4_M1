"""
ScoreService — Use Case de consulta de score.

Esta é a camada de aplicação:
- Orquestra infra (cache + SERASA) sem saber de HTTP
- Aplica regras de negócio (validação de CPF, auditoria)
- Mede latência para observabilidade
- NUNCA loga dados sensíveis completos
"""

import logging
import time
import uuid
from datetime import datetime, timezone

from src.domain.entities import CPF, ConsultaAudit, FaixaScore, ScoreResult
from src.domain.exceptions import InvalidCPFError
from src.infrastructure.cache.score_cache import ScoreCacheRepository
from src.infrastructure.http.serasa_client import SerasaHTTPClient

logger = logging.getLogger(__name__)


class ScoreService:
    """
    Orquestra a consulta de score de crédito.

    Fluxo:
    1. Valida o CPF (Value Object)
    2. Verifica cache Redis
    3. Se cache miss → chama SERASA
    4. Armazena no cache
    5. Registra auditoria (sem PII)
    6. Retorna ScoreResult
    """

    def __init__(
        self,
        serasa_client: SerasaHTTPClient,
        cache: ScoreCacheRepository,
    ) -> None:
        self._serasa = serasa_client
        self._cache = cache

    async def consultar_score(
        self,
        cpf_raw: str,
        usuario_id: str,
    ) -> ScoreResult:
        """
        Consulta score de crédito para um CPF.

        Args:
            cpf_raw: CPF em qualquer formato (só dígitos ou formatado).
            usuario_id: ID do usuário/sistema que fez a requisição (para auditoria).

        Returns:
            ScoreResult com pontuação, faixa e metadados.

        Raises:
            InvalidCPFError: CPF inválido.
            ScoreNotFoundError: CPF sem registro no SERASA.
            ScoreServiceUnavailableError: SERASA indisponível.
        """
        start = time.perf_counter()
        consulta_id = str(uuid.uuid4())

        # 1. Validação: ValueError do Pydantic vira InvalidCPFError aqui
        try:
            cpf = CPF(cpf_raw)
        except InvalidCPFError:
            raise
        except Exception as exc:
            raise InvalidCPFError(f"CPF inválido: {exc}") from exc

        logger.info(
            "Consulta de score iniciada [id=%s, cpf=%s, usuario=%s]",
            consulta_id, cpf.masked, usuario_id,
        )

        # 2. Cache lookup
        cached = await self._cache.get(cpf.value)
        if cached:
            latency = (time.perf_counter() - start) * 1000
            logger.info(
                "Cache HIT [id=%s, cpf=%s, latency=%.1fms]",
                consulta_id, cpf.masked, latency,
            )
            return self._build_result_from_cache(cpf, cached, latency, consulta_id, usuario_id)

        # 3. Cache miss → SERASA
        raw_data = await self._serasa.consultar_score(cpf.value)
        latency = (time.perf_counter() - start) * 1000

        # 4. Gravar no cache (falha silenciosa — não bloqueia resposta)
        await self._cache.set(cpf.value, raw_data)

        # 5. Auditoria
        self._audit(
            consulta_id=consulta_id,
            cpf=cpf,
            usuario_id=usuario_id,
            cache_hit=False,
            latency_ms=latency,
            status="success",
        )

        logger.info(
            "Score obtido do SERASA [id=%s, cpf=%s, score=%d, latency=%.1fms]",
            consulta_id, cpf.masked, raw_data.get("score", 0), latency,
        )

        return ScoreResult(
            cpf=cpf,
            score=raw_data["score"],
            faixa=FaixaScore.from_score(raw_data["score"]),
            consultado_em=datetime.now(tz=timezone.utc),
            fonte="serasa",
            cache_hit=False,
        )

    def _build_result_from_cache(
        self,
        cpf: CPF,
        cached: dict,
        latency_ms: float,
        consulta_id: str,
        usuario_id: str,
    ) -> ScoreResult:
        self._audit(
            consulta_id=consulta_id,
            cpf=cpf,
            usuario_id=usuario_id,
            cache_hit=True,
            latency_ms=latency_ms,
            status="success",
        )
        return ScoreResult(
            cpf=cpf,
            score=cached["score"],
            faixa=FaixaScore.from_score(cached["score"]),
            consultado_em=datetime.now(tz=timezone.utc),
            fonte="serasa",
            cache_hit=True,
        )

    def _audit(
        self,
        *,
        consulta_id: str,
        cpf: CPF,
        usuario_id: str,
        cache_hit: bool,
        latency_ms: float,
        status: str,
        detalhes: dict | None = None,
    ) -> None:
        """
        Registra evento de auditoria.

        Apenas o CPF mascarado é salvo — conformidade com LGPD.
        Em produção, enviar para um sistema de auditoria dedicado (Kafka, DB, etc).
        """
        audit = ConsultaAudit(
            id=consulta_id,
            cpf_masked=cpf.masked,
            usuario_id=usuario_id,
            realizada_em=datetime.now(tz=timezone.utc),
            cache_hit=cache_hit,
            status=status,
            latency_ms=latency_ms,
            detalhes=detalhes or {},
        )
        # TODO: persistir em tabela de auditoria (repo injetado)
        logger.info(
            "AUDIT [id=%s, cpf=%s, usuario=%s, cache_hit=%s, status=%s, latency=%.1fms]",
            audit.id, audit.cpf_masked, audit.usuario_id,
            audit.cache_hit, audit.status, audit.latency_ms,
        )
