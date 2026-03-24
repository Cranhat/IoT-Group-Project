from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    privilege: str

class Password(BaseModel):
    user_id: int
    password: str