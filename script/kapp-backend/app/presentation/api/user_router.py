from fastapi import APIRouter, HTTPException, Depends
from app.usecase.create_user_usecase import CreateUserUseCase
from app.usecase.dto.user_dto import UserCreateInput
from app.presentation.schema.user_schema import UserRegisterRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

# DI用のユーティリティ (本来は依存性注入ライブラリなどを使うが、ここではシンプルに実装)
def get_create_user_usecase():
    # main.py でインスタンス化された repository を使うなどの工夫が必要だが、
    # 一旦ここで repository の依存を解決するように見せる（後で main.py で調整）
    from app.main import user_repository
    return CreateUserUseCase(user_repository)

@router.post("/", response_model=UserResponse)
def register_user(
    request: UserRegisterRequest,
    usecase: CreateUserUseCase = Depends(get_create_user_usecase)
):
    try:
        input_data = UserCreateInput(
            username=request.username,
            email=request.email,
            password=request.password
        )
        output = usecase.execute(input_data)
        return UserResponse(
            id=output.id,
            username=output.username,
            email=output.email
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
