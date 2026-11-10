from types import SimpleNamespace

import pytest

from app.models.user import User
from app.models.volunteer_hours import VolunteerHours
from app.services.volunteer_hours import VolunteerHoursService


class FakeExecResult:
    def __init__(self, value):
        self._value = value

    def first(self):
        return self._value


class FakeSession:
    def __init__(self, student=None, progress=None):
        self.student = student
        self.progress = progress
        self.added = []

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass

    def get(self, model, obj_id):
        if model is User and self.student is not None and self.student.id == obj_id:
            return self.student
        return None

    def exec(self, statement):
        query = str(statement).lower()
        if "progress" in query and "where" in query:
            return FakeExecResult(self.progress)
        return FakeExecResult(None)


class FakeVolunteerHoursRepository:
    def __init__(self, submission=None, student=None, progress=None):
        self.session = FakeSession(student=student, progress=progress)
        self.submission = submission

    def add(self, volunteer_hours):
        self.submission = volunteer_hours
        return volunteer_hours

    def get_by_id(self, submission_id):
        if self.submission is not None and self.submission.id == submission_id:
            return self.submission
        return None


@pytest.mark.unit
def test_submit_hours_adds_pending_submission():
    repo = FakeVolunteerHoursRepository()
    service = VolunteerHoursService(repo)

    result = service.submit_hours(
        date="2026-02-01",
        hours=5,
        activity="Reading mentor",
        student_id=7,
    )

    assert result.status == "pending"
    assert result.student_id == 7
    assert result.hours == 5
    assert result.activity == "Reading mentor"
    assert repo.submission is result


@pytest.mark.unit
def test_approve_updates_submission_and_totals():
    student = SimpleNamespace(id=7, totalVolunteerHours=10)
    progress = SimpleNamespace(id=2, totalHours=15, awardsEarned=0, student_id=7)
    submission = VolunteerHours(
        id=3,
        student_id=7,
        hours=8,
        activity="Library volunteering",
        status="pending",
        administrator_id=None,
    )
    repo = FakeVolunteerHoursRepository(submission=submission, student=student, progress=progress)
    service = VolunteerHoursService(repo)

    approved = service.approve(3, administrator_id=9)

    assert approved.status == "approved"
    assert approved.administrator_id == 9
    assert student.totalVolunteerHours == 18
    assert progress.totalHours == 23
    assert repo.session.added


@pytest.mark.unit
def test_approve_raises_value_error_for_missing_submission():
    repo = FakeVolunteerHoursRepository()
    service = VolunteerHoursService(repo)

    with pytest.raises(ValueError, match="Submission not found"):
        service.approve(123, administrator_id=9)


@pytest.mark.unit
def test_reject_marks_submission_rejected():
    submission = VolunteerHours(
        id=4,
        student_id=3,
        hours=6,
        activity="Beach clean-up",
        status="pending",
        administrator_id=None,
    )
    repo = FakeVolunteerHoursRepository(submission=submission)
    service = VolunteerHoursService(repo)

    rejected = service.reject(4, administrator_id=9)

    assert rejected.status == "rejected"
    assert rejected.administrator_id == 9
    assert repo.session.added
