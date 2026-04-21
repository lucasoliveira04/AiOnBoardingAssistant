from pydantic import BaseModel
from uuid import UUID


class CreateUserRequest(BaseModel):
    nome: str
    sobrenome: str
    cargo: str


class UserResponse(BaseModel):
    id: UUID
    nome: str
    sobrenome: str
    cargo: str

    class Config:
        from_attributes = True