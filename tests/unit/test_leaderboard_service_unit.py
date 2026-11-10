from types import SimpleNamespace

import pytest

from app.models.award import Award, Redemption
from app.services.leaderboard import LeaderboardService


class FakeExecResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows

    def first(self):
        return self._rows[0] if self._rows else None


class FakeLeaderboardSession:
    def __init__(self, progress=None, awards=None, redeemed_ids=None):
        self.progress = progress
        self.awards = awards or []
        self.redeemed_ids = redeemed_ids or []

    def exec(self, statement):
        query = str(statement).lower()
        if "from award" in query:
            return FakeExecResult(self.awards)
        if "from redemption" in query and "award_id" in query:
            return FakeExecResult(list(self.redeemed_ids))
        if "from progress" in query:
            return FakeExecResult([self.progress] if self.progress else [])
        return FakeExecResult([])


class FakeLeaderboardRepository:
    def __init__(self, rows=None, progress=None, awards=None, redeemed_ids=None):
        self.session = FakeLeaderboardSession(progress=progress, awards=awards, redeemed_ids=redeemed_ids)
        self.rows = rows or []

    def get_all_students_by_hours(self):
        return self.rows

    def get_progress(self, student_id):
        return self.session.progress


@pytest.mark.unit
def test_get_leaderboard_assigns_rank_and_current_student():
    student_a = SimpleNamespace(id=1, username="student1", totalVolunteerHours=20)
    student_b = SimpleNamespace(id=2, username="student2", totalVolunteerHours=15)
    repo = FakeLeaderboardRepository(rows=[(student_a, 20), (student_b, 15)])
    service = LeaderboardService(repo)

    rows = service.get_leaderboard(1)

    assert rows[0]["rank"] == 1
    assert rows[0]["name"] == "student1"
    assert rows[0]["hours"] == 20
    assert rows[0]["is_current"] is True
    assert rows[1]["is_current"] is False


@pytest.mark.unit
def test_get_progress_returns_next_award_and_threshold():
    progress = SimpleNamespace(totalHours=30, awardsEarned=0, student_id=7)
    award_1 = SimpleNamespace(id=1, requiredHours=10)
    award_2 = SimpleNamespace(id=2, requiredHours=25)
    repo = FakeLeaderboardRepository(
        progress=progress,
        awards=[award_1, award_2],
        redeemed_ids=[1],
    )
    service = LeaderboardService(repo)

    result = service.get_progress(7)

    assert result["progress"] is progress
    assert result["next_award"] == award_2
    assert result["next_threshold"] == 25
