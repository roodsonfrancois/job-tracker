"""Job Tracker application entry point."""

from app.database import JobApplicationRepository
from app.services.application_service import ApplicationService
from app.ui.main_window import MainWindow


def create_app() -> MainWindow:
    repository = JobApplicationRepository()
    return MainWindow(ApplicationService(repository))


def main() -> None:
    app = create_app()
    app.mainloop()


if __name__ == "__main__":
    main()
