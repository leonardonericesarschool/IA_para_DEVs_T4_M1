"""FastAPI application factory and main entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings
from src.logging_config import configure_logging
from src.middleware import register_exception_handlers, logging_middleware
from src.database import create_db_and_tables


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    settings = get_settings()
    
    # Configure logging
    configure_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug
    )
    
    # Add middleware
    app.middleware("http")(logging_middleware)
    
    # Add CORS middleware for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Create database tables on startup
    @app.on_event("startup")
    def on_startup():
        create_db_and_tables()
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "app": settings.app_name, "version": settings.app_version}
    
    # API v1 routes placeholder
    @app.get("/api/v1")
    async def api_v1_info():
        return {"message": "Pix Keys Management API v1", "version": settings.app_version}
    
    return app


# Create application instance for uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
