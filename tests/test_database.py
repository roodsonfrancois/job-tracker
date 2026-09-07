import sqlite3

import pytest

from app.database import JobApplicationRepository, initialize_database
from app.models import ALLOWED_STATUSES, JobApplication


def test_database_and_parent_directory_are_created(tmp_path):
    path = tmp_path / "new" / "job_tracker.db"
    assert initialize_database(path) == path
    assert path.is_file()


def test_job_applications_table_has_expected_columns(tmp_path):
    path = initialize_database(tmp_path / "job_tracker.db")
    with sqlite3.connect(path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(job_applications)")}
    assert columns == {
        "id", "company", "position", "location", "job_url", "status",
        "date_applied", "follow_up_date", "notes", "created_at", "updated_at",
    }


def test_reinitialization_preserves_existing_data(tmp_path):
    path = tmp_path / "job_tracker.db"
    repository = JobApplicationRepository(path)
    repository.add(JobApplication(company="Example Co", position="Developer"))
    initialize_database(path)
    assert len(JobApplicationRepository(path).list_all()) == 1


@pytest.mark.parametrize("status", ALLOWED_STATUSES)
def test_all_allowed_statuses_can_be_inserted(tmp_path, status):
    repository = JobApplicationRepository(tmp_path / "job_tracker.db")
    repository.add(JobApplication(company="Example Co", position="Developer", status=status))
    assert repository.list_all()[0]["status"] == status


def test_invalid_status_is_rejected_by_model():
    with pytest.raises(ValueError, match="Invalid application status"):
        JobApplication(company="Example Co", position="Developer", status="Unknown")


def test_invalid_status_is_rejected_by_database(tmp_path):
    path = initialize_database(tmp_path / "job_tracker.db")
    with sqlite3.connect(path) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO job_applications (company, position, status) VALUES (?, ?, ?)",
            ("Example Co", "Developer", "Unknown"),
        )
