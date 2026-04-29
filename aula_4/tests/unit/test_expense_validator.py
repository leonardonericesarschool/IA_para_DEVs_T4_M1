"""Unit tests for expense validator."""
import pytest

from app.domain.entities.expense import Expense, ExpenseType
from app.domain.services.expense_validator import ExpenseValidator


class TestExpenseValidator:
    """Test suite for ExpenseValidator."""

    def test_alimentacao_valid_under_limit(self):
        """Test alimentação expense under R$ 100 limit is valid."""
        # Cenário 1: Alimentação com R$ 80,00 deve ser aceita
        expense = Expense(
            name="Almoço de trabalho",
            type=ExpenseType.ALIMENTACAO,
            amount=80.0,
        )

        result = ExpenseValidator.validate(expense)

        assert result.is_valid is True
        assert result.message == ""

    def test_alimentacao_valid_at_limit(self):
        """Test alimentação expense at exactly R$ 100 limit is valid."""
        expense = Expense(
            name="Almoço de trabalho",
            type=ExpenseType.ALIMENTACAO,
            amount=100.0,
        )

        result = ExpenseValidator.validate(expense)

        assert result.is_valid is True
        assert result.message == ""

    def test_alimentacao_invalid_over_limit(self):
        """Test alimentação expense over R$ 100 limit is invalid."""
        # Cenário 2: Alimentação com R$ 120,00 deve ser recusada
        expense = Expense(
            name="Almoço de trabalho",
            type=ExpenseType.ALIMENTACAO,
            amount=120.0,
        )

        result = ExpenseValidator.validate(expense)

        assert result.is_valid is False
        assert "não pode exceder R$ 100,00" in result.message

    def test_alimentacao_invalid_significantly_over_limit(self):
        """Test alimentação expense significantly over limit is invalid."""
        expense = Expense(
            name="Banquete corporativo",
            type=ExpenseType.ALIMENTACAO,
            amount=500.0,
        )

        result = ExpenseValidator.validate(expense)

        assert result.is_valid is False
        assert "não pode exceder R$ 100,00" in result.message

    def test_transporte_no_limit(self):
        """Test transporte expense has no limit."""
        # Cenário 3: Transporte com R$ 150,00 deve ser aceita
        expense = Expense(
            name="Passagem aérea",
            type=ExpenseType.TRANSPORTE,
            amount=150.0,
        )

        result = ExpenseValidator.validate(expense)

        assert result.is_valid is True
        assert result.message == ""

    def test_transporte_high_amount(self):
        """Test transporte expense with high amount is valid."""
        expense = Expense(
            name="Aluguel de carro",
            type=ExpenseType.TRANSPORTE,
            amount=5000.0,
        )

        result = ExpenseValidator.validate(expense)

        assert result.is_valid is True
        assert result.message == ""

    def test_alimentacao_just_over_limit(self):
        """Test alimentação expense just over limit is invalid."""
        expense = Expense(
            name="Lanche",
            type=ExpenseType.ALIMENTACAO,
            amount=100.01,
        )

        result = ExpenseValidator.validate(expense)

        assert result.is_valid is False
