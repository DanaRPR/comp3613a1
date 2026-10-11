from sqlmodel import Field, SQLModel
from typing import Optional


class ProgressBase(SQLModel):
    totalHours: int = Field(default=0)
    awardsEarned: int = Field(default=0)
    student_id: int = Field(foreign_key="user.id", unique=True)


class Progress(ProgressBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
