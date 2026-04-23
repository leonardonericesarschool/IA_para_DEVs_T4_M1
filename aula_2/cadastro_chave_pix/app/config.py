from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    nomeApp: str = "cadastro_chave_pix"
    debug: bool = True
    databaseUrl: str = "sqlite:///cadastro_chave_pix.db"
