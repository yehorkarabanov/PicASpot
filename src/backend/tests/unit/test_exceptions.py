"""
Unit tests for core exceptions.

Tests cover:
- Exception status codes
- Exception messages
- Exception headers
"""

import pytest
from fastapi import status

from app.core.exceptions import (
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    UnprocessableEntityError,
)


class TestNotFoundError:
    """Tests for NotFoundError exception."""

    def test_status_code(self):
        """NotFoundError should have 404 status code."""
        error = NotFoundError("Resource not found")
        assert error.status_code == status.HTTP_404_NOT_FOUND

    def test_detail_message(self):
        """NotFoundError should preserve detail message."""
        message = "User not found"
        error = NotFoundError(message)
        assert error.detail == message

    def test_is_http_exception(self):
        """NotFoundError should be an HTTPException."""
        from fastapi import HTTPException

        error = NotFoundError("Not found")
        assert isinstance(error, HTTPException)


class TestUnauthorizedError:
    """Tests for UnauthorizedError exception."""

    def test_status_code(self):
        """UnauthorizedError should have 401 status code."""
        error = UnauthorizedError("Not authorized")
        assert error.status_code == status.HTTP_401_UNAUTHORIZED

    def test_detail_message(self):
        """UnauthorizedError should preserve detail message."""
        message = "Invalid credentials"
        error = UnauthorizedError(message)
        assert error.detail == message


class TestAuthenticationError:
    """Tests for AuthenticationError exception."""

    def test_status_code(self):
        """AuthenticationError should have 401 status code."""
        error = AuthenticationError("Authentication failed")
        assert error.status_code == status.HTTP_401_UNAUTHORIZED

    def test_www_authenticate_header(self):
        """AuthenticationError should include WWW-Authenticate header."""
        error = AuthenticationError("Token expired")
        assert error.headers is not None
        assert error.headers.get("WWW-Authenticate") == "Bearer"


class TestForbiddenError:
    """Tests for ForbiddenError exception."""

    def test_status_code(self):
        """ForbiddenError should have 403 status code."""
        error = ForbiddenError("Access denied")
        assert error.status_code == status.HTTP_403_FORBIDDEN

    def test_detail_message(self):
        """ForbiddenError should preserve detail message."""
        message = "You don't have permission"
        error = ForbiddenError(message)
        assert error.detail == message


class TestBadRequestError:
    """Tests for BadRequestError exception."""

    def test_status_code(self):
        """BadRequestError should have 400 status code."""
        error = BadRequestError("Invalid data")
        assert error.status_code == status.HTTP_400_BAD_REQUEST

    def test_detail_message(self):
        """BadRequestError should preserve detail message."""
        message = "Email already exists"
        error = BadRequestError(message)
        assert error.detail == message


class TestUnprocessableEntityError:
    """Tests for UnprocessableEntityError exception."""

    def test_status_code(self):
        """UnprocessableEntityError should have 422 status code."""
        error = UnprocessableEntityError("Validation failed")
        assert error.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_detail_message(self):
        """UnprocessableEntityError should preserve detail message."""
        message = "Invalid field format"
        error = UnprocessableEntityError(message)
        assert error.detail == message


class TestExceptionRaising:
    """Tests for raising exceptions."""

    def test_raise_not_found(self):
        """Should be able to raise NotFoundError."""
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError("Item not found")

        assert exc_info.value.status_code == 404

    def test_raise_bad_request(self):
        """Should be able to raise BadRequestError."""
        with pytest.raises(BadRequestError) as exc_info:
            raise BadRequestError("Bad request")

        assert exc_info.value.status_code == 400

    def test_raise_forbidden(self):
        """Should be able to raise ForbiddenError."""
        with pytest.raises(ForbiddenError) as exc_info:
            raise ForbiddenError("Forbidden")

        assert exc_info.value.status_code == 403

    def test_raise_authentication_error(self):
        """Should be able to raise AuthenticationError."""
        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError("Not authenticated")

        assert exc_info.value.status_code == 401
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"
