"""Domain models used by Job Tracker."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class ApplicationStatus(str, Enum):
    SAVED = "Saved"
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


ALLOWED_STATUSES = tuple(status.value for status in ApplicationStatus)


def validate_status(status: str) -> str:
    """Return a valid status or raise a clear domain-level error."""
    if status not in ALLOWED_STATUSES:
        raise ValueError(
            f"Invalid application status {status!r}; expected one of "
            f"{', '.join(ALLOWED_STATUSES)}"
        )
    return status


@dataclass(slots=True)
class JobApplication:
    company: str
    position: str
    status: str = ApplicationStatus.SAVED.value
    location: str | None = None
    job_url: str | None = None
    date_applied: date | None = None
    follow_up_date: date | None = None
    notes: str | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        validate_status(self.status)
