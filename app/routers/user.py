from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import User, get_db
from app.dto.UserDTO import CreateUserRequest, UserResponse

router = APIRouter()


@router.post("/users", response_model=UserResponse)
def create_user(
    data: CreateUserRequest,
    db: Session = Depends(get_db)
):
    user = User(
        nome=data.nome,
        sobrenome=data.sobrenome,
        cargo=data.cargo
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user