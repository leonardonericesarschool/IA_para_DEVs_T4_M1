"""Mapper between domain entities and DTOs."""
from app.application.dtos.expense_dto import (
    ExpenseCreateDTO,
    ExpenseResponseDTO,
)
from app.domain.entities.expense import Expense, ExpenseStatus, ExpenseType


class ExpenseMapper:
    """Mapper for expense entity conversions."""

    @staticmethod
    def dto_to_entity(dto: ExpenseCreateDTO) -> Expense:
        """
        Convert create DTO to domain entity.

        Args:
            dto: The create expense DTO

        Returns:
            Domain entity Expense
        """
        return Expense(
            name=dto.name,
            type=ExpenseType(dto.type),
            amount=dto.amount,
        )

    @staticmethod
    def entity_to_response_dto(
        entity: Expense, message: str = None
    ) -> ExpenseResponseDTO:
        """
        Convert domain entity to response DTO.

        Args:
            entity: The expense entity
            message: Optional custom message

        Returns:
            Response DTO with message
        """
        return ExpenseResponseDTO(
            id=entity.id,
            name=entity.name,
            type=entity.type.value,
            amount=entity.amount,
            status=entity.status.value,
            message=message,
            created_at=entity.created_at,
        )
