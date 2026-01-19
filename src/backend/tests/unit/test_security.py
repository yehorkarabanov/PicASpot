"""
Unit tests for security utilities.

Tests cover:
- JWT token creation and decoding
- Password hashing
- Verification tokens
"""

import uuid
from datetime import timedelta

from app.auth.security import (
    TokenType,
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class TestAccessToken:
    """Tests for JWT access token functions."""

    def test_create_access_token_default_expiry(self):
        """Token should be created with default expiry."""
        subject = str(uuid.uuid4())
        token = create_access_token(subject=subject)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_custom_expiry(self):
        """Token should be created with custom expiry."""
        subject = str(uuid.uuid4())
        expires_delta = timedelta(hours=2)
        token = create_access_token(subject=subject, expires_delta=expires_delta)

        assert token is not None

    def test_create_access_token_with_extra_data(self):
        """Token should include extra data."""
        subject = str(uuid.uuid4())
        extra_data = {"role": "admin", "permissions": ["read", "write"]}
        token = create_access_token(subject=subject, extra_data=extra_data)

        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["role"] == "admin"
        assert decoded["permissions"] == ["read", "write"]

    def test_decode_token_valid(self):
        """Valid token should be decoded successfully."""
        subject = str(uuid.uuid4())
        token = create_access_token(subject=subject)

        decoded = decode_token(token)

        assert decoded is not None
        assert decoded["sub"] == subject
        assert "exp" in decoded

    def test_decode_token_invalid(self):
        """Invalid token should return None."""
        decoded = decode_token("invalid-token")

        assert decoded is None

    def test_decode_token_expired(self):
        """Expired token should return None."""
        subject = str(uuid.uuid4())
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(subject=subject, expires_delta=expires_delta)

        decoded = decode_token(token)

        assert decoded is None

    def test_decode_token_tampered(self):
        """Tampered token should return None."""
        subject = str(uuid.uuid4())
        token = create_access_token(subject=subject)

        # Tamper with the token
        tampered_token = token[:-5] + "xxxxx"

        decoded = decode_token(tampered_token)

        assert decoded is None


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_get_password_hash_returns_string(self):
        """Password hash should be a string."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_different_each_time(self):
        """Same password should produce different hashes (due to salt)."""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Correct password should verify successfully."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Incorrect password should fail verification."""
        password = "TestPassword123"
        wrong_password = "WrongPassword456"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_input(self):
        """Empty password should fail verification."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False

    def test_verify_password_special_characters(self):
        """Password with special characters should work."""
        password = "P@$$w0rd!#%^&*()"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_unicode(self):
        """Password with unicode characters should work."""
        password = "Пароль123!日本語"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_long(self):
        """Password up to 72 bytes should work (bcrypt limit)."""
        # bcrypt has a 72 byte limit
        password = "A" * 60 + "B123"  # Within 72 bytes
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True


class TestTokenType:
    """Tests for TokenType enum."""

    def test_token_type_values(self):
        """All expected token types should exist."""
        assert TokenType.VERIFICATION == "verification"
        assert TokenType.PASSWORD_RESET == "password_reset"
        assert TokenType.USER_DELETION == "user_deletion"

    def test_token_type_is_string(self):
        """TokenType values should be strings."""
        for token_type in TokenType:
            assert isinstance(token_type.value, str)
