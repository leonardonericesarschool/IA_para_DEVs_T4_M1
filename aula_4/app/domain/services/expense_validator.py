"""Expense validation service - implements business rules."""
from dataclasses import dataclass
from typing import Tuple

from app.domain.entities.expense import Expense, ExpenseStatus, ExpenseType


@dataclass
class ValidationResult:
    """Result of expense validation."""

    is_valid: bool
    message: str = ""


class ExpenseValidator:
    """Validator for business rules regarding expenses."""

    # Maximum amount for alimentação in cents or decimal
    MAX_ALIMENTACAO = 100.0  # R$ 100,00
    MAX_TRANSPORTE = float("inf")  # No limit for transporte

    @staticmethod
    def validate(expense: Expense) -> ValidationResult:
        """
        Validate an expense against business rules.

        Rules:
        - Alimentação: maximum R$ 100,00
        - Transporte: no limit

        Args:
            expense: The expense to validate

        Returns:
            ValidationResult with is_valid flag and message if invalid
        """
        if expense.type == ExpenseType.ALIMENTACAO:
            if expense.amount > ExpenseValidator.MAX_ALIMENTACAO:
                return ValidationResult(
                    is_valid=False,
                    message=f"Despesa de alimentação não pode exceder R$ 100,00",
                )

        elif expense.type == ExpenseType.TRANSPORTE:
            # No specific limit for transporte
            pass

        return ValidationResult(is_valid=True)
