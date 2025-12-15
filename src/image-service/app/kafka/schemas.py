from pydantic import BaseModel


class BaseKafkaEmailMessage(BaseModel):
    email: str
    username: str
    link: str


class VerificationEmailMessage(BaseKafkaEmailMessage):
    pass


class ResetPasswordEmailMessage(BaseKafkaEmailMessage):
    pass
