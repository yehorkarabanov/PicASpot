# SQLAlchemy Async Relationships Usage Guide

## ✅ UPDATED FOR ASYNC SQLALCHEMY

All models now have **proper bidirectional relationships** with `lazy="raise"` to ensure async compatibility.

## Why `lazy="raise"`?

With async SQLAlchemy, the default lazy loading (`lazy="select"`) **WILL FAIL** because it tries to execute synchronous queries. Using `lazy="raise"` forces you to explicitly load relationships, preventing runtime errors.

## How to Use Relationships in Your Async Code

### ❌ WRONG - This Will Raise an Error

```python
# This will raise an exception because of lazy="raise"
area = await area_repo.get_by_id(area_id)
print(area.creator.username)  # ❌ LazyLoadException!
```

### ✅ CORRECT - Use Eager Loading

You have two options for eager loading:

#### Option 1: `selectinload()` - Separate Query (Recommended for Collections)
Best for loading collections (one-to-many relationships).

```python
from sqlalchemy.orm import selectinload

# Load area with its landmarks
area = await area_repo.get_by_id(
    area_id, 
    load_options=[selectinload(Area.landmarks)]
)
for landmark in area.landmarks:  # ✅ Works!
    print(landmark.name)

# Load area with creator
area = await area_repo.get_by_id(
    area_id,
    load_options=[selectinload(Area.creator)]
)
print(area.creator.username)  # ✅ Works!
```

#### Option 2: `joinedload()` - Single Query with JOIN
Best for loading single objects (many-to-one relationships).

```python
from sqlalchemy.orm import joinedload

# Load landmark with its area (more efficient for single objects)
landmark = await landmark_repo.get_by_id(
    landmark_id,
    load_options=[joinedload(Landmark.area)]
)
print(landmark.area.name)  # ✅ Works!

# Load with multiple relationships
landmark = await landmark_repo.get_by_id(
    landmark_id,
    load_options=[
        joinedload(Landmark.area),
        joinedload(Landmark.creator)
    ]
)
print(f"{landmark.name} in {landmark.area.name} by {landmark.creator.username}")  # ✅ Works!
```

## Complete Usage Examples

### Example 1: Get Area with All Landmarks

```python
from sqlalchemy.orm import selectinload

async def get_area_with_landmarks(area_repo: AreaRepository, area_id: uuid.UUID):
    area = await area_repo.get_by_id(
        area_id,
        load_options=[selectinload(Area.landmarks)]
    )
    if not area:
        return None
    
    return {
        "name": area.name,
        "landmarks": [
            {"id": lm.id, "name": lm.name} 
            for lm in area.landmarks
        ]
    }
```

### Example 2: Get User with All Created Content

```python
from sqlalchemy.orm import selectinload

async def get_user_stats(user_repo: UserRepository, user_id: uuid.UUID):
    user = await user_repo.get_by_id(
        user_id,
        load_options=[
            selectinload(User.created_areas),
            selectinload(User.created_landmarks),
            selectinload(User.unlocks)
        ]
    )
    
    return {
        "username": user.username,
        "areas_created": len(user.created_areas),
        "landmarks_created": len(user.created_landmarks),
        "unlocks_count": len(user.unlocks)
    }
```

### Example 3: Get Landmark with Full Context

```python
from sqlalchemy.orm import joinedload, selectinload

async def get_landmark_details(landmark_repo: LandmarkRepository, landmark_id: uuid.UUID):
    landmark = await landmark_repo.get_by_id(
        landmark_id,
        load_options=[
            joinedload(Landmark.area),
            joinedload(Landmark.creator),
            selectinload(Landmark.unlocks)  # Could be many unlocks
        ]
    )
    
    return {
        "id": landmark.id,
        "name": landmark.name,
        "area": landmark.area.name,
        "created_by": landmark.creator.username,
        "times_unlocked": len(landmark.unlocks)
    }
```

### Example 4: Get Area Hierarchy (Parent and Children)

```python
from sqlalchemy.orm import joinedload, selectinload

async def get_area_hierarchy(area_repo: AreaRepository, area_id: uuid.UUID):
    area = await area_repo.get_by_id(
        area_id,
        load_options=[
            joinedload(Area.parent_area),  # Single parent
            selectinload(Area.child_areas)  # Multiple children
        ]
    )
    
    result = {
        "name": area.name,
        "parent": area.parent_area.name if area.parent_area else None,
        "children": [child.name for child in area.child_areas]
    }
    return result
```

### Example 5: Get Unlock with Full Details

```python
from sqlalchemy.orm import joinedload

async def get_unlock_details(unlock_repo: UnlockRepository, user_id, area_id, landmark_id):
    # Unlock uses composite primary key
    unlock = await unlock_repo.get_by_id(
        (user_id, area_id, landmark_id),
        load_options=[
            joinedload(Unlock.user),
            joinedload(Unlock.area),
            joinedload(Unlock.landmark)
        ]
    )
    
    return {
        "user": unlock.user.username,
        "landmark": unlock.landmark.name,
        "area": unlock.area.name,
        "unlocked_at": unlock.unlocked_at,
        "photo_url": unlock.photo_url
    }
```

