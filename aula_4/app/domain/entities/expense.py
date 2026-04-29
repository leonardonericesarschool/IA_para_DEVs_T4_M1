"""Expense domain entity."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ExpenseType(str, Enum):
    """Types of expenses."""

    ALIMENTACAO = "alimentação"
    TRANSPORTE = "transporte"


class ExpenseStatus(str, Enum):
    """Status of expense."""

    ACEITA = "aceita"
    RECUSADA = "recusada"


@dataclass
class Expense:
    """Domain entity representing an expense."""

    name: str
    type: ExpenseType
    amount: float
    id: Optional[int] = None
    status: ExpenseStatus = ExpenseStatus.ACEITA
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate expense on creation."""
        if not self.name or not self.name.strip():
            raise ValueError("Expense name cannot be empty")
        if self.amount <= 0:
            raise ValueError("Expense amount must be greater than zero")

    def reject(self):
        """Mark expense as rejected."""
        self.status = ExpenseStatus.RECUSADA

    def accept(self):
        """Mark expense as accepted."""
        self.status = ExpenseStatus.ACEITA
