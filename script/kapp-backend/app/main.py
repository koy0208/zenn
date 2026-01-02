from app.presentation.api import user_router
from fastapi import FastAPI


app = FastAPI(title="kapp-backend")

app.include_router(user_router.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to kapp-backend API"}
