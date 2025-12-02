"""
Custom assertion helpers for testing.

This module provides specialized assertion functions for validating
API responses, pagination, and domain-specific data structures.
"""

from typing import Any


def assert_valid_uuid(value: str) -> None:
    """
    Assert that a string is a valid UUID.

    Args:
        value: String to validate

    Raises:
        AssertionError: If value is not a valid UUID

    Example:
        assert_valid_uuid(user.id)
    """
    import uuid

    try:
        uuid.UUID(str(value))
    except (ValueError, AttributeError):
        raise AssertionError(f"'{value}' is not a valid UUID") from None


def assert_successful_response(response, expected_status: int = 200) -> None:
    """
    Assert that an API response is successful.

    Args:
        response: HTTP response object
        expected_status: Expected HTTP status code

    Raises:
        AssertionError: If response status doesn't match

    Example:
        response = await client.get("/api/v1/users/me")
        assert_successful_response(response, 200)
    """
    assert response.status_code == expected_status, (
        f"Expected {expected_status}, got {response.status_code}. Response: {response.text}"
    )


def assert_error_response(
    response,
    expected_status: int,
    expected_detail: str | None = None,
) -> None:
    """
    Assert that an API response is an error with expected details.

    Args:
        response: HTTP response object
        expected_status: Expected HTTP status code
        expected_detail: Optional expected error detail message

    Raises:
        AssertionError: If response doesn't match expectations

    Example:
        response = await client.get("/api/v1/users/invalid-id")
        assert_error_response(response, 404, "User not found")
    """
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}"
    )

    if expected_detail:
        data = response.json()
        assert "detail" in data, "Response does not contain 'detail' field"
        assert expected_detail in data["detail"], (
            f"Expected detail to contain '{expected_detail}', got '{data['detail']}'"
        )


def assert_validation_error(response, field_name: str | None = None) -> None:
    """
    Assert that response is a validation error (422).

    Args:
        response: HTTP response object
        field_name: Optional field name that should have an error

    Raises:
        AssertionError: If response is not a validation error

    Example:
        response = await client.post("/api/v1/users", json={"invalid": "data"})
        assert_validation_error(response, "email")
    """
    assert response.status_code == 422, (
        f"Expected 422 Unprocessable Entity, got {response.status_code}"
    )

    data = response.json()
    assert "detail" in data, "Validation error must contain 'detail'"

    if field_name:
        errors = data["detail"]
        field_errors = [err for err in errors if field_name in str(err.get("loc", []))]
        assert field_errors, f"No validation error found for field '{field_name}'"


def assert_pagination_response(
    data: dict,
    expected_total: int | None = None,
    expected_page: int = 1,
    expected_size: int | None = None,
) -> None:
    """
    Assert that a response contains valid pagination structure.

    Args:
        data: Response data dictionary
        expected_total: Expected total number of items (optional)
        expected_page: Expected current page number
        expected_size: Expected page size (optional)

    Raises:
        AssertionError: If pagination structure is invalid

    Example:
        response = await client.get("/api/v1/landmarks?page=1&size=10")
        data = response.json()
        assert_pagination_response(data, expected_page=1, expected_size=10)
    """
    assert "items" in data, "Pagination response must contain 'items'"
    assert "total" in data, "Pagination response must contain 'total'"
    assert "page" in data, "Pagination response must contain 'page'"
    assert "size" in data, "Pagination response must contain 'size'"
    assert "pages" in data, "Pagination response must contain 'pages'"

    assert isinstance(data["items"], list), "'items' must be a list"
    assert isinstance(data["total"], int), "'total' must be an integer"
    assert isinstance(data["page"], int), "'page' must be an integer"
    assert isinstance(data["size"], int), "'size' must be an integer"
    assert isinstance(data["pages"], int), "'pages' must be an integer"

    if expected_total is not None:
        assert data["total"] == expected_total, (
            f"Expected total={expected_total}, got {data['total']}"
        )

    assert data["page"] == expected_page, (
        f"Expected page={expected_page}, got {data['page']}"
    )

    if expected_size is not None:
        assert data["size"] == expected_size, (
            f"Expected size={expected_size}, got {data['size']}"
        )

    # Validate that items count doesn't exceed page size
    assert len(data["items"]) <= data["size"], (
        f"Items count ({len(data['items'])}) exceeds page size ({data['size']})"
    )


