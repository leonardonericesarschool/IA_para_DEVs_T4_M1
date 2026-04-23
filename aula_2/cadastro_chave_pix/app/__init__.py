from __future__ import annotations

from flask_openapi3 import Info, OpenAPI
from pydantic import BaseModel

from app.config import Config
from app.db import criarEngine, criarSessionFactory, inicializarBanco
from app.errors import registrarHandlersDeErro
from app.routes.chavesPix import registrarRotasChavesPix


def criarApp(config: Config | None = None):
    config = config or Config()

    info = Info(
        title="API de Cadastro de Chave Pix",
        version="1.0.0",
        description="API REST para cadastro de chaves Pix (CPF/CNPJ/Email/Telefone/Aleatória).",
    )
    app = OpenAPI(config.nomeApp, info=info)
    app.config["DEBUG"] = config.debug

    engine = criarEngine(config.databaseUrl)
    sessionFactory = criarSessionFactory(engine)
    inicializarBanco(engine)

    app.extensions["engine"] = engine
    app.extensions["sessionFactory"] = sessionFactory

    registrarHandlersDeErro(app)

    class ApiInfoResponse(BaseModel):
        mensagem: str
        swaggerUi: str
        openapiJson: str

    @app.get("/", responses={200: ApiInfoResponse})
    def raiz():
        return {
            "mensagem": "API de Cadastro de Chave Pix",
            "swaggerUi": "/openapi/",
            "openapiJson": "/openapi/openapi.json",
        }

    @app.get("/api/v1/health", responses={200: ApiInfoResponse})
    def health():
        return {
            "mensagem": "OK",
            "swaggerUi": "/openapi/",
            "openapiJson": "/openapi/openapi.json",
        }

    registrarRotasChavesPix(app, sessionFactory)

    return app

