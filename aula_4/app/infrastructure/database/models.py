"""SQLAlchemy database models."""
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ExpenseModel(db.Model):
    """Database model for expenses."""

    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(
        db.String(50), nullable=False
    )  # "alimentação" or "transporte"
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.String(50), nullable=False, default="aceita"
    )  # "aceita" or "recusada"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """String representation."""
        return f"<ExpenseModel(id={self.id}, name={self.name}, type={self.type}, amount={self.amount}, status={self.status})>"
