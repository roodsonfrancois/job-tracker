from datetime import date

import pytest

from app.database import JobApplicationRepository
from app.services.application_service import ApplicationService


@pytest.fixture
def service(tmp_path):
    return ApplicationService(JobApplicationRepository(tmp_path / "job_tracker.db"))


def valid_values(**overrides):
    values = {"company": " Acme ", "position": " Engineer ", "status": "Applied"}
    values.update(overrides)
    return values


def test_create_and_retrieve_application(service):
    application_id = service.create_application(**valid_values(location=" Remote "))
    application = service.get_application(application_id)
    assert (application["company"], application["position"], application["location"]) == (
        "Acme", "Engineer", "Remote"
    )


def test_list_applications(service):
    service.create_application(**valid_values(company="First"))
    service.create_application(**valid_values(company="Second"))
    assert {row["company"] for row in service.list_applications()} == {"First", "Second"}


def test_update_application(service):
    application_id = service.create_application(**valid_values())
    assert service.update_application(application_id, **valid_values(company="New Name", status="Offer"))
    assert service.get_application(application_id)["company"] == "New Name"
    assert service.get_application(application_id)["status"] == "Offer"


def test_update_missing_application_returns_false(service):
    assert not service.update_application(999, **valid_values())


def test_delete_application(service):
    application_id = service.create_application(**valid_values())
    assert service.delete_application(application_id)
    assert service.get_application(application_id) is None
    assert not service.delete_application(application_id)


@pytest.mark.parametrize("field", ["company", "position", "status"])
def test_required_fields(service, field):
    with pytest.raises(ValueError, match="required"):
        service.create_application(**valid_values(**{field: "  "}))


def test_invalid_status_rejected(service):
    with pytest.raises(ValueError, match="Invalid application status"):
        service.create_application(**valid_values(status="Maybe"))


def test_valid_dates_are_stored_as_iso_dates(service):
    application_id = service.create_application(
        **valid_values(date_applied="2026-09-07", follow_up_date="2026-09-14")
    )
    application = service.get_application(application_id)
    assert application["date_applied"] == date(2026, 9, 7).isoformat()
    assert application["follow_up_date"] == date(2026, 9, 14).isoformat()


@pytest.mark.parametrize("value", ["09/07/2026", "2026-02-30", "tomorrow"])
def test_invalid_date_rejected(service, value):
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        service.create_application(**valid_values(date_applied=value))


def test_blank_optional_dates_and_fields_become_null(service):
    application_id = service.create_application(
        **valid_values(date_applied=" ", follow_up_date="", notes="  ", job_url="")
    )
    application = service.get_application(application_id)
    assert application["date_applied"] is None
    assert application["follow_up_date"] is None
    assert application["notes"] is None
    assert application["job_url"] is None


def test_summary_counts(service):
    for status in ("Saved", "Applied", "Applied", "Interview", "Offer", "Rejected"):
        service.create_application(**valid_values(company=status, status=status))
    assert service.get_summary() == {
        "Total": 6, "Applied": 2, "Interviews": 1, "Offers": 1,
    }
