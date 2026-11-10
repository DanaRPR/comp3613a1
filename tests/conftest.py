from datetime import datetime

import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.models import Award, Progress, User, VolunteerHours


@pytest.fixture
def session(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        yield db


@pytest.fixture
def student(session):
    user = User(
        username="student1",
        email="student1@example.com",
        password="secret",
        role="student",
        totalVolunteerHours=0,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def admin(session):
    user = User(
        username="admin1",
        email="admin1@example.com",
        password="secret",
        role="admin",
        totalVolunteerHours=0,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def award(session):
    item = Award(name="Gold", description="Top award", requiredHours=25)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@pytest.fixture
def progress_row(session, student):
    row = Progress(totalHours=0, awardsEarned=0, student_id=student.id)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@pytest.fixture
def volunteer_submission(session, student):
    submission = VolunteerHours(
        date=datetime(2026, 1, 10),
        hours=8,
        activity="Library volunteering",
        student_id=student.id,
        status="pending",
    )
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission
