from fastapi import FastAPI
from app.presentation.api import user_router

app = FastAPI(title="kapp-backend")

app.include_router(user_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to kapp-backend API"}