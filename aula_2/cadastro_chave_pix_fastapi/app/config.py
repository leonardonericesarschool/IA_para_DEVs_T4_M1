from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Config:
    """Configuração da aplicação."""
    nomeApp: str = "cadastro_chave_pix"
    debug: bool = True
    databaseUrl: str = "sqlite:///cadastro_chave_pix.db"
    host: str = "127.0.0.1"
    port: int = 8000
    
    @classmethod
    def from_env(cls) -> "Config":
        """Carrega configuração a partir de variáveis de ambiente."""
        return cls(
            nomeApp=os.getenv("NOME_APP", cls.nomeApp),
            debug=os.getenv("DEBUG", "True").lower() == "true",
            databaseUrl=os.getenv("DATABASE_URL", cls.databaseUrl),
            host=os.getenv("HOST", cls.host),
            port=int(os.getenv("PORT", cls.port)),
        )
