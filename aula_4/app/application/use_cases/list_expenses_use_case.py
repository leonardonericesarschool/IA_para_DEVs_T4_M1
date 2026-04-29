"""Use case for listing all expenses."""
from typing import List

from app.application.dtos.expense_dto import ExpenseResponseDTO
from app.application.mappers.expense_mapper import ExpenseMapper
from app.domain.repositories.expense_repository import ExpenseRepository


class ListExpensesUseCase:
    """Use case for listing all expenses."""

    def __init__(self, repository: ExpenseRepository):
        """
        Initialize the use case.

        Args:
            repository: The expense repository
        """
        self.repository = repository

    def execute(self) -> List[ExpenseResponseDTO]:
        """
        Execute the use case to list all expenses.

        Returns:
            List of expense response DTOs
        """
        expenses = self.repository.list_all()
        return [ExpenseMapper.entity_to_response_dto(expense) for expense in expenses]
