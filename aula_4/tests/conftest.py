"""Pytest fixtures and configuration."""
import pytest

from app.config.settings import TestingConfig
from app.infrastructure.database.models import db
from app.main import create_app


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = create_app(config=TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Provide a Flask test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Provide a database session for tests."""
    with app.app_context():
        yield db.session


@pytest.fixture
def runner(app):
    """Provide a Flask CLI test runner."""
    return app.test_cli_runner()
