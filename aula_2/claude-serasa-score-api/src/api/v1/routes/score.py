"""
Rotas de consulta de score.

Responsabilidade desta camada: APENAS HTTP.
- Receber e validar request HTTP
- Chamar o service
- Mapear resultado para response schema
- SEM lógica de negócio aqui
"""

from datetime import datetime, timezone

from fastapi import APIRouter, status

from src.core.dependencies import CurrentUserDep, ScoreServiceDep
from src.schemas.score import (
    ErrorResponse,
    FaixaScoreInfo,
    ScoreConsultaRequest,
    ScoreConsultaResponse,
)

router = APIRouter(prefix="/score", tags=["Score de Crédito"])


@router.post(
    "/consultar",
    response_model=ScoreConsultaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Score retornado com sucesso"},
        401: {"model": ErrorResponse, "description": "API Key ausente ou inválida"},
        404: {"model": ErrorResponse, "description": "CPF sem registro no SERASA"},
        422: {"model": ErrorResponse, "description": "CPF com formato inválido"},
        429: {"model": ErrorResponse, "description": "Rate limit atingido"},
        503: {"model": ErrorResponse, "description": "SERASA indisponível"},
    },
    summary="Consultar score de crédito",
    description=(
        "Consulta o score de crédito SERASA para o CPF informado. "
        "Resultados são cacheados por 24h para reduzir chamadas externas. "
        "Requer autenticação via header `X-API-Key`."
    ),
)
async def consultar_score(
    payload: ScoreConsultaRequest,
    service: ScoreServiceDep,
    current_user: CurrentUserDep,
) -> ScoreConsultaResponse:
    result = await service.consultar_score(
        cpf_raw=payload.cpf,
        usuario_id=current_user,
    )

    return ScoreConsultaResponse(
        cpf_masked=result.cpf.masked,
        score=result.score,
        faixa=FaixaScoreInfo.from_faixa(result.faixa),
        consultado_em=result.consultado_em,
        cache_hit=result.cache_hit,
        fonte=result.fonte,
    )


@router.get(
    "/health",
    tags=["Health"],
    summary="Health check do serviço",
    include_in_schema=False,
)
async def health_check() -> dict:
    return {"status": "ok", "timestamp": datetime.now(tz=timezone.utc).isoformat()}
