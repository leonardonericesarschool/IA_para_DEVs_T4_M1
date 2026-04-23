"""
Rotas de histórico de consultas (auditoria).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import CurrentUserDep
from src.infrastructure.database.session import get_db
from src.repositories.audit_repository import SQLAuditRepository
from src.schemas.score import ConsultaAuditResponse, HistoricoConsultasResponse

router = APIRouter(prefix="/historico", tags=["Histórico de Consultas"])


@router.get(
    "/",
    response_model=HistoricoConsultasResponse,
    summary="Listar histórico de consultas",
    description=(
        "Retorna o histórico de consultas realizadas pelo usuário autenticado. "
        "CPFs são exibidos apenas mascarados."
    ),
)
async def listar_historico(
    current_user: CurrentUserDep,
    page: int = Query(default=1, ge=1, description="Número da página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    db: AsyncSession = Depends(get_db),
) -> HistoricoConsultasResponse:
    repo = SQLAuditRepository(db=db)
    audits, total = await repo.listar_por_usuario(
        usuario_id=current_user,
        page=page,
        page_size=page_size,
    )

    return HistoricoConsultasResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[
            ConsultaAuditResponse(
                id=a.id,
                cpf_masked=a.cpf_masked,
                realizada_em=a.realizada_em,
                cache_hit=a.cache_hit,
                status=a.status,
                latency_ms=a.latency_ms,
            )
            for a in audits
        ],
    )
