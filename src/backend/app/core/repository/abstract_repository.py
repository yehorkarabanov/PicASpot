from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    """Abstract base class for all repositories.

    This class defines the interface for data access operations.
    Implementations should provide concrete methods for CRUD operations
    and efficient data fetching with optional loading options.
    """

    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new entity.

        Args:
            data (Dict[str, Any]): A dictionary of field names and values to create the entity.

        Returns:
            T: The created entity instance.
        """
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: Any, load_options: Optional[List[Any]] = None) -> Optional[T]:
        """Get an entity by its ID, with optional loading options for efficiency.

        Args:
            entity_id (Any): The ID of the entity to retrieve.
            load_options (Optional[List[Any]]): List of SQLAlchemy loading options for eager loading,
                e.g., [selectinload(Model.relationship)] to fetch related objects in one query.

        Returns:
            Optional[T]: The entity if found, else None.
        """
        pass

    @abstractmethod
    async def get_by_field(self, field_name: str, field_value: Any, load_options: Optional[List[Any]] = None) -> Optional[T]:
        """Get an entity by a specific field, with optional loading options for efficiency.

        Args:
            field_name (str): The name of the field to filter by.
            field_value (Any): The value of the field to match.
            load_options (Optional[List[Any]]): List of SQLAlchemy loading options for eager loading,
                e.g., [selectinload(Model.relationship)] to fetch related objects in one query.

        Returns:
            Optional[T]: The entity if found, else None.
        """
        pass

    @abstractmethod
    async def get_all(self, filter_criteria: Optional[Dict[str, Any]] = None, load_options: Optional[List[Any]] = None) -> List[T]:
        """Get all entities, optionally filtered, with optional loading options for efficiency.

        Args:
            filter_criteria (Optional[Dict[str, Any]]): A dictionary of field names and values to filter by,
                using equality checks.
            load_options (Optional[List[Any]]): List of SQLAlchemy loading options for eager loading,
                e.g., [selectinload(Model.relationship)] to fetch related objects in one query.

        Returns:
            List[T]: A list of matching entities.
        """
        pass

    @abstractmethod
    async def update(self, entity_id: Any, data: Dict[str, Any]) -> Optional[T]:
        """Update an entity.

        Args:
            entity_id (Any): The ID of the entity to update.
            data (Dict[str, Any]): A dictionary of field names and values to update.

        Returns:
            Optional[T]: The updated entity if found, else None.
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: Any) -> bool:
        """Delete an entity.

        Args:
            entity_id (Any): The ID of the entity to delete.

        Returns:
            bool: True if the entity was deleted, False if not found.
        """
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save an entity (update if exists, create if new).

        Args:
            entity (T): The entity instance to save.

        Returns:
            T: The saved entity instance.
        """
        pass