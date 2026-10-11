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
    progress = leaderboard_service.get_progress(user.id)
    return templates.TemplateResponse(
        request=request,
        name="progress.html",
        context={"user": user, "progress": progress},
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