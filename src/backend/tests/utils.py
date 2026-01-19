"""
Test utilities and helpers.

Provides common functions and fixtures for testing.
"""

import io
import uuid
from datetime import datetime, timezone
from typing import Any


def create_fake_image(
    format: str = "PNG",
    size: tuple[int, int] = (100, 100),
) -> bytes:
    """
    Create a minimal fake image for testing file uploads.

    Args:
        format: Image format (PNG, JPEG, etc.)
        size: Image dimensions (width, height)

    Returns:
        Bytes representing a minimal valid image
    """
    # Minimal PNG header (1x1 transparent pixel)
    if format.upper() == "PNG":
        return (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
            b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
    # Minimal JPEG (1x1 white pixel)
    elif format.upper() in ("JPEG", "JPG"):
        return (
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01"
            b"\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06"
            b"\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b"
            b"\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c"
            b"\x1c $.' \",#\x1c\x1c(7telefonino2telefoninoe5\\telefonino"
            b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
            b"\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01"
            b"\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04"
            b"\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02"
            b"\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}"
            b'\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x14'
            b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd5\xc0\x00"
            b"\x00\x00\xff\xd9"
        )
    else:
        # Return minimal PNG as fallback
        return create_fake_image("PNG", size)


def create_file_upload(
    filename: str = "test.png",
    content_type: str = "image/png",
    data: bytes | None = None,
) -> tuple[str, io.BytesIO, str]:
    """
    Create a file upload tuple for httpx/requests.

    Args:
        filename: Name of the file
        content_type: MIME type
        data: File content (defaults to fake image)

    Returns:
        Tuple of (filename, file_object, content_type)
    """
    if data is None:
        if "png" in content_type:
            data = create_fake_image("PNG")
        elif "jpeg" in content_type or "jpg" in content_type:
            data = create_fake_image("JPEG")
        else:
            data = b"test file content"

    return (filename, io.BytesIO(data), content_type)


def generate_uuid() -> str:
    """Generate a random UUID string."""
    return str(uuid.uuid4())


def generate_email(domain: str = "example.com") -> str:
    """Generate a random email address."""
    return f"user_{uuid.uuid4().hex[:8]}@{domain}"


def generate_username() -> str:
    """Generate a random username."""
    return f"user_{uuid.uuid4().hex[:12]}"


def generate_valid_password() -> str:
    """Generate a valid password that meets all requirements."""
    return f"ValidPass{uuid.uuid4().hex[:4]}123"


def generate_coordinates(
    lat_range: tuple[float, float] = (-90, 90),
    lon_range: tuple[float, float] = (-180, 180),
) -> tuple[float, float]:
    """
    Generate random coordinates within specified ranges.

    Args:
        lat_range: Min and max latitude
        lon_range: Min and max longitude

    Returns:
        Tuple of (latitude, longitude)
    """
    import random

    lat = random.uniform(lat_range[0], lat_range[1])
    lon = random.uniform(lon_range[0], lon_range[1])
    return (round(lat, 6), round(lon, 6))


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(
        self,
        status_code: int = 200,
        json_data: dict | None = None,
        text: str = "",
        headers: dict | None = None,
    ):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text
        self.headers = headers or {}

    def json(self) -> dict:
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


def assert_response_ok(response: Any, expected_status: int = 200):
    """Assert that a response has the expected status code."""
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}. "
        f"Response: {response.text}"
    )


def assert_response_error(
    response: Any,
    expected_status: int,
    expected_detail_contains: str | None = None,
):
    """Assert that a response is an error with expected status and optional detail check."""
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}"
    )

    if expected_detail_contains:
        data = response.json()
        detail = data.get("detail", "")
        assert expected_detail_contains.lower() in detail.lower(), (
            f"Expected detail to contain '{expected_detail_contains}', got '{detail}'"
        )


def create_auth_header(token: str) -> dict[str, str]:
    """Create authorization header dict from token."""
    return {"Authorization": f"Bearer {token}"}
