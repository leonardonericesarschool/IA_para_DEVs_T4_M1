from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import jsonify


@dataclass(frozen=True)
class ErroApi(Exception):
    statusCode: int
    mensagem: str
    detalhes: Any | None = None


def responderErro(mensagem: str, statusCode: int, detalhes: Any | None = None):
    payload = {"mensagem": mensagem}
    if detalhes is not None:
        payload["detalhes"] = detalhes
    return jsonify(payload), statusCode


def registrarHandlersDeErro(app):
    @app.errorhandler(ErroApi)
    def tratarErroApi(erro: ErroApi):
        return responderErro(erro.mensagem, erro.statusCode, erro.detalhes)

    @app.errorhandler(404)
    def tratarNaoEncontrado(_):
        return responderErro("Recurso não encontrado", 404)

    @app.errorhandler(400)
    def tratarBadRequest(erro):
        descricao = getattr(erro, "description", None)
        detalhes = None
        if descricao:
            detalhes = descricao
        return responderErro("Requisição inválida", 400, detalhes)

    @app.errorhandler(Exception)
    def tratarErroInesperado(erro: Exception):
        app.logger.exception(erro)
        return responderErro("Erro interno no servidor", 500)
