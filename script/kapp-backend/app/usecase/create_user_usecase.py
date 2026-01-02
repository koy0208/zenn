from app.domain.model.user import User
from app.domain.repository.user_repository import UserRepository
from app.usecase.dto.user_dto import UserCreateInput, UserOutput


class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, input_data: UserCreateInput) -> UserOutput:
        # 重複チェックの例
        if self.user_repository.find_by_email(input_data.email):
            raise ValueError("Email already registered")

        if self.user_repository.find_by_username(input_data.username):
            raise ValueError("Username already taken")

        # 本来はここでパスワードハッシュ化を行う
        user = User(
            username=input_data.username,
            email=input_data.email,
            hashed_password=f"hashed_{input_data.password}",  # 簡易的な処理
        )

        saved_user = self.user_repository.save(user)

        return UserOutput(
            id=saved_user.id, username=saved_user.username, email=saved_user.email
        )
