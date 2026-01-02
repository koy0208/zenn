from pydantic import BaseModel, EmailStr


class UserCreateInput(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOutput(BaseModel):
    id: int
    username: str
    email: EmailStr
