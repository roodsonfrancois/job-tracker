from datetime import date
from unittest.mock import Mock

from app.config import APP_VERSION
from app.database import JobApplicationRepository
from app.help_content import HELP_SECTION_TITLES, HELP_TOPICS
from app.services.application_service import ApplicationService
from app.ui.calendar_dialog import format_selected_date, initial_calendar_date
from app.ui.calendar_dialog import CalendarDialog


def test_selected_date_uses_existing_iso_format():
    assert format_selected_date(date(2026, 9, 7)) == "2026-09-07"


def test_existing_valid_date_initializes_calendar():
    assert initial_calendar_date(" 2026-09-15 ") == date(2026, 9, 15)


def test_blank_or_invalid_picker_value_defaults_to_today():
    fallback = date(2026, 1, 2)
    assert initial_calendar_date("", fallback) == fallback
    assert initial_calendar_date("not-a-date", fallback) == fallback


def test_calendar_form_value_preserves_database_date_semantics(tmp_path):
    service = ApplicationService(JobApplicationRepository(tmp_path / "test.db"))
    selected = format_selected_date(date(2026, 9, 7))
    application_id = service.create_application(
        company="Acme", position="Engineer", status="Applied",
        date_applied=selected, follow_up_date="",
    )
    saved = service.get_application(application_id)
    assert saved["date_applied"] == "2026-09-07"
    assert saved["follow_up_date"] is None


def test_replacing_date_entry_allows_selection_and_clear():
    from app.ui.application_dialog import ApplicationDialog

    entry = Mock()
    ApplicationDialog._replace_entry(entry, "2026-09-07")
    entry.delete.assert_called_once_with(0, "end")
    entry.insert.assert_called_once_with(0, "2026-09-07")


def test_calendar_close_releases_grab_and_returns_it_to_parent():
    parent = Mock()
    parent.winfo_exists.return_value = True
    parent.winfo_viewable.return_value = True
    dialog = Mock()
    dialog._parent = parent
    dialog.grab_current.return_value = dialog

    CalendarDialog._close(dialog)

    dialog.grab_release.assert_called_once_with()
    dialog.destroy.assert_called_once_with()
    parent.grab_set.assert_called_once_with()
    parent.lift.assert_called_once_with()


def test_help_contains_all_major_sections_and_centralized_version():
    required = {
        "Getting Started", "Application Fields", "Dashboard", "Search and Filters",
        "Sorting", "Follow-up Indicators", "View, Edit, and Delete",
        "Open Job Posting", "CSV Export", "Create Backup",
        "Restore Backup — Warning", "Local Data and Privacy", "Troubleshooting",
    }
    assert required.issubset(set(HELP_SECTION_TITLES))
    combined = "\n".join(f"{title}\n{body}" for title, body in HELP_TOPICS)
    for field in (
        "Company", "Position", "Location", "Job URL", "Status", "Saved", "Applied",
        "Interview", "Offer", "Rejected", "Withdrawn", "Date Applied",
        "Follow-up Date", "Notes",
    ):
        assert field in combined
    assert APP_VERSION == "1.0.0"
