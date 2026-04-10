from pydantic import BaseModel, Field
from datetime import datetime


class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}
