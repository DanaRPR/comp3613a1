from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

class AwardBase(SQLModel):
    name: str
    description: str = Field(default="")
    requiredHours: int = Field(gt=0)


class Award(AwardBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class RedemptionBase(SQLModel):
    redemptionDate: dateTime = Field(default_factory=datetime.now)
    status: str = Field(default="completed")
    student_id: int = Field(foreign_key="user.id")
    award_id: int = Field(foreign_key="award.id")


class Redemption(RedemptionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
