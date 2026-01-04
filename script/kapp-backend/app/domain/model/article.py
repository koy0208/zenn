from datetime import datetime
from pydantic import BaseModel, ConfigDict


class Article(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    title: str
    content: str
    author_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
