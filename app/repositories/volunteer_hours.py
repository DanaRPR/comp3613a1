from sqlmodel import Session, select
from app.models.volunteer_hours import VolunteerHours
from app.models.user import User


class VolunteerHoursRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, volunteer_hours: VolunteerHours) -> VolunteerHours:
        self.session.add(volunteer_hours)
        self.session.commit()
        self.session.refresh(volunteer_hours)
        return volunteer_hours

    def get_by_id(self, submission_id: int) -> VolunteerHours | None:
        return self.session.get(VolunteerHours, submission_id)

    def get_pending(self) -> list[VolunteerHours]:
        statement = select(VolunteerHours).where(VolunteerHours.status == "pending")
        return self.session.exec(statement).all()

    def get_pending_with_student_names(self) -> list[dict]:
        statement = (
            select(VolunteerHours, User.username)
            .join(User, VolunteerHours.student_id == User.id)
            .where(VolunteerHours.status == "pending")
        )
        rows = self.session.exec(statement).all()
        return [
            {
                "id": sub.id,
                "activity": sub.activity,
                "date": sub.date,
                "hours": sub.hours,
                "student_name": name,
            }
            for sub, name in rows
        ]
