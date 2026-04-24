"""FastAPI routes for Pix key management."""
from uuid import UUID
from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.schemas.pix_key import (
    CriarChavePixRequest,
    ChavePixResponse,
    ListaChavesResponse,
    ErrorResponse,
)
from src.services.pix_key_service import PixKeyService
from src.repositories.pix_key_repository import PixKeyRepository
from src.core.exceptions import PixKeyException

logger = getLogger(__name__)

router = APIRouter(prefix="/pix-keys", tags=["pix-keys"])


async def get_pix_key_service(db: AsyncSession = Depends(get_db)) -> PixKeyService:
    """Dependency injection for PixKeyService.

    Args:
        db: Database session

    Returns:
        PixKeyService instance
    """
    repo = PixKeyRepository(db)
    return PixKeyService(repo)


@router.post(
    "",
    response_model=ChavePixResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validação falhou"},
        409: {"model": ErrorResponse, "description": "Chave já existe"},
    },
)
async def criar_chave(
    request: CriarChavePixRequest,
    service: PixKeyService = Depends(get_pix_key_service),
) -> ChavePixResponse:
    """Create a new Pix key.

    Args:
        request: Create Pix key request with type, value, and account/client IDs
        service: PixKeyService dependency

    Returns:
        Created Pix key with ID and timestamps

    Raises:
        HTTPException: 400 if validation fails, 409 if key already exists
    """
    try:
        chave = await service.criar_chave(
            tipo_chave=request.tipo_chave.value,
            valor_chave=request.valor_chave,
            conta_id=request.conta_id,
            cliente_id=request.cliente_id,
        )
        return ChavePixResponse.model_validate(chave)
    except PixKeyException as e:
        logger.error(f"Erro ao criar chave: {e.message}", extra={"code": e.code})
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/{chave_id}",
    response_model=ChavePixResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Chave não encontrada"},
    },
)
async def consultar_chave(
    chave_id: UUID,
    service: PixKeyService = Depends(get_pix_key_service),
) -> ChavePixResponse:
    """Get a Pix key by ID.

    Args:
        chave_id: Pix key ID
        service: PixKeyService dependency

    Returns:
        Pix key details

    Raises:
        HTTPException: 404 if key not found
    """
    chave = await service.get_chave(chave_id)

    if not chave:
        logger.warning(f"Chave não encontrada", extra={"chave_id": str(chave_id)})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chave Pix não encontrada",
        )

    return ChavePixResponse.model_validate(chave)


@router.get(
    "/cliente/{cliente_id}",
    response_model=ListaChavesResponse,
)
async def listar_chaves_cliente(
    cliente_id: int,
    skip: int = 0,
    limit: int = 10,
    service: PixKeyService = Depends(get_pix_key_service),
) -> ListaChavesResponse:
    """List Pix keys for a client with pagination.

    Args:
        cliente_id: Client ID
        skip: Pagination offset (default 0)
        limit: Items per page (default 10, max 100)
        service: PixKeyService dependency

    Returns:
        Paginated list of Pix keys
    """
    # Validate pagination params
    skip = max(0, skip)
    limit = min(100, max(1, limit))

    chaves, total = await service.listar_por_cliente(cliente_id, skip, limit)

    page = (skip // limit) + 1 if limit > 0 else 1

    return ListaChavesResponse(
        items=[ChavePixResponse.model_validate(c) for c in chaves],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/conta/{conta_id}",
    response_model=ListaChavesResponse,
)
async def listar_chaves_conta(
    conta_id: int,
    skip: int = 0,
    limit: int = 10,
    service: PixKeyService = Depends(get_pix_key_service),
) -> ListaChavesResponse:
    """List Pix keys for an account with pagination.

    Args:
        conta_id: Account ID
        skip: Pagination offset (default 0)
        limit: Items per page (default 10, max 100)
        service: PixKeyService dependency

    Returns:
        Paginated list of Pix keys
    """
    # Validate pagination params
    skip = max(0, skip)
    limit = min(100, max(1, limit))

    chaves, total = await service.listar_por_conta(conta_id, skip, limit)

    page = (skip // limit) + 1 if limit > 0 else 1

    return ListaChavesResponse(
        items=[ChavePixResponse.model_validate(c) for c in chaves],
        total=total,
        page=page,
        limit=limit,
    )


@router.delete(
    "/{chave_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Chave não encontrada"},
    },
)
async def deletar_chave(
    chave_id: UUID,
    service: PixKeyService = Depends(get_pix_key_service),
) -> None:
    """Delete a Pix key.

    Args:
        chave_id: Pix key ID
        service: PixKeyService dependency

    Raises:
        HTTPException: 404 if key not found
    """
    deleted = await service.deletar_chave(chave_id)

    if not deleted:
        logger.warning(f"Tentativa de deletar chave não encontrada", extra={"chave_id": str(chave_id)})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chave Pix não encontrada",
        )
