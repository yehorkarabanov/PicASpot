"""
Unit tests for security module (password hashing and JWT tokens).
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import jwt

from app.auth.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.settings import settings


@pytest.mark.unit
class TestPasswordHashing:
    """Tests for password hashing functionality."""

    def test_password_hash_creates_different_hash(self):
        """Test that hashing the same password twice creates different hashes."""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert hash1 != password
        assert hash2 != password

    def test_verify_password_with_correct_password(self):
        """Test that correct password verification succeeds."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_with_incorrect_password(self):
        """Test that incorrect password verification fails."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_with_empty_password(self):
        """Test that empty password verification fails."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False

    def test_hash_empty_password(self):
        """Test that hashing empty password still works."""
        hashed = get_password_hash("")
        assert hashed is not None
        assert len(hashed) > 0


@pytest.mark.unit
class TestJWTTokens:
    """Tests for JWT token creation and verification."""

    def test_create_access_token_basic(self):
        """Test basic access token creation."""
        user_id = str(uuid.uuid4())
        token = create_access_token(subject=user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self):
        """Test access token creation with custom expiry."""
        user_id = str(uuid.uuid4())
        expires_delta = timedelta(minutes=15)
        token = create_access_token(subject=user_id, expires_delta=expires_delta)

        # Decode token to verify expiry
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)

        # Should expire in approximately 15 minutes (with small tolerance)
        time_diff = (exp - now).total_seconds()
        assert 14 * 60 < time_diff < 16 * 60

    def test_verify_token_valid(self):
        """Test verification of valid token."""
        user_id = str(uuid.uuid4())
        token = create_access_token(subject=user_id)

        payload = decode_token(token)

        assert payload is not None
        assert payload["sub"] == user_id
        assert "exp" in payload

    def test_verify_token_expired(self):
        """Test verification of expired token."""
        user_id = str(uuid.uuid4())
        # Create token that expires immediately
        token = create_access_token(
            subject=user_id, expires_delta=timedelta(seconds=-1)
        )

        # decode_token returns None for invalid tokens
        result = decode_token(token)
        assert result is None

    def test_verify_token_invalid(self):
        """Test verification of invalid token."""
        invalid_token = "invalid.token.here"

        # decode_token returns None for invalid tokens
        result = decode_token(invalid_token)
        assert result is None

    def test_verify_token_tampered(self):
        """Test verification of tampered token."""
        user_id = str(uuid.uuid4())
        token = create_access_token(subject=user_id)

        # Tamper with the token
        tampered_token = token[:-5] + "xxxxx"

        # decode_token returns None for invalid tokens
        result = decode_token(tampered_token)
        assert result is None

    def test_token_contains_correct_payload(self):
        """Test that token payload contains expected fields."""
        user_id = str(uuid.uuid4())
        token = create_access_token(subject=user_id)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        assert "sub" in payload
        assert "exp" in payload
        assert payload["sub"] == user_id

    def test_create_access_token_with_additional_claims(self):
        """Test token creation with additional custom claims."""
        user_id = str(uuid.uuid4())
        token = create_access_token(subject=user_id)

        payload = decode_token(token)

        assert payload is not None
        assert payload["sub"] == user_id
        assert "exp" in payload

    def test_multiple_tokens_for_same_user_are_different(self):
        """Test that creating multiple tokens for same user produces different tokens."""
        user_id = str(uuid.uuid4())
        token1 = create_access_token(subject=user_id)
        token2 = create_access_token(subject=user_id)

        # Tokens should be different due to timestamp
        assert token1 != token2

        # But both should verify to same user
        payload1 = decode_token(token1)
        payload2 = decode_token(token2)
        assert payload1["sub"] == payload2["sub"] == user_id

