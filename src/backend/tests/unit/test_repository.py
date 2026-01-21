"""
Unit tests for BaseRepository.

Tests cover:
- CRUD operations
- Query filtering
- Error handling

Note: These tests mock the session to avoid SQLAlchemy query building issues.
The BaseRepository is tested through mocking rather than actual SQL execution.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest


class TestBaseRepositoryCreate:
    """Tests for BaseRepository.create method."""

    @pytest.mark.asyncio
    async def test_create_adds_commits_and_refreshes(self):
        """Create should add, commit, and refresh the object."""
        from app.core.repository.base_repository import BaseRepository
        from app.user.models import User

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        repository = BaseRepository(session=mock_session, model=User)

        data = {
            "username": "test",
            "email": "test@example.com",
            "hashed_password": "hash",
        }

        # The create method creates the object and adds it
        result = await repository.create(data)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()


class TestBaseRepositoryGetById:
    """Tests for BaseRepository.get_by_id method."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self):
        """Get by ID should return object when found."""
        from app.core.repository.base_repository import BaseRepository
        from app.user.models import User

        entity_id = uuid.uuid4()
        mock_user = MagicMock(spec=User)
        mock_user.id = entity_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result

        repository = BaseRepository(session=mock_session, model=User)
        result = await repository.get_by_id(entity_id)

        assert result is not None
        assert result.id == entity_id
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Get by ID should return None when not found."""
        from app.core.repository.base_repository import BaseRepository
        from app.user.models import User

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result

        repository = BaseRepository(session=mock_session, model=User)
        result = await repository.get_by_id(uuid.uuid4())

        assert result is None


class TestBaseRepositoryGetByField:
    """Tests for BaseRepository.get_by_field method."""

    @pytest.mark.asyncio
    async def test_get_by_field_found(self):
        """Get by field should return object when found."""
        from app.core.repository.base_repository import BaseRepository
        from app.user.models import User

        mock_user = MagicMock(spec=User)
        mock_user.email = "test@example.com"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result

        repository = BaseRepository(session=mock_session, model=User)
        result = await repository.get_by_field("email", "test@example.com")

        assert result is not None
        assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_by_field_not_found(self):
        """Get by field should return None when not found."""
        from app.core.repository.base_repository import BaseRepository
        from app.user.models import User

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result

        repository = BaseRepository(session=mock_session, model=User)
        result = await repository.get_by_field("email", "nonexistent@example.com")

        assert result is None


class TestBaseRepositoryUpdate:
    """Tests for BaseRepository.update method."""

    @pytest.mark.asyncio
    async def test_update_success(self):
        """Update should modify and commit the object."""
        from app.core.repository.base_repository import BaseRepository
        from app.user.models import User

        entity_id = uuid.uuid4()
        mock_user = MagicMock(spec=User)
        mock_user.id = entity_id
        mock_user.username = "old_name"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        repository = BaseRepository(session=mock_session, model=User)
        result = await repository.update(entity_id, {"username": "new_name"})

        assert result is not None
        mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        """Update should return None when object not found."""
        from app.core.repository.base_repository import BaseRepository
        from app.user.models import User

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result

        repository = BaseRepository(session=mock_session, model=User)
        result = await repository.update(uuid.uuid4(), {"username": "new_name"})

        assert result is None


class TestBaseRepositoryDelete:
    """Tests for BaseRepository.delete method."""

    @pytest.mark.asyncio
    async def test_delete_success(self):
        """Delete should remove and commit the object."""
        from app.core.repository.base_repository import BaseRepository
        from app.user.models import User

        entity_id = uuid.uuid4()
        mock_user = MagicMock(spec=User)
        mock_user.id = entity_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_session.delete = AsyncMock()
        mock_session.commit = AsyncMock()

        repository = BaseRepository(session=mock_session, model=User)
        result = await repository.delete(entity_id)

        assert result is True
        mock_session.delete.assert_called_once_with(mock_user)
        mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_delete_not_found(self):
        """Delete should return False when object not found."""
        from app.core.repository.base_repository import BaseRepository
        from app.user.models import User

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_session.delete = AsyncMock()

        repository = BaseRepository(session=mock_session, model=User)
        result = await repository.delete(uuid.uuid4())

        assert result is False
        mock_session.delete.assert_not_called()


class TestBaseRepositorySave:
    """Tests for BaseRepository.save method."""

    @pytest.mark.asyncio
    async def test_save_success(self):
        """Save should add, commit, and refresh the entity."""
        from app.core.repository.base_repository import BaseRepository
        from app.user.models import User

        mock_user = MagicMock(spec=User)
        mock_user.id = uuid.uuid4()

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        repository = BaseRepository(session=mock_session, model=User)
        result = await repository.save(mock_user)

        mock_session.add.assert_called_once_with(mock_user)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_user)
        assert result is mock_user
