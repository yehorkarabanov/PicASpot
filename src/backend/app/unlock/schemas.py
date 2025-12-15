from uuid import UUID

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, ConfigDict


class UnlockCreate(BaseModel):
    """Schema for creating a new unlock (verifying a photo)"""

    landmark_id: UUID = Form(..., description="Landmark ID to verify")
    image_file: UploadFile = File(..., description="Photo of the landmark")

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
