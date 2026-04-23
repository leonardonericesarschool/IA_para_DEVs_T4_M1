from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.config import Config
from app.db import inicializarBancoDados
from app.errors import ErroApi
from app.routes import chavesPix


def criarApp(config: Config = None) -> FastAPI:
    """
    Factory para criar e configurar a aplicação FastAPI.
    
    Responsabilidades:
    - Instanciar FastAPI
    - Inicializar banco de dados
    - Registrar handlers de erro
    - Registrar rotas
    
    Args:
        config: Objeto de configuração (usa padrão se None)
        
    Returns:
        Aplicação FastAPI configurada
    """
    if config is None:
        config = Config.from_env()
    
    # Criar aplicação
    app = FastAPI(
        title=config.nomeApp,
        description="API REST para cadastro de chaves Pix com FastAPI",
        version="1.0.0",
        debug=config.debug,
    )
    
    # Inicializar banco de dados
    engine, SessionLocal = inicializarBancoDados(config)
    
    # Injeta a SessionLocal nas rotas
    chavesPix.definirSessionLocal(SessionLocal)
    
    # ======================
    # Handlers de Erro
    # ======================
    
    @app.exception_handler(ErroApi)
    async def manipularErroApi(request, exc: ErroApi):
        """Handler para erros customizados da API."""
        return JSONResponse(
            status_code=exc.statusCode,
            content={
                "mensagem": exc.mensagem,
                "detalhes": exc.detalhes,
            },
        )
    
    @app.exception_handler(RequestValidationError)
    async def manipularErroValidacao(request, exc: RequestValidationError):
        """Handler para erros de validação Pydantic."""
        erros = []
        for erro in exc.errors():
            campo = ".".join(str(x) for x in erro["loc"][1:])
            erros.append({
                "campo": campo,
                "mensagem": erro["msg"],
                "tipo": erro["type"],
            })
        
        return JSONResponse(
            status_code=422,
            content={
                "mensagem": "Erro de validação",
                "detalhes": {
                    "erros": erros,
                },
            },
        )
    
    @app.exception_handler(Exception)
    async def manipularErroGenerico(request, exc: Exception):
        """Handler para erros genéricos."""
        return JSONResponse(
            status_code=500,
            content={
                "mensagem": "Erro interno do servidor",
                "detalhes": {
                    "erro": str(exc),
                },
            },
        )
    
    # ======================
    # Health Check
    # ======================
    
    @app.get("/health", tags=["Health"])
    async def healthCheck():
        """Verifica se a aplicação está ativa."""
        return {"status": "ok", "aplicacao": config.nomeApp}
    
    # ======================
    # Rotas
    # ======================
    
    app.include_router(chavesPix.router)
    
    return app
