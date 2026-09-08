"""Job-application use cases and input validation."""

from __future__ import annotations

from datetime import date

from app.database import JobApplicationRepository
from app.models import ApplicationStatus, JobApplication, validate_status


class ApplicationService:
    def __init__(self, repository: JobApplicationRepository) -> None:
        self.repository = repository

    def list_applications(
        self, query: str = "", status: str | None = None,
        sort_by: str = "created_at", descending: bool = True,
    ):
        return self.repository.search(query, status, sort_by, descending)

    def get_application(self, application_id: int):
        return self.repository.get_by_id(application_id)

    def create_application(self, **values: str) -> int:
        return self.repository.add(self._build_application(values))

    def update_application(self, application_id: int, **values: str) -> bool:
        return self.repository.update(application_id, self._build_application(values))

    def delete_application(self, application_id: int) -> bool:
        return self.repository.delete(application_id)

    def get_summary(self) -> dict[str, int]:
        return self.repository.summary()

    @staticmethod
    def _build_application(values: dict[str, str]) -> JobApplication:
        cleaned = {key: value.strip() for key, value in values.items()}
        company = cleaned.get("company", "")
        position = cleaned.get("position", "")
        status = cleaned.get("status", ApplicationStatus.SAVED.value)
        if not company:
            raise ValueError("Company is required.")
        if not position:
            raise ValueError("Position is required.")
        if not status:
            raise ValueError("Status is required.")
        validate_status(status)
        return JobApplication(
            company=company,
            position=position,
            location=cleaned.get("location") or None,
            job_url=cleaned.get("job_url") or None,
            status=status,
            date_applied=ApplicationService._parse_date(
                cleaned.get("date_applied", ""), "Date applied"
            ),
            follow_up_date=ApplicationService._parse_date(
                cleaned.get("follow_up_date", ""), "Follow-up date"
            ),
            notes=cleaned.get("notes") or None,
        )

    @staticmethod
    def _parse_date(value: str, field_name: str) -> date | None:
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError as error:
            raise ValueError(f"{field_name} must use YYYY-MM-DD format.") from error
