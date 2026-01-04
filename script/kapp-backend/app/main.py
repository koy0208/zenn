from app.presentation.api import user_router
from app.presentation.api.article_router import router as article_router
from fastapi import FastAPI


app = FastAPI(title="kapp-backend")

app.include_router(user_router.router)
app.include_router(article_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to kapp-backend API"}
