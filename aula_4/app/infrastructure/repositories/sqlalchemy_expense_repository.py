"""SQLAlchemy implementation of ExpenseRepository."""
from typing import List, Optional

from app.domain.entities.expense import Expense, ExpenseStatus, ExpenseType
from app.domain.repositories.expense_repository import ExpenseRepository
from app.infrastructure.database.models import ExpenseModel, db


class SQLAlchemyExpenseRepository(ExpenseRepository):
    """Concrete implementation of ExpenseRepository using SQLAlchemy."""

    def save(self, expense: Expense) -> Expense:
        """
        Save an expense to the database.

        Args:
            expense: The expense entity to save

        Returns:
            The saved expense with ID populated

        Raises:
            Exception: If save fails
        """
        model = ExpenseModel(
            name=expense.name,
            type=expense.type.value,
            amount=expense.amount,
            status=expense.status.value,
            created_at=expense.created_at,
        )

        db.session.add(model)
        db.session.commit()

        # Update expense with generated ID
        expense.id = model.id
        return expense

    def get_by_id(self, expense_id: int) -> Optional[Expense]:
        """
        Retrieve an expense by ID.

        Args:
            expense_id: The ID of the expense

        Returns:
            The expense if found, None otherwise
        """
        model = ExpenseModel.query.get(expense_id)

        if not model:
            return None

        return self._model_to_entity(model)

    def list_all(self) -> List[Expense]:
        """
        Retrieve all expenses.

        Returns:
            List of all expenses ordered by creation date (newest first)
        """
        models = ExpenseModel.query.order_by(ExpenseModel.created_at.desc()).all()
        return [self._model_to_entity(model) for model in models]

    @staticmethod
    def _model_to_entity(model: ExpenseModel) -> Expense:
        """
        Convert database model to domain entity.

        Args:
            model: The database model

        Returns:
            The domain entity
        """
        return Expense(
            id=model.id,
            name=model.name,
            type=ExpenseType(model.type),
            amount=model.amount,
            status=ExpenseStatus(model.status),
            created_at=model.created_at,
        )
