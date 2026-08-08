from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class UserInDB(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
