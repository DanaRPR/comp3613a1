from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.leaderboard import LeaderboardRepository
from app.services.leaderboard import LeaderboardService
from . import router, templates


@router.get("/app/progress", response_class=HTMLResponse)
async def progress_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    leaderboard_service = LeaderboardService(LeaderboardRepository(db))
    data = leaderboard_service.get_progress(user.id)

    return templates.TemplateResponse(
        request=request,
        name="progress.html",
        context={
            "user": user,
            "progress": data["progress"],
            "next_award": data["next_award"],
            "next_threshold": data["next_threshold"],
        },
    )


@router.get("/app/leaderboard", response_class=HTMLResponse)
async def leaderboard_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    leaderboard_service = LeaderboardService(LeaderboardRepository(db))
    leaderboard = leaderboard_service.get_leaderboard(user.id)

    return templates.TemplateResponse(
        request=request,
        name="leaderboard.html",
        context={"user": user, "leaderboard": leaderboard},
    )