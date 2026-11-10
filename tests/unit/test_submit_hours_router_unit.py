from types import SimpleNamespace

import pytest
from starlette.requests import Request

from app.routers import submit_hours


class FakeTemplates:
    def TemplateResponse(self, **kwargs):
        return SimpleNamespace(**kwargs)


class FailingVolunteerHoursService:
    def __init__(self, repository):
        self.repository = repository

    def submit_hours(self, **kwargs):
        raise ValueError("invalid submission")


@pytest.mark.unit
async def test_submit_action_renders_value_error_message(monkeypatch):
    monkeypatch.setattr(submit_hours, "templates", FakeTemplates())
    monkeypatch.setattr(
        submit_hours,
        "VolunteerHoursService",
        FailingVolunteerHoursService,
    )
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/app/submit",
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("testclient", 123),
        }
    )

    response = await submit_hours.submit_action(
        request=request,
        user=SimpleNamespace(id=7),
        db=object(),
        date=None,
        hours=5,
        activity="Community clean-up",
    )

    assert response.status_code == 400
    assert response.name == "submit_hours.html"
    assert response.context["error"] == "invalid submission"
