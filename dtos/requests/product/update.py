"""
Product Update Request DTO.

This module defines the request DTO for updating products.
"""

from typing import Optional
from pydantic import field_validator

from dtos.requests.abstraction import IRequestDTO
from dtos.base import EnhancedBaseModel


class ProductUpdateRequestDTO(IRequestDTO, EnhancedBaseModel):
    """
    Request DTO for updating a product.
    
    Attributes:
        reference_number (str): Client-provided request tracking ID.
        name (str): Optional new name.
        description (str): Optional new description.
        is_active (bool): Optional active status.
    """
    
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    
    class Config:
        extra = "forbid"
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize name if provided."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Name cannot be empty")
        if len(v) > 255:
            raise ValueError("Name cannot exceed 255 characters")
        return v.strip()