def assert_geojson_point(geojson: dict) -> None:
    """
    Assert that a dictionary is a valid GeoJSON Point.

    Args:
        geojson: Dictionary to validate

    Raises:
        AssertionError: If not a valid GeoJSON Point

    Example:
        assert_geojson_point(landmark["location"])
    """
    assert isinstance(geojson, dict), "GeoJSON must be a dictionary"
    assert geojson.get("type") == "Point", "GeoJSON type must be 'Point'"
    assert "coordinates" in geojson, "GeoJSON must contain 'coordinates'"

    coords = geojson["coordinates"]
    assert isinstance(coords, list), "Coordinates must be a list"
    assert len(coords) == 2, "Point coordinates must have 2 elements [lon, lat]"

    lon, lat = coords
    assert isinstance(lon, (int, float)), "Longitude must be a number"
    assert isinstance(lat, (int, float)), "Latitude must be a number"
    assert -180 <= lon <= 180, f"Longitude {lon} out of range [-180, 180]"
    assert -90 <= lat <= 90, f"Latitude {lat} out of range [-90, 90]"


def assert_geojson_polygon(geojson: dict) -> None:
    """
    Assert that a dictionary is a valid GeoJSON Polygon.

    Args:
        geojson: Dictionary to validate

    Raises:
        AssertionError: If not a valid GeoJSON Polygon

    Example:
        assert_geojson_polygon(area["geometry"])
    """
    assert isinstance(geojson, dict), "GeoJSON must be a dictionary"
    assert geojson.get("type") == "Polygon", "GeoJSON type must be 'Polygon'"
    assert "coordinates" in geojson, "GeoJSON must contain 'coordinates'"

    coords = geojson["coordinates"]
    assert isinstance(coords, list), "Coordinates must be a list"
    assert len(coords) >= 1, "Polygon must have at least one ring"

    for ring in coords:
        assert isinstance(ring, list), "Each ring must be a list"
        assert len(ring) >= 4, "Ring must have at least 4 points (closed)"

        # Verify ring is closed (first and last points are same)
        assert ring[0] == ring[-1], (
            "Ring must be closed (first and last points must be identical)"
        )

        # Validate each coordinate
        for coord in ring:
            assert len(coord) == 2, "Each coordinate must be [lon, lat]"
            lon, lat = coord
            assert -180 <= lon <= 180, f"Longitude {lon} out of range"
            assert -90 <= lat <= 90, f"Latitude {lat} out of range"


def assert_has_keys(data: dict, required_keys: list[str]) -> None:
    """
    Assert that a dictionary contains all required keys.

    Args:
        data: Dictionary to check
        required_keys: List of required key names

    Raises:
        AssertionError: If any required key is missing

    Example:
        assert_has_keys(user_data, ["id", "username", "email"])
    """
    missing_keys = [key for key in required_keys if key not in data]
    assert not missing_keys, f"Missing required keys: {', '.join(missing_keys)}"


def assert_timestamp_format(timestamp: str) -> None:
    """
    Assert that a string is a valid ISO 8601 timestamp.

    Args:
        timestamp: String to validate

    Raises:
        AssertionError: If not a valid timestamp

    Example:
        assert_timestamp_format(user["created_at"])
    """
    from datetime import datetime

    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise AssertionError(f"'{timestamp}' is not a valid ISO 8601 timestamp") from None


def assert_response_matches_model(
    response_data: dict,
    model_instance: Any,
    fields: list[str],
) -> None:
    """
    Assert that response data matches model instance for specified fields.

    Args:
        response_data: Response data dictionary
        model_instance: Database model instance
        fields: List of field names to compare

    Raises:
        AssertionError: If any field doesn't match

    Example:
        assert_response_matches_model(
            response_data,
            user,
            ["id", "username", "email"]
        )
    """
    for field in fields:
        assert field in response_data, f"Field '{field}' missing from response"

        model_value = getattr(model_instance, field)
        response_value = response_data[field]

        # Convert UUID to string for comparison
        if hasattr(model_value, "hex"):
            model_value = str(model_value)

        assert model_value == response_value, (
            f"Field '{field}': expected {model_value}, got {response_value}"
        )


__all__ = [
    "assert_valid_uuid",
    "assert_successful_response",
    "assert_error_response",
    "assert_validation_error",
    "assert_pagination_response",
    "assert_geojson_point",
    "assert_geojson_polygon",
    "assert_has_keys",
    "assert_timestamp_format",
    "assert_response_matches_model",
]

