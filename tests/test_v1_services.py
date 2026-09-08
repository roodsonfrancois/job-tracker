import csv
import sqlite3
from datetime import datetime

import pytest

from app.config import APP_VERSION
from app.database import JobApplicationRepository
from app.services.application_service import ApplicationService
from app.services.file_service import CSV_COLUMNS, FileService
from app.services.url_service import validate_job_url


@pytest.fixture
def services(tmp_path):
    repository = JobApplicationRepository(tmp_path / "current.db")
    return ApplicationService(repository), FileService(repository)


def add(service, company="Acme", position="Engineer", location="Remote",
        status="Saved", date_applied="", follow_up_date="", notes="", job_url=""):
    return service.create_application(
        company=company, position=position, location=location, status=status,
        date_applied=date_applied, follow_up_date=follow_up_date, notes=notes,
        job_url=job_url,
    )


@pytest.mark.parametrize(
    ("query", "expected"),
    [("acme", "Acme"), ("ENGINEER", "Acme"), (" toronto ", "Beta")],
)
def test_search_company_position_location_is_case_insensitive(services, query, expected):
    service, _ = services
    add(service)
    add(service, company="Beta", position="Support", location="Toronto")
    assert [row["company"] for row in service.list_applications(query=query)] == [expected]


def test_empty_search_and_combined_status_filter(services):
    service, _ = services
    add(service, company="Support One", status="Interview")
    add(service, company="Support Two", status="Applied")
    add(service, company="Other", status="Interview")
    assert len(service.list_applications(query="  ")) == 3
    assert [row["company"] for row in service.list_applications(
        query="support", status="Interview"
    )] == ["Support One"]


@pytest.mark.parametrize("field", ["company", "position", "status"])
def test_text_sorting_toggles_direction(services, field):
    service, _ = services
    add(service, company="Zulu", position="Writer", status="Saved")
    add(service, company="alpha", position="Analyst", status="Offer")
    ascending = [row[field].lower() for row in service.list_applications(
        sort_by=field, descending=False
    )]
    descending = [row[field].lower() for row in service.list_applications(
        sort_by=field, descending=True
    )]
    assert ascending == sorted(ascending)
    assert descending == sorted(descending, reverse=True)


@pytest.mark.parametrize("field", ["date_applied", "follow_up_date"])
def test_date_sorting_handles_blanks(services, field):
    service, _ = services
    add(service, company="Blank")
    add(service, company="Later", **{field: "2026-09-20"})
    add(service, company="Earlier", **{field: "2026-09-01"})
    rows = service.list_applications(sort_by=field, descending=False)
    assert {row["company"] for row in rows} == {"Blank", "Later", "Earlier"}
    assert rows[-1][field] == "2026-09-20"


def test_invalid_sort_and_filter_are_rejected(services):
    service, _ = services
    with pytest.raises(ValueError, match="Unsupported sort"):
        service.list_applications(sort_by="drop table")
    with pytest.raises(ValueError, match="Invalid application status"):
        service.list_applications(status="Unknown")


@pytest.mark.parametrize("url", ["http://example.com/job", " https://jobs.example.org/a "])
def test_valid_job_urls(url):
    assert validate_job_url(url) == url.strip()


@pytest.mark.parametrize("url", ["", "example.com", "ftp://example.com", "https://"])
def test_invalid_job_urls(url):
    with pytest.raises(ValueError, match="http"):
        validate_job_url(url)


def test_csv_export_handles_unicode_quotes_commas_and_multiline(services, tmp_path):
    service, files = services
    add(
        service, company="Café, Inc.", position='Senior "Builder"',
        notes="First line\nSecond line", job_url="https://example.com/job",
    )
    destination = tmp_path / "applications.csv"
    assert files.export_csv(destination) == 1
    with destination.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.reader(source))
    assert rows[0] == [heading for _, heading in CSV_COLUMNS]
    assert rows[1][0] == "Café, Inc."
    assert rows[1][1] == 'Senior "Builder"'
    assert rows[1][7] == "First line\nSecond line"


def test_empty_csv_export_does_not_create_file(services, tmp_path):
    _, files = services
    destination = tmp_path / "empty.csv"
    assert files.export_csv(destination) == 0
    assert not destination.exists()


def test_backup_contains_expected_records(services, tmp_path):
    service, files = services
    add(service, company="Backed Up")
    destination = files.create_backup(tmp_path / "backup.db")
    with sqlite3.connect(destination) as connection:
        assert connection.execute("SELECT company FROM job_applications").fetchone()[0] == "Backed Up"


def test_backup_default_name(services):
    _, files = services
    assert files.default_backup_name(datetime(2026, 9, 7, 18, 30)) == (
        "job_tracker_backup_2026-09-07_183000.db"
    )


def test_restore_valid_backup_and_creates_current_data_safety_backup(services, tmp_path):
    service, files = services
    add(service, company="Current")
    backup_repository = JobApplicationRepository(tmp_path / "selected.db")
    backup_service = ApplicationService(backup_repository)
    add(backup_service, company="Restored")

    safety = files.restore_backup(tmp_path / "selected.db", tmp_path / "safety")

    assert service.list_applications()[0]["company"] == "Restored"
    with sqlite3.connect(safety) as connection:
        assert connection.execute("SELECT company FROM job_applications").fetchone()[0] == "Current"


def test_restore_rejects_non_sqlite_and_preserves_current_data(services, tmp_path):
    service, files = services
    add(service, company="Current")
    invalid = tmp_path / "invalid.db"
    invalid.write_text("not sqlite", encoding="utf-8")
    with pytest.raises(ValueError, match="SQLite"):
        files.restore_backup(invalid, tmp_path / "safety")
    assert service.list_applications()[0]["company"] == "Current"


def test_restore_rejects_database_without_schema(services, tmp_path):
    _, files = services
    wrong = tmp_path / "wrong.db"
    with sqlite3.connect(wrong) as connection:
        connection.execute("CREATE TABLE something_else (id INTEGER)")
    with pytest.raises(ValueError, match="not a Job Tracker"):
        files.validate_backup(wrong)


def test_restore_rejects_active_database_as_source(services, tmp_path):
    _, files = services
    with pytest.raises(ValueError, match="onto itself"):
        files.restore_backup(files.repository.database_path, tmp_path / "safety")


def test_version_is_v1():
    assert APP_VERSION == "1.0.0"
