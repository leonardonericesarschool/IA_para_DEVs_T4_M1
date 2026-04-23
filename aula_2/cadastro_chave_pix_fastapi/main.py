import uvicorn
from app import criarApp
from app.config import Config


if __name__ == "__main__":
    config = Config.from_env()
    app = criarApp(config)
    
    # Para usar reload em desenvolvimento:
    # uvicorn main:app --reload
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
    )
