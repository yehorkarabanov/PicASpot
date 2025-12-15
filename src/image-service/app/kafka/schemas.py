from pydantic import BaseModel


class ImageProcessingMessage(BaseModel):
    image_id: str
    operation: str
    params: dict | None = None
