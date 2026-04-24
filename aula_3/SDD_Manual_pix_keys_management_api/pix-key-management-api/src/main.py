"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from src.config import settings
from src.core.logging import setup_logging
from src.api.v1.routes import pix_keys

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers
app.include_router(pix_keys.router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": settings.api_title}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
