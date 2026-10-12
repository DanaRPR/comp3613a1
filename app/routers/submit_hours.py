from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.volunteer_hours import VolunteerHoursRepository
from app.services.volunteer_hours import VolunteerHoursService
from . import router, templates


@router.get("/app/submit", response_class=HTMLResponse)
async def submit_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    return templates.TemplateResponse(
        request=request,
        name="submit_hours.html",
        context={"user": user},
    )


@router.post("/app/submit", response_class=HTMLResponse)
async def submit_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    date: Annotated[datetime, Form()],
    hours: Annotated[int, Form(gt=0)],
    activity: Annotated[str, Form()],
):
    repo = VolunteerHoursRepository(db)
    service = VolunteerHoursService(repo)

    try:
        service.submit_hours(
            student_id=user.id,
            date=date,
            hours=hours,
            activity=activity,
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="submit_hours.html",
            context={"user": user, "error": strr(exc)},
            status_code=400,
        )

    return templates.TemplateResponse(
        request=request,
        name="submit_hours.html",
        context={"user": user, "success": "Submitted! An administrator will review it sonn."},
    )    
    
    
    
     