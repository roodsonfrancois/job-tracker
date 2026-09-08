"""Job Tracker application entry point."""

import logging

from app.config import get_app_data_dir, get_log_path
from app.database import JobApplicationRepository
from app.services.application_service import ApplicationService
from app.ui.main_window import MainWindow


def create_app() -> MainWindow:
    data_directory = get_app_data_dir()
    data_directory.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=get_log_path(), level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    repository = JobApplicationRepository()
    return MainWindow(ApplicationService(repository))


def main() -> None:
    try:
        app = create_app()
        app.mainloop()
    except Exception:
        logging.getLogger(__name__).exception("Unexpected application failure")
        raise


if __name__ == "__main__":
    main()
