from pydantic import BaseModel


class BaseKafkaEmailMessage(BaseModel):
    email: str
    username: str
    link: str


class VerificationEmailMessage(BaseKafkaEmailMessage):
    pass


class ResetPasswordEmailMessage(BaseKafkaEmailMessage):
    pass


class UnlockVerifyMessage(BaseModel):
    """Schema for Kafka message to verify unlock"""

    user_id: str
    landmark_id: str
    photo_url: str
    landmark_image: str
    latitude: float
    longitude: float
    unlock_radius_meters: int
    photo_radius_meters: int
