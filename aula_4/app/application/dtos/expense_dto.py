"""Data Transfer Objects for expenses."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ExpenseCreateDTO(BaseModel):
    """DTO for creating a new expense."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(alimentação|transporte)$")
    amount: float = Field(..., gt=0)

    @field_validator("name")
    @classmethod
    def name_must_not_be_whitespace(cls, v):
        """Validate name is not just whitespace."""
        if not v.strip():
            raise ValueError("name cannot be empty or whitespace")
        return v.strip()

    @field_validator("amount")
    @classmethod
    def amount_must_be_valid(cls, v):
        """Validate amount is reasonable."""
        if v < 0.01:
            raise ValueError("amount must be at least R$ 0.01")
        if v > 999999.99:
            raise ValueError("amount cannot exceed R$ 999999.99")
        return v


class ExpenseResponseDTO(BaseModel):
    """DTO for expense response."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str
    type: str
    amount: float
    status: str
    message: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("message", mode="before")
    @classmethod
    def set_message(cls, v, info):
        """Set message based on status if not provided."""
        if v is not None:
            return v
        status = info.data.get("status")
        if status == "aceita":
            return "Despesa registrada com sucesso"
        elif status == "recusada":
            return "Despesa foi recusada"
        return None
