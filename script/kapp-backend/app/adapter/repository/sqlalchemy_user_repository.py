from sqlalchemy.orm import Session
from app.domain.model.user import User
from app.domain.repository.user_repository import UserRepository
from app.adapter.orm.user_orm import UserORM

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> User:
        user_orm = UserORM.from_domain(user)
        
        if user.id:
            # 更新の場合（今回は簡易的にマージ）
            self.db.merge(user_orm)
        else:
            # 新規作成
            self.db.add(user_orm)
        
        self.db.commit()
        self.db.refresh(user_orm)
        return user_orm.to_domain()

    def find_by_email(self, email: str) -> User | None:
        user_orm = self.db.query(UserORM).filter(UserORM.email == email).first()
        if user_orm:
            return user_orm.to_domain()
        return None

    def find_by_username(self, username: str) -> User | None:
        user_orm = self.db.query(UserORM).filter(UserORM.username == username).first()
        if user_orm:
            return user_orm.to_domain()
        return None