### Example 6: Using get_all() with Relationships

```python
from sqlalchemy.orm import selectinload

async def get_all_verified_areas_with_landmarks(area_repo: AreaRepository):
    areas = await area_repo.get_all(
        filter_criteria={"is_verified": True},
        load_options=[
            selectinload(Area.landmarks),
            selectinload(Area.creator)
        ]
    )
    
    return [
        {
            "name": area.name,
            "creator": area.creator.username,
            "landmark_count": len(area.landmarks)
        }
        for area in areas
    ]
```

## Custom Repository Methods with Relationships

You can add custom methods to your repositories that include relationships:

### AreaRepository Example

```python
from sqlalchemy.orm import selectinload, joinedload

class AreaRepository(BaseRepository[Area]):
    
    async def get_with_landmarks(self, area_id: uuid.UUID) -> Area | None:
        """Get area with all its landmarks loaded"""
        return await self.get_by_id(
            area_id,
            load_options=[selectinload(Area.landmarks)]
        )
    
    async def get_with_full_context(self, area_id: uuid.UUID) -> Area | None:
        """Get area with creator, parent, children, and landmarks"""
        return await self.get_by_id(
            area_id,
            load_options=[
                joinedload(Area.creator),
                joinedload(Area.parent_area),
                selectinload(Area.child_areas),
                selectinload(Area.landmarks)
            ]
        )
```

### UserRepository Example

```python
from sqlalchemy.orm import selectinload

class UserRepository(BaseRepository[User]):
    
    async def get_with_created_content(self, user_id: uuid.UUID) -> User | None:
        """Get user with all their created areas and landmarks"""
        return await self.get_by_id(
            user_id,
            load_options=[
                selectinload(User.created_areas),
                selectinload(User.created_landmarks),
            ]
        )
    
    async def get_with_unlocks(self, user_id: uuid.UUID) -> User | None:
        """Get user with all their unlocks"""
        return await self.get_by_id(
            user_id,
            load_options=[selectinload(User.unlocks)]
        )
```

## Performance Tips

### 1. Choose the Right Loading Strategy

- **`joinedload()`**: Use for **many-to-one** or **one-to-one** (e.g., `landmark.area`, `area.creator`)
  - Single query with JOIN
  - More efficient for loading few related objects
  
- **`selectinload()`**: Use for **one-to-many** (e.g., `area.landmarks`, `user.created_areas`)
  - Separate query with IN clause
  - More efficient for loading collections
  - Avoids cartesian product problem

### 2. Avoid N+1 Queries

```python
# ❌ BAD - N+1 queries (will actually raise exception with lazy="raise")
areas = await area_repo.get_all()
for area in areas:
    print(area.creator.username)  # ❌ Error! lazy="raise" prevents this

# ✅ GOOD - Single query
areas = await area_repo.get_all(
    load_options=[joinedload(Area.creator)]
)
for area in areas:
    print(area.creator.username)  # ✅ Works efficiently!
```

### 3. Nested Relationships

You can load nested relationships:

```python
from sqlalchemy.orm import selectinload, joinedload

# Load landmarks with their areas AND the area creators
landmarks = await landmark_repo.get_all(
    load_options=[
        selectinload(Landmark.area).joinedload(Area.creator)
    ]
)

for landmark in landmarks:
    print(f"{landmark.name} in {landmark.area.name} by {landmark.area.creator.username}")
```

## Database Migration Note

**Important**: The relationships are ORM-level only and **do not require a database migration**. Your existing database schema is fine because:
- ForeignKeys were already defined (database constraints exist)
- `relationship()` only affects Python code, not SQL schema

## Testing Relationships

```python
import pytest
from sqlalchemy.orm import selectinload

@pytest.mark.asyncio
async def test_area_landmarks_relationship(db_session):
    # Create user
    user = User(username="test", email="test@test.com", hashed_password="xxx")
    db_session.add(user)
    await db_session.flush()
    
    # Create area
    area = Area(name="Test Area", created_by=user.id)
    db_session.add(area)
    await db_session.flush()
    
    # Create landmark
    landmark = Landmark(
        name="Test Landmark",
        area_id=area.id,
        created_by=user.id,
        image_url="http://test.com/image.jpg",
        location="POINT(0 0)"
    )
    db_session.add(landmark)
    await db_session.commit()
    
    # Reload with relationships
    area_with_landmarks = await db_session.get(
        Area, 
        area.id,
        options=[selectinload(Area.landmarks)]
    )
    
    assert len(area_with_landmarks.landmarks) == 1
    assert area_with_landmarks.landmarks[0].name == "Test Landmark"
```

## Summary

✅ All relationships use `lazy="raise"` for async safety
✅ Always use `selectinload()` or `joinedload()` to load relationships
✅ Your existing `BaseRepository` already supports `load_options`
✅ No database migration needed
✅ Prevents N+1 query problems by forcing explicit loading
✅ Type-safe with proper Mapped[] annotations

Happy querying! 🚀

