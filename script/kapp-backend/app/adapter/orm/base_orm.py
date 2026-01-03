from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, func

class BaseORM(SQLModel):
    # created_at: 自動で現在時刻が入る
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), 
            server_default=func.now(), 
            nullable=False
        )
    )
    
    # updated_at: 更新時に自動で時刻が更新される
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), 
            server_default=func.now(), 
            onupdate=func.now(), 
            nullable=False
        )
    )
