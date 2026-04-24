"""Pydantic schemas for PixKey API"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from src.utils import validate_cpf, validate_email, validate_phone
from src.entities import PixKeyType


class RegisterPixKeyRequest(BaseModel):
    """Request schema for registering a new Pix Key"""
    key_type: PixKeyType = Field(..., description="Type of Pix Key")
    key_value: Optional[str] = Field(None, description="Actual key value (null for RANDOM)")
    alias: Optional[str] = Field(None, max_length=50, description="User-friendly name")
    
    @field_validator('key_type')
    @classmethod
    def validate_key_type(cls, v: PixKeyType) -> PixKeyType:
        """Validate key_type is a valid enum value"""
        if v not in [PixKeyType.CPF, PixKeyType.EMAIL, PixKeyType.PHONE, PixKeyType.RANDOM]:
            raise ValueError('Invalid key_type')
        return v
    
    @field_validator('key_value')
    @classmethod
    def validate_key_value(cls, v: Optional[str], info) -> Optional[str]:
        """Validate key_value based on key_type"""
        key_type = info.data.get('key_type')
        
        if key_type == PixKeyType.RANDOM:
            if v is not None:
                raise ValueError('key_value must be null for RANDOM')
            return v
        
        if key_type in [PixKeyType.CPF, PixKeyType.EMAIL, PixKeyType.PHONE]:
            if not v:
                raise ValueError(f'key_value required for {key_type}')
            
            if key_type == PixKeyType.CPF:
                is_valid, error = validate_cpf(v)
                if not is_valid:
                    raise ValueError(error or 'Invalid CPF')
            elif key_type == PixKeyType.EMAIL:
                is_valid, error = validate_email(v)
                if not is_valid:
                    raise ValueError(error or 'Invalid email')
            elif key_type == PixKeyType.PHONE:
                is_valid, error = validate_phone(v)
                if not is_valid:
                    raise ValueError(error or 'Invalid phone')
        
        return v


class PixKeyResponse(BaseModel):
    """Response schema for PixKey"""
    key_id: str
    key_type: str
    key_value_masked: str
    key_value: Optional[str] = None  # Only in registration response
    status: str
    alias: Optional[str] = None
    is_preferred: bool
    validation_status: str
    created_at: str
    updated_at: str
    message: Optional[str] = None


class PixKeyListResponse(BaseModel):
    """Response schema for list of PixKeys"""
    items: List[PixKeyResponse]
    total: int
    page: int
    page_size: int
    
    @property
    def total_pages(self) -> int:
        """Calculate total pages"""
        return (self.total + self.page_size - 1) // self.page_size


class ErrorDetail(BaseModel):
    """Error detail response"""
    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: ErrorDetail
