from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base


def criarEngine(databaseUrl: str):
    return create_engine(databaseUrl, future=True)


def criarSessionFactory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def inicializarBanco(engine):
    Base.metadata.create_all(bind=engine)


@contextmanager
def criarSessao(sessionFactory):
    sessao = sessionFactory()
    try:
        yield sessao
        sessao.commit()
    except Exception:
        sessao.rollback()
        raise
    finally:
        sessao.close()
