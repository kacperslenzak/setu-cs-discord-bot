from sqlmodel import SQLModel, Field
from datetime import datetime


class Reminder(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int
    message: str
    remind_at: datetime
