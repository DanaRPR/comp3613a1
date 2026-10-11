from sqlmodel import Session, select
from app.models.award import Award, Redemption


class AwardRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_awards(self) -> list[Award]:
        statement = select(Award).order_by(Award.requiredHours)
        return self.session.exec(statement).all()

    def get_redeemed_award_ids(self, student_id: int) -> list[int]:
        statement = select(Redemption.award_id).where(Redemption.student_id == student_id)
        return list(self.session.exec(statement).all())

    def add_redemption(self, redemption: Redemption) -> Redemption:
        self.session.add(redemption)
        self.session.commit()
        self.session.refresh(redemption)
        return redemption
