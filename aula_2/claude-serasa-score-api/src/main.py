"""
Entrypoint da aplicação FastAPI.

Configuração: CORS, middlewares, routers, exception handlers, lifespan.
"""

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.api.v1.routes.score import router as score_router
from src.core.config import get_settings
from src.core.exception_handlers import register_exception_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

# ── Rate Limiter ──────────────────────────────────────────────────────────────

limiter = Limiter(key_func=get_remote_address)


# ── Lifespan (startup/shutdown) ───────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    logger.info("🚀 Iniciando %s v%s [%s]", settings.app_name, settings.app_version, settings.environment)
    yield
    logger.info("🛑 Encerrando %s", settings.app_name)


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API para consulta de score de crédito SERASA.\n\n"
        "## Autenticação\n"
        "Todas as rotas requerem o header `X-API-Key`.\n\n"
        "## LGPD\n"
        "CPFs são mascarados em logs e nas respostas da API."
    ),
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

# ── Middlewares ───────────────────────────────────────────────────────────────

# CORS: origens explícitas em produção — nunca wildcard com credenciais
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.suaempresa.com.br"] if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["X-API-Key", "Content-Type"],
)

# Request ID para rastreabilidade
@app.middleware("http")
async def add_request_id(request: Request, call_next):  # type: ignore[no-untyped-def]
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Exception Handlers ────────────────────────────────────────────────────────

register_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(score_router, prefix="/v1")

# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root() -> dict:
    return {"app": settings.app_name, "version": settings.app_version, "status": "running"}
