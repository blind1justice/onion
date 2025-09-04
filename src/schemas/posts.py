from pydantic import BaseModel

from src.schemas.users import UserSchema


class PostSchema(BaseModel):
    id: int
    subject: str
    content: str
    user: UserSchema


class PostSchemaAdd(BaseModel):
    subject: str
    content: str
