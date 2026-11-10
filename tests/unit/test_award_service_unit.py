from types import SimpleNamespace

import pytest

from app.models.award import Redemption
from app.services.award import AwardService


class FakeExecResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class FakeAwardSession:
    def __init__(self, awards=None, redeemed_ids=None):
        self.awards = awards or []
        self.redeemed_ids = redeemed_ids or []
        self.committed = False

    def exec(self, statement):
        query = str(statement).lower()
        if "from award" in query:
            return FakeExecResult(self.awards)
        if "redemption" in query and "award_id" in query:
            return FakeExecResult(list(self.redeemed_ids))
        return FakeExecResult([])


class FakeAwardRepository:
    def __init__(self, awards=None, redeemed_ids=None):
        self.session = FakeAwardSession(awards=awards, redeemed_ids=redeemed_ids)
        self.awards = awards or []
        self.redeemed_ids = redeemed_ids or []
        self.saved_redemption = None

    def get_all_awards(self):
        return self.awards

    def get_redeemed_award_ids(self, student_id):
        return list(self.redeemed_ids)

    def add_redemption(self, redemption):
        self.saved_redemption = redemption
        return redemption


@pytest.mark.unit
def test_get_available_awards_marks_eligible_and_not_redeemed():
    awards = [SimpleNamespace(id=1, name="Bronze", description="", requiredHours=10)]
    repo = FakeAwardRepository(awards=awards, redeemed_ids=[])
    service = AwardService(repo)

    result = service.get_available_awards(student_id=7, total_hours=15)

    assert result[0]["available"] is True
    assert result[0]["already_redeemed"] is False


@pytest.mark.unit
def test_get_available_awards_marks_redeemed_and_ineligible():
    awards = [SimpleNamespace(id=1, name="Bronze", description="", requiredHours=10)]
    repo = FakeAwardRepository(awards=awards, redeemed_ids=[1])
    service = AwardService(repo)

    result = service.get_available_awards(student_id=7, total_hours=8)

    assert result[0]["available"] is False
    assert result[0]["already_redeemed"] is True


@pytest.mark.unit
def test_redeem_raises_for_missing_award():
    repo = FakeAwardRepository(awards=[], redeemed_ids=[])
    service = AwardService(repo)

    with pytest.raises(ValueError, match="Award not found"):
        service.redeem(student_id=7, award_id=88, total_hours=20)


@pytest.mark.unit
def test_redeem_raises_for_duplicate_redemption():
    award = SimpleNamespace(id=2, name="Silver", description="", requiredHours=20)
    repo = FakeAwardRepository(awards=[award], redeemed_ids=[2])
    service = AwardService(repo)

    with pytest.raises(ValueError, match="already redeemed"):
        service.redeem(student_id=7, award_id=2, total_hours=25)
