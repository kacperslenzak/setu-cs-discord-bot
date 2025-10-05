from sqlmodel import SQLModel, Field


class Reminder(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int
    message: str
