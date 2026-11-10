from datetime import datetime

import pytest
from sqlmodel import select

from app.models import Award, Progress, Redemption, User
from app.repositories.leaderboard import LeaderboardRepository
from app.services.leaderboard import LeaderboardService


@pytest.mark.integration
def test_leaderboard_excludes_admins_and_orders_students_by_hours(session, student):
    admin = User(username="admin1", email="admin1@example.com", password="secret", role="admin", totalVolunteerHours=99)
    another = User(username="student2", email="student2@example.com", password="secret", role="student", totalVolunteerHours=15)
    session.add_all([admin, another])
    session.commit()

    student.totalVolunteerHours = 20
    session.add(student)
    session.commit()

    rows = LeaderboardService(LeaderboardRepository(session)).get_leaderboard(student.id)

    names = [row["name"] for row in rows]
    assert names == ["student1", "student2"]
    assert rows[0]["rank"] == 1
    assert rows[0]["is_current"] is True


@pytest.mark.integration
def test_get_progress_returns_next_unredeemed_award(session, student, award):
    progress = Progress(totalHours=30, awardsEarned=0, student_id=student.id)
    session.add(progress)
    session.commit()

    session.add(Redemption(student_id=student.id, award_id=award.id, status="completed", redemptionDate=datetime.now()))
    session.commit()

    result = LeaderboardService(LeaderboardRepository(session)).get_progress(student.id)

    assert result["progress"].totalHours == 30
    assert result["next_award"] is None
    assert result["next_threshold"] is None


@pytest.mark.integration
def test_get_progress_returns_first_unredeemed_award(session, student):
    progress = Progress(totalHours=30, awardsEarned=0, student_id=student.id)
    session.add(progress)
    session.commit()

    award_1 = Award(name="Bronze", description="First", requiredHours=10)
    award_2 = Award(name="Silver", description="Second", requiredHours=25)
    session.add_all([award_1, award_2])
    session.commit()

    session.add(Redemption(student_id=student.id, award_id=award_1.id, status="completed", redemptionDate=datetime.now()))
    session.commit()

    result = LeaderboardService(LeaderboardRepository(session)).get_progress(student.id)

    assert result["next_award"].name == "Silver"
    assert result["next_threshold"] == 25
