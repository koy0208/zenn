from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    username: str
    email: EmailStr
    hashed_password: str
