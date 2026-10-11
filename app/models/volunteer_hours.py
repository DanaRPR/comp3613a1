from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime


class VolunteerHoursBase(SQLModel):
    date: datetime
    hours: int = Field(gt=0)
    activity: str = Field(min_length=1)
    status: str = Field(default="pending")
    student_id: int = Field(foreign_key="user.id")
    administrator_id: Optional[int] = Field(default=None, foreign_key="user.id")


class VolunteerHours(VolunteerHoursBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
