from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.award import AwardRepository
from app.services.award import AwardService
from . import router, templates


@router.get("/app/awards", response_class=HTMLResponse)
async def awards_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    award_service = AwardService(AwardRepository(db))
    awards = award_service.get_available_awards(user.id, total_hours=user.totalVolunteerHours)
    return templates.TemplateResponse(
        request=request,
        name="awards.html",
        context={"user": user, "awards": awards},
    )


@router.post("/app/awards/redeem/{award_id}", response_class=HTMLResponse)
async def award_redeem(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    award_id: int,
):
    award_service = AwardService(AwardRepository(db))
    try:
        award_service.redeem(user.id, award_id, total_hours=user.totalVolunteerHours)
    except ValueError:
        pass
    return RedirectResponse(url="/app/awards", status_code=303)
    