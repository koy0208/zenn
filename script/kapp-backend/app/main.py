from fastapi import FastAPI
from app.presentation.api import user_router
from app.adapter.repository.in_memory_user_repository import InMemoryUserRepository

app = FastAPI(title="kapp-backend")

# シングルトンとしてリポジトリを保持 (DIのため)
user_repository = InMemoryUserRepository()

app.include_router(user_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to kapp-backend API"}
