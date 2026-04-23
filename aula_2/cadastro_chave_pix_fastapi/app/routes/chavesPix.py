from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError

from app.models import ChavePix
from app.schemas import (
    ChavePixCriarRequest,
    ChavePixAtualizarRequest,
    ChavePixResponse,
    PaginatedResponse,
)
from app.errors import ErroApi

router = APIRouter(
    prefix="/api/v1/chaves-pix",
    tags=["Chaves Pix"],
)

# Dependência global que será injetada
SessionLocal: sessionmaker = None


def definirSessionLocal(session_factory: sessionmaker):
    """Define a factory de sessões para o roteador."""
    global SessionLocal
    SessionLocal = session_factory


def obterSessao() -> Session:
    """Dependência para injetar sessão no endpoint."""
    sessao = SessionLocal()
    try:
        yield sessao
    finally:
        sessao.close()


def serializarChavePix(chavePix: ChavePix) -> dict:
    """
    Serializa um objeto ChavePix para dicionário.
    
    Args:
        chavePix: Objeto ChavePix do banco
        
    Returns:
        Dicionário com os dados da chave
    """
    return {
        "id": chavePix.id,
        "tipoChave": chavePix.tipoChave,
        "valorChave": chavePix.valorChave,
        "descricao": chavePix.descricao,
        "criadoEm": chavePix.criadoEm,
        "atualizadoEm": chavePix.atualizadoEm,
    }


@router.post(
    "",
    status_code=201,
    response_model=ChavePixResponse,
    responses={
        400: {"model": dict, "description": "Requisição inválida ou chave duplicada"},
        500: {"model": dict, "description": "Erro interno do servidor"},
    },
)
def criarChavePix(body: ChavePixCriarRequest, sessao: Session = Depends(obterSessao)):
    """
    Cria uma nova chave Pix.
    
    **Regras**:
    - A combinação (tipoChave, valorChave) deve ser única
    - Retorna 201 se criada com sucesso
    - Retorna 400 se chave duplicada
    
    **Body**:
    - tipoChave: CPF, CNPJ, EMAIL ou TELEFONE
    - valorChave: valor da chave (obrigatório)
    - descricao: (opcional)
    """
    try:
        # Verificar se chave já existe
        chaveExistente = sessao.query(ChavePix).filter_by(
            tipoChave=body.tipoChave.value,
            valorChave=body.valorChave,
        ).first()
        
        if chaveExistente:
            raise ErroApi(
                statusCode=400,
                mensagem="Chave Pix já registrada",
                detalhes={
                    "tipoChave": body.tipoChave.value,
                    "valorChave": body.valorChave,
                },
            )
        
        # Criar nova chave
        novaChave = ChavePix(
            tipoChave=body.tipoChave.value,
            valorChave=body.valorChave,
            descricao=body.descricao,
        )
        
        sessao.add(novaChave)
        sessao.commit()
        sessao.refresh(novaChave)
        
        return serializarChavePix(novaChave)
        
    except ErroApi:
        sessao.rollback()
        raise
    except IntegrityError as e:
        sessao.rollback()
        raise ErroApi(
            statusCode=400,
            mensagem="Erro de integridade de dados",
            detalhes={"erro": str(e)},
        )
    except Exception as e:
        sessao.rollback()
        raise ErroApi(
            statusCode=500,
            mensagem="Erro ao criar chave Pix",
            detalhes={"erro": str(e)},
        )


@router.get(
    "",
    response_model=PaginatedResponse,
    responses={
        400: {"model": dict, "description": "Parâmetros inválidos"},
        500: {"model": dict, "description": "Erro interno do servidor"},
    },
)
def listarChavesPix(
    page: int = Query(1, ge=1, description="Página (começa em 1)"),
    limit: int = Query(10, ge=1, le=100, description="Limite de itens (máx 100)"),
    sessao: Session = Depends(obterSessao),
):
    """
    Lista todas as chaves Pix com paginação.
    
    **Query Parameters**:
    - page: Página (padrão: 1)
    - limit: Limite de itens por página (padrão: 10, máx: 100)
    
    **Response**:
    - items: Lista de chaves Pix
    - total: Total de chaves
    - page: Página atual
    - limit: Limite utilizado
    - pages: Total de páginas
    """
    try:
        # Contar total
        total = sessao.query(ChavePix).count()
        
        # Calcular offset e total de páginas
        offset = (page - 1) * limit
        total_pages = (total + limit - 1) // limit
        
        # Buscar chaves paginadas
        chaves = sessao.query(ChavePix).offset(offset).limit(limit).all()
        
        sessao.commit()
        
        items = [serializarChavePix(chave) for chave in chaves]
        
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=total_pages,
        )
        
    except Exception as e:
        sessao.rollback()
        raise ErroApi(
            statusCode=500,
            mensagem="Erro ao listar chaves Pix",
            detalhes={"erro": str(e)},
        )


