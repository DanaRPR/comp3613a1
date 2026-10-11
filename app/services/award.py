from datetime import datetime
from sqlmodel import select
from app.repositories.award import AwardRepository
from app.models.award import Redemption
from app.models.progress import Progress


class AwardService:
    def __init__(self, repository: AwardRepository):
        self.repository = repository

    def get_available_awards(self, student_id: int, total_hours: int) -> list[dict]:
        awards = self.repository.get_all_awards()
        redeemed_ids = self.repository.get_redeemed_award_ids(student_id)
        result = []
        for award in awards:
            already_redeemed = award.id in redeemed_ids
            available = total_hours >= award.requiredHours and not already_redeemed
            result.append({
                "id": award.id,
                "name": award.name,
                "description": award.description,
                "requiredHours": award.requiredHours,
                "available": available,
                "already_redeemed": already_redeemed,
            })
        return result

    def redeem(self, student_id: int, award_id: int, total_hours: int) -> Redemption:
        awards = self.repository.get_all_awards()
        award = next((a for a in awards if a.id == award_id), None)
        if award is None:
            raise ValueError("Award not found.")

        redeemed_ids = self.repository.get_redeemed_award_ids(student_id)
        if award.id in redeemed_ids:
            raise ValueError("You have already redeemed this award.")

        if total_hours < award.requiredHours:
            raise ValueError(f"You need {award.requiredHours} hours to redeem this award. You have {total_hours}.")

        redemption = Redemption(
            student_id=student_id,
            award_id=award.id,
            status="completed",
        )
        saved = self.repository.add_redemption(redemption)

        statement = select(Progress).where(Progress.student_id == student_id)
        progress = self.repository.session.exec(statement).first()
        if progress is not None:
            progress.awardsEarned = progress.awardsEarned + 1
            self.repository.session.add(progress)
            self.repository.session.commit()

        return saved
