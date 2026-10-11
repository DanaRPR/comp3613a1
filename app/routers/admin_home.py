from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep
from app.repositories.volunteer_hours import VolunteerHoursRepository
from app.services.volunteer_hours import VolunteerHoursService
from . import router, templates


@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db: SessionDep,
):
    service = VolunteerHoursService(VolunteerHoursRepository(db))
    pending = service.get_pending_with_student_names()
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"user": user, "pending": pending},
    )


@router.post("/admin/approve/{submission_id}", response_class=HTMLResponse)
async def admin_approve(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    submission_id: int,
):
    service = VolunteerHoursService(VolunteerHoursRepository(db))
    try:
        service.approve(submission_id, administrator_id=user.id)
    except ValueError:
        pass
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/reject/{submission_id}", response_class=HTMLResponse)
async def admin_reject(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    submission_id: int,
):
    service = VolunteerHoursService(VolunteerHoursRepository(db))
    try:
        service.reject(submission_id, administrator_id=user.id)
    except ValueError:
        pass
    return RedirectResponse(url="/admin", status_code=303)