@router.get(
    "/{id}",
    response_model=ChavePixResponse,
    responses={
        404: {"model": dict, "description": "Chave não encontrada"},
        500: {"model": dict, "description": "Erro interno do servidor"},
    },
)
def obterChavePix(id: int, sessao: Session = Depends(obterSessao)):
    """
    Obtém uma chave Pix pelo ID.
    
    **Path Parameters**:
    - id: ID da chave Pix
    
    **Response**:
    - Retorna a chave se encontrada (200)
    - Retorna 404 se não encontrada
    """
    try:
        chavePix = sessao.query(ChavePix).filter_by(id=id).first()
        
        if not chavePix:
            sessao.commit()
            raise HTTPException(
                status_code=404,
                detail="Chave Pix não encontrada",
            )
        
        sessao.commit()
        return serializarChavePix(chavePix)
        
    except HTTPException:
        raise
    except Exception as e:
        sessao.rollback()
        raise ErroApi(
            statusCode=500,
            mensagem="Erro ao obter chave Pix",
            detalhes={"erro": str(e)},
        )


@router.put(
    "/{id}",
    response_model=ChavePixResponse,
    responses={
        404: {"model": dict, "description": "Chave não encontrada"},
        500: {"model": dict, "description": "Erro interno do servidor"},
    },
)
def atualizarChavePix(
    id: int,
    body: ChavePixAtualizarRequest,
    sessao: Session = Depends(obterSessao),
):
    """
    Atualiza uma chave Pix (apenas descrição).
    
    **Path Parameters**:
    - id: ID da chave Pix
    
    **Body**:
    - descricao: Nova descrição (opcional)
    
    **Response**:
    - Retorna a chave atualizada se sucesso (200)
    - Retorna 404 se não encontrada
    """
    try:
        chavePix = sessao.query(ChavePix).filter_by(id=id).first()
        
        if not chavePix:
            sessao.commit()
            raise HTTPException(
                status_code=404,
                detail="Chave Pix não encontrada",
            )
        
        # Atualizar apenas o campo descricao
        if body.descricao is not None:
            chavePix.descricao = body.descricao
        
        sessao.commit()
        sessao.refresh(chavePix)
        
        return serializarChavePix(chavePix)
        
    except HTTPException:
        raise
    except Exception as e:
        sessao.rollback()
        raise ErroApi(
            statusCode=500,
            mensagem="Erro ao atualizar chave Pix",
            detalhes={"erro": str(e)},
        )


@router.delete(
    "/{id}",
    status_code=204,
    responses={
        404: {"model": dict, "description": "Chave não encontrada"},
        500: {"model": dict, "description": "Erro interno do servidor"},
    },
)
def deletarChavePix(id: int, sessao: Session = Depends(obterSessao)):
    """
    Deleta uma chave Pix.
    
    **Path Parameters**:
    - id: ID da chave Pix
    
    **Response**:
    - Retorna 204 No Content se deletada
    - Retorna 404 se não encontrada
    """
    try:
        chavePix = sessao.query(ChavePix).filter_by(id=id).first()
        
        if not chavePix:
            sessao.commit()
            raise HTTPException(
                status_code=404,
                detail="Chave Pix não encontrada",
            )
        
        sessao.delete(chavePix)
        sessao.commit()
        
        # 204 No Content
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        sessao.rollback()
        raise ErroApi(
            statusCode=500,
            mensagem="Erro ao deletar chave Pix",
            detalhes={"erro": str(e)},
        )
