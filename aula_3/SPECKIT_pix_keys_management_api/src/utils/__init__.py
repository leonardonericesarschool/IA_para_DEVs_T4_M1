"""Validation utilities for different Pix Key types"""
import re
from typing import Tuple, Optional


def validate_cpf(cpf: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Brazilian CPF format (11 digits)
    
    Args:
        cpf: CPF string (digits only or with dots/dashes)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Remove common formatting
    clean_cpf = re.sub(r'\D', '', cpf)
    
    if not clean_cpf:
        return False, "CPF cannot be empty"
    
    if len(clean_cpf) != 11:
        return False, f"CPF must have 11 digits, got {len(clean_cpf)}"
    
    if not clean_cpf.isdigit():
        return False, "CPF must contain only digits"
    
    if clean_cpf == clean_cpf[0] * 11:  # All same digits is invalid
        return False, "Invalid CPF: all digits are the same"
    
    # Basic checksum validation (simplified, not full algorithm)
    # This is a MVP validation; full CPF validation can be added later
    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format
    
    Args:
        email: Email string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email cannot be empty"
    
    if len(email) > 254:
        return False, f"Email too long (max 254 chars, got {len(email)})"
    
    # RFC 5322 simplified regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Brazilian phone number format (11 digits: 2-digit area code + 9-digit number)
    
    Args:
        phone: Phone string (digits only or with formatting)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Remove common formatting
    clean_phone = re.sub(r'\D', '', phone)
    
    if not clean_phone:
        return False, "Phone cannot be empty"
    
    if len(clean_phone) != 11:
        return False, f"Phone must have 11 digits (area code + number), got {len(clean_phone)}"
    
    if not clean_phone.isdigit():
        return False, "Phone must contain only digits"
    
    # Basic validation: area code (first 2 digits) must be 11-99
    area_code = int(clean_phone[:2])
    if area_code < 11 or area_code > 99:
        return False, f"Invalid area code: {area_code:02d}"
    
    # First digit of number (3rd digit) must be 6, 7, 8, or 9 for mobile
    first_digit = int(clean_phone[2])
    if first_digit not in [6, 7, 8, 9]:
        return False, f"Invalid phone number first digit: {first_digit} (must be 6-9)"
    
    return True, None


def mask_cpf(cpf: str) -> str:
    """Mask CPF for display: XXX.XXX.XXX-99"""
    clean_cpf = re.sub(r'\D', '', cpf)
    if len(clean_cpf) < 11:
        return cpf
    return f"{'*' * 3}.{'*' * 3}.{'*' * 3}-{clean_cpf[-2:]}"


def mask_email(email: str) -> str:
    """Mask email for display: user***@example.com"""
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 3:
        masked_local = '*' * len(local)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask phone for display: (XX) 9****-***9"""
    clean_phone = re.sub(r'\D', '', phone)
    if len(clean_phone) < 11:
        return phone
    
    area_code = clean_phone[:2]
    return f"({area_code}) 9****-{clean_phone[-4:]}"


def mask_random_key(key: str) -> str:
    """Mask random key for display: XXXX-XXXX-XXXX-99ab"""
    if len(key) < 8:
        return '*' * len(key)
    return '*' * (len(key) - 4) + key[-4:]
