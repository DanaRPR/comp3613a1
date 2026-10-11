"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.user import User
from app.models.volunteer_hours import VolunteerHours
from app.models.progress import Progress
from app.models.award import Award, Redemption

__all__ = ["User", "VolunteerHours", "Progress", "Award", "Redemption"]
