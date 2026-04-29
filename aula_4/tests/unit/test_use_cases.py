"""Unit tests for use cases."""
import pytest
from unittest.mock import MagicMock

from app.application.dtos.expense_dto import ExpenseCreateDTO
from app.application.use_cases.create_expense_use_case import CreateExpenseUseCase
from app.application.use_cases.list_expenses_use_case import ListExpensesUseCase
from app.domain.entities.expense import Expense, ExpenseStatus, ExpenseType


class TestCreateExpenseUseCase:
    """Test suite for CreateExpenseUseCase."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        mock = MagicMock()
        mock.save.return_value = Expense(
            id=1,
            name="Test Expense",
            type=ExpenseType.ALIMENTACAO,
            amount=80.0,
            status=ExpenseStatus.ACEITA,
        )
        return mock

    @pytest.fixture
    def use_case(self, mock_repository):
        """Create use case with mock repository."""
        return CreateExpenseUseCase(mock_repository)

    def test_create_valid_alimentacao_expense(self, use_case, mock_repository):
        """Test creating a valid alimentação expense."""
        # Arrange
        dto = ExpenseCreateDTO(
            name="Almoço de trabalho",
            type="alimentação",
            amount=80.0,
        )

        # Act
        response, status_code = use_case.execute(dto)

        # Assert
        assert status_code == 201
        assert response.status == "aceita"
        assert response.message == "Despesa registrada com sucesso"
        assert response.name == "Test Expense"
        mock_repository.save.assert_called_once()

    def test_create_invalid_alimentacao_expense_over_limit(
        self, use_case, mock_repository
    ):
        """Test creating an invalid alimentação expense over limit."""
        # Arrange
        mock_repository.save.return_value = Expense(
            id=2,
            name="Almoço caro",
            type=ExpenseType.ALIMENTACAO,
            amount=120.0,
            status=ExpenseStatus.RECUSADA,
        )

        dto = ExpenseCreateDTO(
            name="Almoço caro",
            type="alimentação",
            amount=120.0,
        )

        # Act
        response, status_code = use_case.execute(dto)

        # Assert
        assert status_code == 400
        assert response.status == "recusada"
        assert "não pode exceder R$ 100,00" in response.message

    def test_create_transporte_expense(self, use_case, mock_repository):
        """Test creating a transporte expense."""
        # Arrange
        mock_repository.save.return_value = Expense(
            id=3,
            name="Passagem aérea",
            type=ExpenseType.TRANSPORTE,
            amount=500.0,
            status=ExpenseStatus.ACEITA,
        )

        dto = ExpenseCreateDTO(
            name="Passagem aérea",
            type="transporte",
            amount=500.0,
        )

        # Act
        response, status_code = use_case.execute(dto)

        # Assert
        assert status_code == 201
        assert response.status == "aceita"


class TestListExpensesUseCase:
    """Test suite for ListExpensesUseCase."""

    def test_list_expenses_empty(self):
        """Test listing expenses when none exist."""
        # Arrange
        mock_repository = MagicMock()
        mock_repository.list_all.return_value = []
        use_case = ListExpensesUseCase(mock_repository)

        # Act
        result = use_case.execute()

        # Assert
        assert result == []
        mock_repository.list_all.assert_called_once()

    def test_list_expenses_multiple(self):
        """Test listing multiple expenses."""
        # Arrange
        mock_repository = MagicMock()
        expenses = [
            Expense(
                id=1,
                name="Almoço",
                type=ExpenseType.ALIMENTACAO,
                amount=80.0,
                status=ExpenseStatus.ACEITA,
            ),
            Expense(
                id=2,
                name="Uber",
                type=ExpenseType.TRANSPORTE,
                amount=50.0,
                status=ExpenseStatus.ACEITA,
            ),
        ]
        mock_repository.list_all.return_value = expenses
        use_case = ListExpensesUseCase(mock_repository)

        # Act
        result = use_case.execute()

        # Assert
        assert len(result) == 2
        assert result[0].name == "Almoço"
        assert result[1].name == "Uber"
        mock_repository.list_all.assert_called_once()
