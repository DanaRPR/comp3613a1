from datetime import datetime
from sqlmodel import Session, select
from app.repositories.volunteer_hours import VolunteerHoursRepository
from app.models.volunteer_hours import VolunteerHours
from app.models.user import User
from app.models.progress import Progress


class VolunteerHoursService:
    def __init__(self, repository: VolunteerHoursRepository):
        self.repository = repository

    def submit_hours(self, date: datetime, hours: int, activity: str, student_id: int) -> VolunteerHours:
        submission = VolunteerHours(
            date=date,
            hours=hours,
            activity=activity,
            student_id=student_id,
            status="pending",
        )
        return self.repository.add(submission)

    def get_pending_with_student_names(self) -> list[dict]:
        return self.repository.get_pending_with_student_names()

    def approve(self, submission_id: int, administrator_id: int) -> VolunteerHours:
        submission = self.repository.get_by_id(submission_id)
        if submission is None:
            raise ValueError("Submission not found.")
        if submission.status != "pending":
            raise ValueError("Submission has already been reviewed.")

        submission.status = "approved"
        submission.administrator_id = administrator_id
        self.repository.session.add(submission)

        student = self.repository.session.get(User, submission.student_id)
        if student is None:
            raise ValueError("Student not found.")
        student.totalVolunteerHours = student.totalVolunteerHours + submission.hours
        self.repository.session.add(student)

        statement = select(Progress).where(Progress.student_id == student.id)
        progress = self.repository.session.exec(statement).first()
        if progress is None:
            progress = Progress(
                totalHours=submission.hours,
                awardsEarned=0,
                student_id=student.id,
            )
        else:
            progress.totalHours = progress.totalHours + submission.hours
            self.repository.session.add(progress)

        self.repository.session.add(progress)
        self.repository.session.commit()
        self.repository.session.refresh(submission)
        return submission

    def reject(self, submission_id: int, administrator_id: int) -> VolunteerHours:
        submission = self.repository.get_by_id(submission_id)
        if submission is None:
            raise ValueError("Submission not found.")
        if submission.status != "pending":
            raise ValueError("Submission has already been reviewed.")

        submission.status = "rejected"
        submission.administrator_id = administrator_id
        self.repository.session.add(submission)
        self.repository.session.commit()
        self.repository.session.refresh(submission)
        return submission
