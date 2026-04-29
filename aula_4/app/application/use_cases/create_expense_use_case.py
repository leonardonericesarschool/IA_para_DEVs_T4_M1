"""Use case for creating a new expense."""
from typing import Tuple

from app.application.dtos.expense_dto import (
    ExpenseCreateDTO,
    ExpenseResponseDTO,
)
from app.application.mappers.expense_mapper import ExpenseMapper
from app.domain.repositories.expense_repository import ExpenseRepository
from app.domain.services.expense_validator import ExpenseValidator


class CreateExpenseUseCase:
    """Use case for creating a new expense with validation."""

    def __init__(self, repository: ExpenseRepository):
        """
        Initialize the use case.

        Args:
            repository: The expense repository
        """
        self.repository = repository
        self.validator = ExpenseValidator()

    def execute(self, dto: ExpenseCreateDTO) -> Tuple[ExpenseResponseDTO, int]:
        """
        Execute the use case to create an expense.

        Process:
        1. Convert DTO to entity
        2. Validate business rules
        3. Apply status based on validation
        4. Persist to repository
        5. Return response with appropriate HTTP status

        Args:
            dto: The expense creation DTO

        Returns:
            Tuple of (response_dto, http_status_code)
            - On validation success: (ExpenseResponseDTO with status="aceita", 201)
            - On validation failure: (ExpenseResponseDTO with status="recusada", 400)

        Raises:
            ValueError: If DTO validation fails (should be caught by Pydantic before)
        """
        # Convert DTO to domain entity
        expense = ExpenseMapper.dto_to_entity(dto)

        # Validate against business rules
        validation_result = self.validator.validate(expense)

        # Apply status and message based on validation
        if not validation_result.is_valid:
            expense.reject()
            message = validation_result.message
            http_status = 400
        else:
            expense.accept()
            message = "Despesa registrada com sucesso"
            http_status = 201

        # Persist the expense
        saved_expense = self.repository.save(expense)

        # Convert to response DTO
        response = ExpenseMapper.entity_to_response_dto(saved_expense, message)

        return response, http_status
