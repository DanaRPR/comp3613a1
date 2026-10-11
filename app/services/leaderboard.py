from sqlmodel import select
from app.repositories.leaderboard import LeaderboardRepository
from app.models.progress import Progress
from app.models.award import Award, Redemption


class LeaderboardService:
    def __init__(self, repository: LeaderboardRepository):
        self.repository = repository

    def get_leaderboard(self, current_student_id: int) -> list[dict]:
        rows = self.repository.get_all_students_by_hours()
        leaderboard = []
        for rank, (student, hours) in enumerate(rows, start=1):
            leaderboard.append({
                "rank": rank,
                "name": student.username,
                "hours": hours,
                "is_current": student.id == current_student_id,
            })
        return leaderboard

    def get_progress(self, student_id: int) -> dict:
        progress = self.repository.get_progress(student_id)

        statement = select(Award).order_by(Award.requiredHours)
        all_awards = self.repository.session.exec(statement).all()

        redeemed_statement = select(Redemption.award_id).where(Redemption.student_id == student_id)
        redeemed_ids = list(self.repository.session.exec(redeemed_statement).all())

        next_award = None
        next_threshold = None
        for award in all_awards:
            if award.id not in redeemed_ids:
                next_award = award
                next_threshold = award.requiredHours
                break

        return {
            "progress": progress,
            "next_award": next_award,
            "next_threshold": next_threshold,
        }
