"""
Unit tests for schema validation and serialization.

Tests cover:
- Pydantic schema validation
- Field constraints
- Custom validators
"""

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.auth.schemas import UserCreate, UserLogin, UserResetPassword
from app.user.schemas import UserResponse, UserUpdate, UserUpdatePassword


class TestUserCreateSchema:
    """Tests for UserCreate schema."""

    def test_valid_user_create(self):
        """Valid user data should pass validation."""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="ValidPass123",
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "ValidPass123"

    def test_password_minimum_length(self):
        """Password shorter than 8 characters should fail."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="Short1",
            )
        assert "password" in str(exc_info.value).lower()

    def test_password_requires_uppercase(self):
        """Password without uppercase should fail."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="lowercase123",
            )

    def test_password_requires_number(self):
        """Password without number should fail."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="NoNumbersHere",
            )

    def test_invalid_email_format(self):
        """Invalid email should fail validation."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="not-an-email",
                password="ValidPass123",
            )

    def test_missing_username(self):
        """Missing username should fail validation."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="ValidPass123",
            )


class TestUserLoginSchema:
    """Tests for UserLogin schema."""

    def test_valid_login(self):
        """Valid login data should pass."""
        login = UserLogin(
            username="testuser",
            password="ValidPass123",
        )
        assert login.username == "testuser"

    def test_login_with_email(self):
        """Login with email in username field should pass."""
        login = UserLogin(
            username="test@example.com",
            password="ValidPass123",
        )
        assert login.username == "test@example.com"

    def test_password_minimum_length(self):
        """Password shorter than 8 characters should fail."""
        with pytest.raises(ValidationError):
            UserLogin(
                username="testuser",
                password="short",
            )


class TestUserUpdateSchema:
    """Tests for UserUpdate schema."""

    def test_update_username_only(self):
        """Updating only username should work."""
        update = UserUpdate(username="newname")
        assert update.username == "newname"
        assert update.email is None

    def test_update_email_only(self):
        """Updating only email should work."""
        update = UserUpdate(email="new@example.com")
        assert update.email == "new@example.com"
        assert update.username is None

    def test_update_both_fields(self):
        """Updating both fields should work."""
        update = UserUpdate(username="newname", email="new@example.com")
        assert update.username == "newname"
        assert update.email == "new@example.com"

    def test_empty_update(self):
        """Empty update (no changes) should be valid."""
        update = UserUpdate()
        assert update.username is None
        assert update.email is None

    def test_invalid_email(self):
        """Invalid email format should fail."""
        with pytest.raises(ValidationError):
            UserUpdate(email="invalid")


class TestUserUpdatePasswordSchema:
    """Tests for UserUpdatePassword schema."""

    def test_valid_password_update(self):
        """Valid password update should pass."""
        update = UserUpdatePassword(
            password="CurrentPass123",
            new_password="NewPassword456",
        )
        assert update.password == "CurrentPass123"
        assert update.new_password == "NewPassword456"

    def test_current_password_too_short(self):
        """Current password shorter than 8 chars should fail."""
        with pytest.raises(ValidationError):
            UserUpdatePassword(
                password="short",
                new_password="ValidNew123",
            )

    def test_new_password_too_short(self):
        """New password shorter than 8 chars should fail."""
        with pytest.raises(ValidationError):
            UserUpdatePassword(
                password="ValidCurrent123",
                new_password="short",
            )


class TestUserResetPasswordSchema:
    """Tests for UserResetPassword schema."""

    def test_valid_reset(self):
        """Valid reset data should pass."""
        reset = UserResetPassword(
            password="NewPassword123",
            token="valid-token-string",
        )
        assert reset.password == "NewPassword123"
        assert reset.token == "valid-token-string"

    def test_password_too_short(self):
        """Password shorter than 8 chars should fail."""
        with pytest.raises(ValidationError):
            UserResetPassword(
                password="short",
                token="valid-token",
            )

    def test_missing_token(self):
        """Missing token should fail."""
        with pytest.raises(ValidationError):
            UserResetPassword(password="ValidPass123")


class TestAreaSchemas:
    """Tests for Area schemas."""

    def test_area_name_validation(self):
        """Area name constraints should be enforced."""
        from app.area.schemas import AreaBase

        # Valid name
        area = AreaBase(name="Valid Area Name")
        assert area.name == "Valid Area Name"

        # Name too long (if max_length is 255)
        with pytest.raises(ValidationError):
            AreaBase(name="A" * 256)

    def test_area_description_optional(self):
        """Area description should be optional."""
        from app.area.schemas import AreaBase

        area = AreaBase(name="Test Area")
        assert area.description is None

        area_with_desc = AreaBase(name="Test Area", description="A description")
        assert area_with_desc.description == "A description"


class TestLandmarkSchemas:
    """Tests for Landmark schemas."""

    def test_coordinate_validation(self):
        """Coordinates should be within valid ranges."""
        from app.landmark.schemas import LandmarkBase

        # Valid coordinates
        landmark = LandmarkBase(
            name="Test",
            latitude=45.0,
            longitude=-75.0,
        )
        assert landmark.latitude == 45.0
        assert landmark.longitude == -75.0

    def test_latitude_range(self):
        """Latitude should be between -90 and 90."""
        from app.landmark.schemas import LandmarkBase

        with pytest.raises(ValidationError):
            LandmarkBase(name="Test", latitude=91.0, longitude=0.0)

        with pytest.raises(ValidationError):
            LandmarkBase(name="Test", latitude=-91.0, longitude=0.0)

    def test_longitude_range(self):
        """Longitude should be between -180 and 180."""
        from app.landmark.schemas import LandmarkBase

        with pytest.raises(ValidationError):
            LandmarkBase(name="Test", latitude=0.0, longitude=181.0)

        with pytest.raises(ValidationError):
            LandmarkBase(name="Test", latitude=0.0, longitude=-181.0)

    def test_radius_validation(self):
        """Radius values should be within valid ranges."""
        from app.landmark.schemas import LandmarkBase

        # Valid radius
        landmark = LandmarkBase(
            name="Test",
            latitude=0.0,
            longitude=0.0,
            unlock_radius_meters=500,
            photo_radius_meters=100,
        )
        assert landmark.unlock_radius_meters == 500
        assert landmark.photo_radius_meters == 100

        # Invalid unlock radius (too small)
        with pytest.raises(ValidationError):
            LandmarkBase(
                name="Test",
                latitude=0.0,
                longitude=0.0,
                unlock_radius_meters=0,
            )

        # Invalid unlock radius (too large)
        with pytest.raises(ValidationError):
            LandmarkBase(
                name="Test",
                latitude=0.0,
                longitude=0.0,
                unlock_radius_meters=20000,
            )
