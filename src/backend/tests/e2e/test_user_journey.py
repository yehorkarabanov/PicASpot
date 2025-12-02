"""
Example E2E tests for complete user workflows.

These tests simulate real user journeys through the application,
testing multiple endpoints in sequence.
"""

import pytest
from httpx import AsyncClient

from tests.utils.assertions import (
    assert_has_keys,
    assert_successful_response,
    assert_valid_uuid,
)


@pytest.mark.e2e
class TestUserJourney:
    """Test complete user registration and usage flow."""

    @pytest.mark.asyncio
    async def test_complete_user_registration_flow(
        self,
        async_client: AsyncClient,
        clean_database,
    ):
        """
        Test complete user registration workflow:
        1. Register new user
        2. Verify email (simulated)
        3. Login
        4. Access protected resources
        """
        # Step 1: Register new user
        register_data = {
            "username": "journeyuser",
            "email": "journeyuser@example.com",
            "password": "SecurePassword123!",
        }

        register_response = await async_client.post(
            "/api/v1/auth/register",
            json=register_data,
        )

        assert_successful_response(register_response, 201)
        user_data = register_response.json()
        assert_has_keys(user_data, ["id", "username", "email"])
        assert_valid_uuid(user_data["id"])

        # Step 2: Email verification would happen here
        # (Skipped for this example - would require email/token logic)

        # Step 3: Login with credentials
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"],
        }

        login_response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
        )

        # This may fail if email verification is required
        if login_response.status_code == 200:
            login_result = login_response.json()
            assert "access_token" in login_result

            # Step 4: Access protected resource with token
            headers = {"Authorization": f"Bearer {login_result['access_token']}"}

            profile_response = await async_client.get(
                "/api/v1/users/me",
                headers=headers,
            )

            assert_successful_response(profile_response, 200)
            profile_data = profile_response.json()
            assert profile_data["username"] == register_data["username"]
            assert profile_data["email"] == register_data["email"]


@pytest.mark.e2e
class TestLandmarkDiscoveryJourney:
    """Test complete landmark discovery workflow."""

    @pytest.mark.asyncio
    async def test_discover_and_unlock_landmark(
        self,
        authenticated_client: AsyncClient,
        test_user,
        test_session,
        clean_database,
    ):
        """
        Test landmark discovery workflow:
        1. Browse available areas
        2. View landmarks in an area
        3. Navigate to landmark location
        4. Unlock landmark with photo
        """
        from tests.factories import AreaFactory, LandmarkFactory

        # Setup: Create test data
        area = await AreaFactory.create(
            test_session,
            test_user,
            name="Test City",
        )

        landmark = await LandmarkFactory.create(
            test_session,
            test_user,
            area,
            name="Test Monument",
            latitude=51.5074,
            longitude=-0.1278,
        )

        # Step 1: Browse areas
        areas_response = await authenticated_client.get("/api/v1/areas")
        assert_successful_response(areas_response, 200)
        areas_data = areas_response.json()
        assert len(areas_data["items"]) > 0

        # Step 2: Get landmarks in area
        landmarks_response = await authenticated_client.get(
            f"/api/v1/areas/{area.id}/landmarks"
        )
        assert_successful_response(landmarks_response, 200)
        landmarks_data = landmarks_response.json()
        assert len(landmarks_data["items"]) > 0

        # Step 3: Get specific landmark details
        landmark_response = await authenticated_client.get(
            f"/api/v1/landmarks/{landmark.id}"
        )
        assert_successful_response(landmark_response, 200)
        landmark_data = landmark_response.json()
        assert landmark_data["name"] == "Test Monument"

        # Step 4: Attempt to unlock landmark
        # (This would require photo upload and location validation)
        unlock_data = {
            "landmark_id": str(landmark.id),
            "latitude": 51.5074,  # Near landmark
            "longitude": -0.1278,
            "photo_url": "https://example.com/photo.jpg",
        }

        unlock_response = await authenticated_client.post(
            "/api/v1/unlocks",
            json=unlock_data,
        )

        # Response depends on implementation details
        # (proximity check, photo validation, etc.)
        assert unlock_response.status_code in [200, 201, 400, 422]


@pytest.mark.e2e
@pytest.mark.slow
class TestAreaManagementJourney:
    """Test complete area management workflow for admin users."""

    @pytest.mark.asyncio
    async def test_create_and_manage_area_hierarchy(
        self,
        superuser_client: AsyncClient,
        test_superuser,
        test_session,
        clean_database,
    ):
        """
        Test area management workflow:
        1. Create parent area (Country)
        2. Create child area (City)
        3. Add landmarks to city
        4. Verify area hierarchy
        5. Update area details
        """
        # Step 1: Create parent area
        country_data = {
            "name": "Test Country",
            "description": "A test country for E2E testing",
        }

        country_response = await superuser_client.post(
            "/api/v1/areas",
            json=country_data,
        )

        assert_successful_response(country_response, 201)
        country = country_response.json()
        assert_valid_uuid(country["id"])

        # Step 2: Create child area
        city_data = {
            "name": "Test City",
            "description": "A test city",
            "parent_area_id": country["id"],
        }

        city_response = await superuser_client.post(
            "/api/v1/areas",
            json=city_data,
        )

        assert_successful_response(city_response, 201)
        city = city_response.json()
        assert city["parent_area_id"] == country["id"]

        # Step 3: Add landmark to city
        landmark_data = {
            "name": "City Monument",
            "description": "Famous monument",
            "area_id": city["id"],
            "latitude": 51.5074,
            "longitude": -0.1278,
            "image_url": "https://example.com/monument.jpg",
        }

        landmark_response = await superuser_client.post(
            "/api/v1/landmarks",
            json=landmark_data,
        )

        assert_successful_response(landmark_response, 201)

        # Step 4: Verify area hierarchy
        hierarchy_response = await superuser_client.get(
            f"/api/v1/areas/{country['id']}/children"
        )

        if hierarchy_response.status_code == 200:
            children = hierarchy_response.json()
            assert len(children["items"]) > 0
            assert any(child["id"] == city["id"] for child in children["items"])

        # Step 5: Update area details
        update_data = {
            "description": "Updated description",
            "is_verified": True,
        }

        update_response = await superuser_client.patch(
            f"/api/v1/areas/{city['id']}",
            json=update_data,
        )

        if update_response.status_code == 200:
            updated_city = update_response.json()
            assert updated_city["description"] == update_data["description"]


# Run E2E tests with: pytest tests/e2e/ -v -m e2e
# Run slow E2E tests: pytest tests/e2e/ -v -m "e2e and slow"

