from fastapi import APIRouter, HTTPException, Depends
from app.usecase.create_user_usecase import CreateUserUseCase
from app.usecase.dto.user_dto import UserCreateInput
from app.presentation.schema.user_schema import UserRegisterRequest, UserResponse
from sqlalchemy.orm import Session
from app.adapter.database import get_db
from app.adapter.repository.sqlalchemy_user_repository import SQLAlchemyUserRepository

router = APIRouter(prefix="/users", tags=["users"])
# DI用のユーティリティ


def get_create_user_usecase(db: Session = Depends(get_db)):

    user_repository = SQLAlchemyUserRepository(db)

    return CreateUserUseCase(user_repository)


@router.post("/", response_model=UserResponse)
def register_user(
    request: UserRegisterRequest,
    usecase: CreateUserUseCase = Depends(get_create_user_usecase),
):
    try:
        input_data = UserCreateInput(
            username=request.username, email=request.email, password=request.password
        )
        output = usecase.execute(input_data)
        return UserResponse(id=output.id, username=output.username, email=output.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
