"""
Repositório de auditoria — persiste registros de consulta no PostgreSQL.

Protocolo + implementação concreta: permite trocar o storage sem alterar o service.
"""

import hashlib
import json
import logging
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import ConsultaAudit
from src.infrastructure.database.models import ConsultaAuditModel

logger = logging.getLogger(__name__)


class AuditRepository(Protocol):
    """Abstração — o ScoreService depende disso, não da implementação concreta."""

    async def salvar(self, audit: ConsultaAudit) -> None: ...

    async def listar_por_usuario(
        self, usuario_id: str, page: int, page_size: int
    ) -> tuple[list[ConsultaAudit], int]: ...


class SQLAuditRepository:
    """Implementação PostgreSQL do AuditRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def salvar(self, audit: ConsultaAudit) -> None:
        """
        Persiste registro de auditoria.

        cpf_hash: SHA-256 do CPF normalizado (para busca futura sem expor PII).
        detalhes: serializado como JSON string.
        """
        # Extrair CPF real do masked para gerar hash
        # O masked é "***.***.XXX-YY" — usamos o hash do CPF digits via audit.detalhes
        cpf_hash = audit.detalhes.get("cpf_hash", "unknown")

        record = ConsultaAuditModel(
            id=audit.id,
            cpf_masked=audit.cpf_masked,
            cpf_hash=cpf_hash,
            usuario_id=audit.usuario_id,
            realizada_em=audit.realizada_em,
            cache_hit=audit.cache_hit,
            status=audit.status,
            latency_ms=audit.latency_ms,
            detalhes=json.dumps(audit.detalhes) if audit.detalhes else None,
        )
        self._db.add(record)
        # O commit é feito pelo middleware de session (get_db)

    async def listar_por_usuario(
        self, usuario_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[ConsultaAudit], int]:
        offset = (page - 1) * page_size

        # Total
        count_result = await self._db.execute(
            select(ConsultaAuditModel)
            .where(ConsultaAuditModel.usuario_id == usuario_id)
        )
        all_records = count_result.scalars().all()
        total = len(all_records)

        # Paginado
        result = await self._db.execute(
            select(ConsultaAuditModel)
            .where(ConsultaAuditModel.usuario_id == usuario_id)
            .order_by(ConsultaAuditModel.realizada_em.desc())
            .offset(offset)
            .limit(page_size)
        )
        records = result.scalars().all()

        audits = [
            ConsultaAudit(
                id=r.id,
                cpf_masked=r.cpf_masked,
                usuario_id=r.usuario_id,
                realizada_em=r.realizada_em,
                cache_hit=r.cache_hit,
                status=r.status,
                latency_ms=r.latency_ms,
                detalhes=json.loads(r.detalhes) if r.detalhes else {},
            )
            for r in records
        ]
        return audits, total
