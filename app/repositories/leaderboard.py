from sqlmodel import Session, select
from app.models.user import User
from app.models.progress import Progress


class LeaderboardRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_students_by_hours(self) -> list[tuple[User, int]]:
        statement = select(User).where(User.role != "admin").order_by(User.totalVolunteerHours.desc())
        users = self.session.exec(statement).all()
        return [(u, u.totalVolunteerHours) for u in users]

    def get_progress(self, student_id: int) -> Progress | None:
        statement = select(Progress).where(Progress.student_id == student_id)
        return self.session.exec(statement).first()
