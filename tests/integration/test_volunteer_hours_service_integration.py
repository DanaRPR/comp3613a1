from datetime import datetime

import pytest
from sqlmodel import select

from app.models import Progress, User, VolunteerHours
from app.repositories.volunteer_hours import VolunteerHoursRepository
from app.services.volunteer_hours import VolunteerHoursService


@pytest.mark.integration
def test_submit_hours_creates_pending_submission(session, student):
    repo = VolunteerHoursRepository(session)
    service = VolunteerHoursService(repo)

    created = service.submit_hours(
        date=datetime(2026, 2, 1),
        hours=5,
        activity="Reading mentor",
        student_id=student.id,
    )

    saved = session.get(VolunteerHours, created.id)
    assert saved is not None
    assert saved.status == "pending"
    assert saved.student_id == student.id
    assert saved.hours == 5


@pytest.mark.integration
def test_approve_submission_updates_student_and_progress(session, student, volunteer_submission):
    repo = VolunteerHoursRepository(session)
    service = VolunteerHoursService(repo)

    progress = Progress(totalHours=0, awardsEarned=0, student_id=student.id)
    session.add(progress)
    session.commit()
    session.refresh(progress)

    approved = service.approve(volunteer_submission.id, administrator_id=student.id)

    assert approved.status == "approved"
    updated_student = session.get(User, student.id)
    assert updated_student.totalVolunteerHours == 8

    updated_progress = session.get(Progress, progress.id)
    assert updated_progress.totalHours == 8
    assert updated_progress.awardsEarned == 0


@pytest.mark.integration
def test_approve_submission_creates_progress_when_missing(session, student, volunteer_submission):
    repo = VolunteerHoursRepository(session)
    service = VolunteerHoursService(repo)

    approved = service.approve(volunteer_submission.id, administrator_id=student.id)

    assert approved.status == "approved"
    progress = session.exec(select(Progress).where(Progress.student_id == student.id)).first()
    assert progress is not None
    assert progress.totalHours == 8
    assert progress.awardsEarned == 0


@pytest.mark.integration
def test_approve_submission_rejects_duplicate_review(session, student, volunteer_submission):
    repo = VolunteerHoursRepository(session)
    service = VolunteerHoursService(repo)

    service.approve(volunteer_submission.id, administrator_id=student.id)

    with pytest.raises(ValueError, match="already been reviewed"):
        service.approve(volunteer_submission.id, administrator_id=student.id)


@pytest.mark.integration
def test_approve_missing_submission_raises_value_error(session):
    repo = VolunteerHoursRepository(session)
    service = VolunteerHoursService(repo)

    with pytest.raises(ValueError, match="Submission not found"):
        service.approve(999, administrator_id=1)


@pytest.mark.integration
def test_reject_submission_sets_rejected_status(session, volunteer_submission):
    repo = VolunteerHoursRepository(session)
    service = VolunteerHoursService(repo)

    rejected = service.reject(volunteer_submission.id, administrator_id=7)

    assert rejected.status == "rejected"
    assert rejected.administrator_id == 7


@pytest.mark.integration
def test_reject_missing_submission_raises_value_error(session):
    repo = VolunteerHoursRepository(session)
    service = VolunteerHoursService(repo)

    with pytest.raises(ValueError, match="Submission not found"):
        service.reject(999, administrator_id=1)


@pytest.mark.integration
def test_pending_submissions_include_student_names(session):
    student_1 = User(username="student1", email="student1@example.com", password="secret", role="student", totalVolunteerHours=0)
    student_2 = User(username="student2", email="student2@example.com", password="secret", role="student", totalVolunteerHours=0)
    session.add_all([student_1, student_2])
    session.commit()

    pending_1 = VolunteerHours(date=datetime(2026, 1, 10), hours=4, activity="Reading", student_id=student_1.id, status="pending")
    reviewed = VolunteerHours(date=datetime(2026, 1, 11), hours=6, activity="Half marathon", student_id=student_2.id, status="approved")
    pending_2 = VolunteerHours(date=datetime(2026, 1, 12), hours=3, activity="Tutoring", student_id=student_2.id, status="pending")
    session.add_all([pending_1, reviewed, pending_2])
    session.commit()

    rows = VolunteerHoursRepository(session).get_pending_with_student_names()

    assert len(rows) == 2
    assert {row["student_name"] for row in rows} == {"student1", "student2"}
    assert {row["activity"] for row in rows} == {"Reading", "Tutoring"}
