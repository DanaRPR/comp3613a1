from datetime import datetime

import pytest

from app.models import Award, Progress, Redemption
from app.repositories.award import AwardRepository
from app.services.award import AwardService


@pytest.mark.integration
def test_get_available_awards_eligible_and_unredeemed(session, student, award):
    repo = AwardRepository(session)
    service = AwardService(repo)

    awards = service.get_available_awards(student_id=student.id, total_hours=25)

    assert awards[0]["available"] is True
    assert awards[0]["already_redeemed"] is False


@pytest.mark.integration
def test_get_available_awards_marks_ineligible_and_redeemed(session, student, award):
    repo = AwardRepository(session)
    service = AwardService(repo)

    session.add(Redemption(student_id=student.id, award_id=award.id, status="completed", redemptionDate=datetime.now()))
    session.commit()

    awards = service.get_available_awards(student_id=student.id, total_hours=20)

    assert awards[0]["available"] is False
    assert awards[0]["already_redeemed"] is True


@pytest.mark.integration
def test_redeem_award_creates_redemption_and_updates_progress(session, student, award, progress_row):
    repo = AwardRepository(session)
    service = AwardService(repo)

    redeemed = service.redeem(student_id=student.id, award_id=award.id, total_hours=30)

    assert redeemed.status == "completed"
    assert redeemed.student_id == student.id

    updated_progress = session.get(Progress, progress_row.id)
    assert updated_progress.awardsEarned == 1


@pytest.mark.integration
def test_redeem_award_does_not_create_missing_progress(session, student, award):
    repo = AwardRepository(session)
    service = AwardService(repo)

    redeemed = service.redeem(student_id=student.id, award_id=award.id, total_hours=30)

    assert redeemed.status == "completed"
    progress = session.exec(__import__("sqlmodel").select(Progress).where(Progress.student_id == student.id)).first()
    assert progress is None


@pytest.mark.integration
def test_redeem_award_rejects_insufficient_hours(session, student, award):
    repo = AwardRepository(session)
    service = AwardService(repo)

    with pytest.raises(ValueError, match="You need"):
        service.redeem(student_id=student.id, award_id=award.id, total_hours=10)


@pytest.mark.integration
def test_redeem_award_rejects_duplicate(session, student, award):
    repo = AwardRepository(session)
    service = AwardService(repo)

    service.redeem(student_id=student.id, award_id=award.id, total_hours=30)

    with pytest.raises(ValueError, match="already redeemed"):
        service.redeem(student_id=student.id, award_id=award.id, total_hours=30)
