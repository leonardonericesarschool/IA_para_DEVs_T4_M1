"""Unit tests for PixKey entity"""
import pytest
from uuid import UUID, uuid4
from datetime import datetime
from src.entities.pix_key import PixKey
from src.entities import PixKeyType, PixKeyStatus, PixKeyValidationStatus
from src.exceptions import InvalidStatusTransitionError


@pytest.fixture
def sample_pix_key():
    """Fixture for creating a sample PixKey entity"""
    return PixKey(
        key_id=uuid4(),
        user_id=uuid4(),
        key_type=PixKeyType.EMAIL,
        key_value_hash="hash_of_email@example.com",
        key_value_masked="user***@example.com",
        alias="Personal Email",
        status=PixKeyStatus.ACTIVE
    )


class TestPixKeyInitialization:
    """Tests for PixKey entity initialization"""
    
    def test_create_with_required_fields(self):
        """Test PixKey creation with required fields only"""
        key_id = uuid4()
        user_id = uuid4()
        
        pix_key = PixKey(
            key_id=key_id,
            user_id=user_id,
            key_type=PixKeyType.CPF,
            key_value_hash="hash_cpf",
            key_value_masked="***.***.***-99"
        )
        
        assert pix_key.key_id == key_id
        assert pix_key.user_id == user_id
        assert pix_key.key_type == PixKeyType.CPF
        assert pix_key.status == PixKeyStatus.ACTIVE
        assert pix_key.validation_status == PixKeyValidationStatus.VALID
        assert pix_key.is_preferred is False
        assert pix_key.alias is None
    
    def test_create_with_all_fields(self):
        """Test PixKey creation with all fields"""
        key_id = uuid4()
        user_id = uuid4()
        now = datetime.utcnow()
        
        pix_key = PixKey(
            key_id=key_id,
            user_id=user_id,
            key_type=PixKeyType.PHONE,
            key_value_hash="hash_phone",
            key_value_masked="(11) 9****-1234",
            status=PixKeyStatus.INACTIVE,
            alias="Work Phone",
            is_preferred=True,
            validation_status=PixKeyValidationStatus.VALID,
            validation_error=None,
            pix_network_id="external-id-123",
            created_at=now,
            updated_at=now
        )
        
        assert pix_key.status == PixKeyStatus.INACTIVE
        assert pix_key.alias == "Work Phone"
        assert pix_key.is_preferred is True


class TestPixKeyStatusTransitions:
    """Tests for PixKey status state machine"""
    
    def test_deactivate_active_key(self, sample_pix_key):
        """Test deactivating an active key"""
        assert sample_pix_key.status == PixKeyStatus.ACTIVE
        
        sample_pix_key.deactivate()
        
        assert sample_pix_key.status == PixKeyStatus.INACTIVE
    
    def test_deactivate_already_inactive_key_raises_error(self, sample_pix_key):
        """Test deactivating an already inactive key raises error"""
        sample_pix_key.status = PixKeyStatus.INACTIVE
        
        with pytest.raises(InvalidStatusTransitionError) as exc_info:
            sample_pix_key.deactivate()
        
        assert "INACTIVE" in str(exc_info.value)
        assert "INACTIVE" in str(exc_info.value)
    
    def test_deactivate_resets_is_preferred(self, sample_pix_key):
        """Test deactivating a key resets is_preferred flag"""
        sample_pix_key.is_preferred = True
        
        sample_pix_key.deactivate()
        
        assert sample_pix_key.is_preferred is False
        assert sample_pix_key.status == PixKeyStatus.INACTIVE
    
    def test_deactivate_updates_timestamp(self, sample_pix_key):
        """Test deactivating updates the updated_at timestamp"""
        old_timestamp = sample_pix_key.updated_at
        
        # Small delay to ensure timestamp changes
        import time
        time.sleep(0.01)
        
        sample_pix_key.deactivate()
        
        assert sample_pix_key.updated_at > old_timestamp
    
    def test_activate_inactive_key(self, sample_pix_key):
        """Test activating an inactive key"""
        sample_pix_key.status = PixKeyStatus.INACTIVE
        
        sample_pix_key.activate()
        
        assert sample_pix_key.status == PixKeyStatus.ACTIVE
    
    def test_activate_already_active_key_raises_error(self, sample_pix_key):
        """Test activating an already active key raises error"""
        assert sample_pix_key.status == PixKeyStatus.ACTIVE
        
        with pytest.raises(InvalidStatusTransitionError):
            sample_pix_key.activate()
    
    def test_activate_updates_timestamp(self, sample_pix_key):
        """Test activating updates the updated_at timestamp"""
        sample_pix_key.status = PixKeyStatus.INACTIVE
        old_timestamp = sample_pix_key.updated_at
        
        import time
        time.sleep(0.01)
        
        sample_pix_key.activate()
        
        assert sample_pix_key.updated_at > old_timestamp


class TestPixKeyAlias:
    """Tests for PixKey alias management"""
    
    def test_update_alias_valid(self, sample_pix_key):
        """Test updating alias to valid value"""
        sample_pix_key.update_alias("New Alias")
        
        assert sample_pix_key.alias == "New Alias"
    
    def test_update_alias_to_none(self, sample_pix_key):
        """Test updating alias to None"""
        sample_pix_key.alias = "Some Alias"
        
        sample_pix_key.update_alias(None)
        
        assert sample_pix_key.alias is None
    
    def test_update_alias_too_long_raises_error(self, sample_pix_key):
        """Test updating alias with too long string raises error"""
        long_alias = "x" * 51
        
        with pytest.raises(ValueError) as exc_info:
            sample_pix_key.update_alias(long_alias)
        
        assert "50 characters" in str(exc_info.value)


class TestPixKeyPreference:
    """Tests for PixKey preferred marking"""
    
    def test_mark_as_preferred(self, sample_pix_key):
        """Test marking an active key as preferred"""
        assert sample_pix_key.is_preferred is False
        
        sample_pix_key.mark_as_preferred()
        
        assert sample_pix_key.is_preferred is True
    
    def test_mark_inactive_as_preferred_raises_error(self, sample_pix_key):
        """Test marking an inactive key as preferred raises error"""
        sample_pix_key.status = PixKeyStatus.INACTIVE
        
        with pytest.raises(ValueError) as exc_info:
            sample_pix_key.mark_as_preferred()
        
        assert "active" in str(exc_info.value).lower()
    
    def test_unmark_as_preferred(self, sample_pix_key):
        """Test unmarking key from preferred"""
        sample_pix_key.is_preferred = True
        
        sample_pix_key.unmark_as_preferred()
        
        assert sample_pix_key.is_preferred is False


class TestPixKeyToDict:
    """Tests for PixKey serialization"""
    
    def test_to_dict_without_hash(self, sample_pix_key):
        """Test converting PixKey to dict without hash"""
        result = sample_pix_key.to_dict(include_hash=False)
        
        assert "key_id" in result
        assert "key_value_hash" not in result
        assert result["key_type"] == "EMAIL"
        assert result["status"] == "ACTIVE"
    
    def test_to_dict_with_hash(self, sample_pix_key):
        """Test converting PixKey to dict with hash"""
        result = sample_pix_key.to_dict(include_hash=True)
        
        assert "key_value_hash" in result
        assert result["key_value_hash"] == "hash_of_email@example.com"
