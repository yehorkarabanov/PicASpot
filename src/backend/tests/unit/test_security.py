"""
Example unit tests for security functions.

These tests demonstrate how to test utility functions in isolation
using mocks and without database dependencies.
"""

from datetime import timedelta

import pytest

from app.auth.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_password_hash_generation(self):
        """Test that password hashing produces a valid hash."""
        password = "mySecurePassword123!"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password  # Hash should be different from plain password
        assert len(hashed) > 0

    def test_password_verification_success(self):
        """Test successful password verification."""
        password = "mySecurePassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test failed password verification with wrong password."""
        password = "mySecurePassword123!"
        wrong_password = "wrongPassword456!"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "mySecurePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to random salt
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token creation and decoding."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(subject=user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_with_extra_data(self):
        """Test JWT token creation with additional claims."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        extra_data = {"role": "admin", "scope": "full"}
        token = create_access_token(subject=user_id, extra_data=extra_data)

        decoded = decode_token(token)

        assert decoded is not None
        assert decoded["sub"] == user_id
        assert decoded["role"] == "admin"
        assert decoded["scope"] == "full"

    def test_create_token_with_custom_expiry(self):
        """Test JWT token creation with custom expiration."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        expires_delta = timedelta(minutes=30)
        token = create_access_token(subject=user_id, expires_delta=expires_delta)

        assert token is not None

        decoded = decode_token(token)
        assert decoded is not None
        assert "exp" in decoded

    def test_decode_valid_token(self):
        """Test decoding a valid JWT token."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(subject=user_id)

        decoded = decode_token(token)

        assert decoded is not None
        assert decoded["sub"] == user_id
        assert "exp" in decoded

    def test_decode_invalid_token(self):
        """Test decoding an invalid JWT token."""
        invalid_token = "invalid.token.string"

        decoded = decode_token(invalid_token)

        assert decoded is None

    def test_token_contains_expiry(self):
        """Test that token contains expiry claim."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(subject=user_id)

        decoded = decode_token(token)

        assert "exp" in decoded
        assert isinstance(decoded["exp"], (int, float))


@pytest.mark.unit
class TestVerificationTokens:
    """Test verification token creation and validation."""

    @pytest.mark.asyncio
    async def test_create_verification_token_no_redis(self):
        """Test creating verification token without Redis storage."""
        from app.auth.security import TokenType, create_verification_token

        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # Create token without Redis
        token = await create_verification_token(
            user_id, TokenType.VERIFICATION, use_redis=False
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_decode_verification_token_no_redis(self):
        """Test decoding verification token without Redis validation."""
        from app.auth.security import (
            TokenType,
            create_verification_token,
            decode_verification_token,
        )

        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # Create and decode token
        token = await create_verification_token(
            user_id, TokenType.VERIFICATION, use_redis=False
        )

        decoded = await decode_verification_token(token, use_redis=False)

        assert decoded is not None
        assert decoded["user_id"] == user_id
        assert decoded["type"] == TokenType.VERIFICATION.value


# Pytest markers for easy test filtering
pytestmark = pytest.mark.unit
