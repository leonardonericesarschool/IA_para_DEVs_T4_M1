"""Repository interface for expenses."""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.expense import Expense


class ExpenseRepository(ABC):
    """Abstract repository for expense persistence."""

    @abstractmethod
    def save(self, expense: Expense) -> Expense:
        """
        Save an expense to persistence.

        Args:
            expense: The expense entity to save

        Returns:
            The saved expense with ID populated

        Raises:
            Exception: If save fails
        """
        pass

    @abstractmethod
    def get_by_id(self, expense_id: int) -> Optional[Expense]:
        """
        Retrieve an expense by ID.

        Args:
            expense_id: The ID of the expense

        Returns:
            The expense if found, None otherwise
        """
        pass

    @abstractmethod
    def list_all(self) -> List[Expense]:
        """
        Retrieve all expenses.

        Returns:
            List of all expenses
        """
        pass
