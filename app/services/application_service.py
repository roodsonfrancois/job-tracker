"""Use cases for displaying job application data."""

from app.database import JobApplicationRepository


class ApplicationService:
    def __init__(self, repository: JobApplicationRepository) -> None:
        self.repository = repository

    def list_applications(self):
        return self.repository.list_all()

    def get_summary(self) -> dict[str, int]:
        return self.repository.summary()
