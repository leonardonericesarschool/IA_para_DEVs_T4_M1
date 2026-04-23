from contextlib import contextmanager
import datetime as dt
from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator

from app.config import Config

# Configuração base para ORM
Base = declarative_base()


def inicializarBancoDados(config: Config) -> tuple[any, sessionmaker]:
    """
    Inicializa o banco de dados e retorna engine e session factory.
    
    Args:
        config: Objeto de configuração
        
    Returns:
        Tupla (engine, SessionLocal)
    """
    engine = create_engine(
        config.databaseUrl,
        connect_args={"check_same_thread": False} if "sqlite" in config.databaseUrl else {},
        echo=config.debug,
    )
    
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    
    return engine, SessionLocal


@contextmanager
def criarSessao(SessionLocal: sessionmaker) -> Generator[Session, None, None]:
    """
    Context manager para gerenciar sessões de banco de dados.
    Garante commit ou rollback automático.
    
    Args:
        SessionLocal: Factory de sessões
        
    Yields:
        Sessão do banco de dados
    """
    sessao = SessionLocal()
    try:
        yield sessao
        sessao.commit()
    except Exception:
        sessao.rollback()
        raise
    finally:
        sessao.close()
