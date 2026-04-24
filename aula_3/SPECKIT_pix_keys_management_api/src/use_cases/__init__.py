"""Register Pix Key use case"""
import hashlib
from typing import Tuple
from uuid import UUID, uuid4
from src.entities.pix_key import PixKey
from src.entities import PixKeyType, PixKeyStatus, PixKeyAuditOperation
from src.exceptions import DuplicateKeyError, MaxKeysExceededError, ValidationError
from src.repositories import PixKeyRepository, PixKeyAuditRepository
from src.utils import validate_cpf, validate_email, validate_phone, mask_cpf, mask_email, mask_phone, mask_random_key
from src.config import get_settings


class RegisterPixKeyUseCase:
    """
    Use case for registering a new Pix Key
    
    Business logic:
    1. Validate key format
    2. Check for duplicates
    3. Check max keys limit
    4. Create PixKey entity
    5. Persist to repository
    6. Create audit log
    """
    
    def __init__(
        self,
        pix_key_repository: PixKeyRepository,
        audit_repository: PixKeyAuditRepository
    ):
        self.pix_key_repo = pix_key_repository
        self.audit_repo = audit_repository
        self.settings = get_settings()
    
    async def execute(
        self,
        user_id: UUID,
        key_type: PixKeyType,
        key_value: str,
        alias: str = None
    ) -> Tuple[PixKey, str]:
        """
        Execute the register Pix Key use case
        
        Args:
            user_id: ID of user registering the key
            key_type: Type of key (CPF, EMAIL, PHONE, RANDOM)
            key_value: The actual key value (null for RANDOM type)
            alias: Optional user-friendly name for the key
            
        Returns:
            Tuple of (PixKey entity, plaintext_key_value)
            The plaintext_key_value is returned for one-time display to user
            
        Raises:
            ValidationError: Invalid key format
            DuplicateKeyError: Key already registered
            MaxKeysExceededError: User exceeded max keys limit
        """
        
        # Generate or validate key value
        if key_type == PixKeyType.RANDOM:
            plaintext_key = str(uuid4())
        else:
            plaintext_key = key_value
            self._validate_key_format(key_type, plaintext_key)
        
        # Hash the key for storage
        key_hash = self._hash_key(plaintext_key)
        
        # Check for duplicates
        existing_key = await self.pix_key_repo.get_by_hash(user_id, key_hash)
        if existing_key:
            # Handle both dict and object returns
            key_id = existing_key.get("key_id") if isinstance(existing_key, dict) else existing_key.key_id
            status = existing_key.get("status") if isinstance(existing_key, dict) else existing_key.status
            raise DuplicateKeyError(
                key_id=key_id,
                status=status
            )
        
        # Check max keys limit
        current_count = await self.pix_key_repo.count_for_user(user_id)
        if current_count >= self.settings.max_pix_keys_per_user:
            raise MaxKeysExceededError(
                max_allowed=self.settings.max_pix_keys_per_user,
                current_count=current_count
            )
        
        # Generate masked display
        masked_key = self._mask_key(key_type, plaintext_key)
        
        # Create PixKey entity
        key_id = uuid4()
        pix_key = PixKey(
            key_id=key_id,
            user_id=user_id,
            key_type=key_type,
            key_value_hash=key_hash,
            key_value_masked=masked_key,
            status=PixKeyStatus.ACTIVE,
            alias=alias
        )
        
        # Persist to repository
        created_data = await self.pix_key_repo.create(
            user_id=user_id,
            key_type=key_type,
            key_value_hash=key_hash,
            key_value_masked=masked_key,
            alias=alias,
            validation_status="VALID"
        )
        
        # Create audit log
        await self.audit_repo.create_audit_log(
            key_id=key_id,
            user_id=user_id,
            operation=PixKeyAuditOperation.REGISTERED,
            status="SUCCESS",
            details={
                "key_type": key_type.value,
                "alias": alias
            }
        )
        
        return pix_key, plaintext_key
    
    @staticmethod
    def _validate_key_format(key_type: PixKeyType, key_value: str) -> None:
        """
        Validate key format based on type
        
        Raises:
            ValidationError: If key format is invalid
        """
        if key_type == PixKeyType.CPF:
            is_valid, error = validate_cpf(key_value)
            if not is_valid:
                raise ValidationError(
                    message=error or "Invalid CPF format",
                    details={"field": "key_value", "error": error}
                )
        
        elif key_type == PixKeyType.EMAIL:
            is_valid, error = validate_email(key_value)
            if not is_valid:
                raise ValidationError(
                    message=error or "Invalid email format",
                    details={"field": "key_value", "error": error}
                )
        
        elif key_type == PixKeyType.PHONE:
            is_valid, error = validate_phone(key_value)
            if not is_valid:
                raise ValidationError(
                    message=error or "Invalid phone format",
                    details={"field": "key_value", "error": error}
                )
    
    @staticmethod
    def _hash_key(key_value: str) -> str:
        """
        Hash key value for storage
        
        Uses SHA-256 to create a one-way hash of the key for storage.
        The original key is never stored in the database.
        """
        return hashlib.sha256(key_value.encode()).hexdigest()
    
    @staticmethod
    def _mask_key(key_type: PixKeyType, key_value: str) -> str:
        """
        Create masked display of key for non-sensitive contexts
        
        The masked version is shown everywhere except in the registration response.
        """
        if key_type == PixKeyType.CPF:
            return mask_cpf(key_value)
        elif key_type == PixKeyType.EMAIL:
            return mask_email(key_value)
        elif key_type == PixKeyType.PHONE:
            return mask_phone(key_value)
        elif key_type == PixKeyType.RANDOM:
            return mask_random_key(key_value)
        else:
            return key_value  # fallback
