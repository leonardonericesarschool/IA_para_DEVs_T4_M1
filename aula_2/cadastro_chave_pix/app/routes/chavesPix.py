from __future__ import annotations

import uuid

from flask_openapi3 import Tag
from pydantic import EmailStr, TypeAdapter
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.db import criarSessao
from app.errors import ErroApi
from app.models import ChavePix
from app.schemas import (
    ChavePixAtualizarRequest,
    ChavePixCriarRequest,
    ChavePixResponse,
    ListarChavesPixQuery,
    MensagemResponse,
    PaginacaoChavesPixResponse,
    normalizarDigitos,
    regexTelefone,
    regexSomenteDigitos,
)

tagChavesPix = Tag(name="Chaves Pix", description="Cadastro de chaves Pix")

emailAdapter = TypeAdapter(EmailStr)


def serializarChavePix(chavePix: ChavePix) -> ChavePixResponse:
    return ChavePixResponse(
        id=chavePix.id,
        tipoChave=chavePix.tipoChave,
        valorChave=chavePix.valorChave,
        descricao=chavePix.descricao,
        criadoEm=chavePix.criadoEm.isoformat(),
    )


def validarValorChavePorTipo(tipoChave: str, valorChave: str) -> str:
    if tipoChave in ("cpf", "cnpj"):
        digitos = normalizarDigitos(valorChave)
        if not regexSomenteDigitos.match(digitos):
            raise ErroApi(400, "Requisição inválida", [{"campo": "valorChave", "mensagem": "CPF/CNPJ deve conter apenas números"}])
        if tipoChave == "cpf" and len(digitos) != 11:
            raise ErroApi(400, "Requisição inválida", [{"campo": "valorChave", "mensagem": "CPF deve ter 11 dígitos"}])
        if tipoChave == "cnpj" and len(digitos) != 14:
            raise ErroApi(400, "Requisição inválida", [{"campo": "valorChave", "mensagem": "CNPJ deve ter 14 dígitos"}])
        return digitos

    if tipoChave == "telefone":
        texto = str(valorChave).strip()
        if not regexTelefone.match(texto):
            raise ErroApi(
                400,
                "Requisição inválida",
                [{"campo": "valorChave", "mensagem": "Telefone deve estar no formato E.164, por exemplo +5511999999999"}],
            )
        return texto

    if tipoChave == "email":
        try:
            emailValidado = emailAdapter.validate_python(valorChave)
        except Exception:
            raise ErroApi(400, "Requisição inválida", [{"campo": "valorChave", "mensagem": "Email inválido"}])
        return str(emailValidado).strip().lower()

    if tipoChave == "aleatoria":
        texto = str(valorChave).strip()
        try:
            uuid.UUID(texto)
        except Exception:
            raise ErroApi(400, "Requisição inválida", [{"campo": "valorChave", "mensagem": "Chave aleatória deve ser um UUID válido"}])
        return texto

    return str(valorChave).strip()


def registrarRotasChavesPix(app, sessionFactory):
    @app.post(
        "/api/v1/chaves-pix",
        tags=[tagChavesPix],
        responses={201: ChavePixResponse},
    )
    def criarChavePix(body: ChavePixCriarRequest):
        with criarSessao(sessionFactory) as sessao:
            chavePix = ChavePix(
                tipoChave=body.tipoChave,
                valorChave=body.valorChave,
                descricao=body.descricao,
            )
            sessao.add(chavePix)
            try:
                sessao.flush()
            except IntegrityError:
                raise ErroApi(400, "Requisição inválida", [{"campo": "valorChave", "mensagem": "Chave Pix já cadastrada"}])

            return serializarChavePix(chavePix).model_dump(), 201

    @app.get(
        "/api/v1/chaves-pix",
        tags=[tagChavesPix],
        responses={200: PaginacaoChavesPixResponse},
    )
    def listarChavesPix(query: ListarChavesPixQuery):
        page = query.page
        limit = query.limit
        offset = (page - 1) * limit

        filtros = []
        if query.tipoChave:
            filtros.append(ChavePix.tipoChave == query.tipoChave)
        if query.valorChave:
            filtros.append(ChavePix.valorChave == query.valorChave)

        with criarSessao(sessionFactory) as sessao:
            total = sessao.execute(select(func.count()).select_from(ChavePix).where(*filtros)).scalar_one()
            itens = (
                sessao.execute(
                    select(ChavePix)
                    .where(*filtros)
                    .order_by(ChavePix.id.desc())
                    .offset(offset)
                    .limit(limit)
                )
                .scalars()
                .all()
            )

            payload = PaginacaoChavesPixResponse(
                itens=[serializarChavePix(item) for item in itens],
                page=page,
                limit=limit,
                total=total,
            )
            return payload.model_dump()

    @app.get(
        "/api/v1/chaves-pix/<int:id>",
        tags=[tagChavesPix],
        responses={200: ChavePixResponse},
    )
    def buscarChavePixPorId(id: int):
        with criarSessao(sessionFactory) as sessao:
            chavePix = sessao.get(ChavePix, id)
            if not chavePix:
                raise ErroApi(404, "Recurso não encontrado")
            return serializarChavePix(chavePix).model_dump()

    @app.put(
        "/api/v1/chaves-pix/<int:id>",
        tags=[tagChavesPix],
        responses={200: ChavePixResponse},
    )
    def atualizarChavePix(body: ChavePixAtualizarRequest, id: int):
        if body.valorChave is None and body.descricao is None:
            raise ErroApi(400, "Requisição inválida", [{"mensagem": "Informe ao menos um campo para atualização"}])

        with criarSessao(sessionFactory) as sessao:
            chavePix = sessao.get(ChavePix, id)
            if not chavePix:
                raise ErroApi(404, "Recurso não encontrado")

            if body.descricao is not None:
                chavePix.descricao = body.descricao
            if body.valorChave is not None:
                chavePix.valorChave = validarValorChavePorTipo(chavePix.tipoChave, body.valorChave)

            try:
                sessao.flush()
            except IntegrityError:
                raise ErroApi(400, "Requisição inválida", [{"campo": "valorChave", "mensagem": "Chave Pix já cadastrada"}])

            return serializarChavePix(chavePix).model_dump()

    @app.delete(
        "/api/v1/chaves-pix/<int:id>",
        tags=[tagChavesPix],
        responses={200: MensagemResponse},
    )
    def removerChavePix(id: int):
        with criarSessao(sessionFactory) as sessao:
            chavePix = sessao.get(ChavePix, id)
            if not chavePix:
                raise ErroApi(404, "Recurso não encontrado")
            sessao.delete(chavePix)
            return {"mensagem": "Chave Pix removida com sucesso"}
