"""Database connection and initialization."""
from flask import Flask

from app.infrastructure.database.models import db


def init_db(app: Flask) -> None:
    """
    Initialize the database.

    Creates all tables if they don't exist.

    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.create_all()


def setup_database(app: Flask) -> None:
    """
    Setup database with Flask app.

    Args:
        app: Flask application instance
    """
    db.init_app(app)
