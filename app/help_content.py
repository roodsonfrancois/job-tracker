"""Local, packaged user-help content."""

HELP_TOPICS = (
    ("Getting Started", """1. Add a job application.
2. Enter the company and position.
3. Select the current application status.
4. Record the date you submitted the application.
5. Optionally set a date when you plan to follow up.
6. Add the original job-posting URL and useful notes.
7. Save the application and update its status as the hiring process progresses."""),
    ("Application Fields", """Company — Name of the employer or company.

Position — Job title being applied for.

Location — City, province/state, country, remote, hybrid, or other location details.

Job URL — Link to the original posting. Job Tracker stores the URL; it does not download or synchronize the posting.

Status:
• Saved — An interesting job whose application has not been submitted.
• Applied — The application was submitted.
• Interview — The employer moved the application to the interview stage.
• Offer — A job offer was received.
• Rejected — The employer rejected or closed the application.
• Withdrawn — You withdrew from the hiring process.

Date Applied — Date the application was submitted. Enter YYYY-MM-DD or use the calendar button. It may be left blank when the submission date is not yet known.

Follow-up Date — Optional reference date when you intend to contact the employer or recruiter. Use the calendar button or Clear. Job Tracker V1 does not send notifications.

Notes — Free-form details such as recruiter/contact name, interviews, salary, requirements, next steps, or personal observations. Notes are stored locally but are not encrypted by Job Tracker."""),
    ("Dashboard", """Total is every stored application. Applied, Interviews, and Offers count applications whose current status is Applied, Interview, or Offer. These are current-status counts, not historical events."""),
    ("Search and Filters", """Search matches company, position, and location without regard to letter case. Leading or trailing spaces do not matter. Select a Status to narrow results. Search and Status can be combined."""),
    ("Sorting", """Click Company, Position, Status, Date Applied, or Follow-up headers to sort. Click the same header again to switch between ascending and descending order."""),
    ("Follow-up Indicators", """Rows with overdue follow-up dates use a pale red background in light mode and dark red in dark mode. Follow-ups due today use pale yellow in light mode and dark gold in dark mode."""),
    ("View, Edit, and Delete", """Select a row to view its details. Use Edit, or double-click the row, to change it. Delete permanently removes the selected application from the active database after confirmation. Create periodic backups for important data."""),
    ("Open Job Posting", """Job Tracker stores the URL and opens it in your default web browser. Internet access may be required. Job Tracker does not control whether an external posting remains available."""),
    ("CSV Export", """Export All CSV writes every stored application, regardless of the current search or filter. The file can be opened in spreadsheet applications such as Excel or LibreOffice Calc, but neither is required. Exporting does not remove or modify Job Tracker data."""),
    ("Create Backup", """Create Backup writes a separate SQLite backup file to a location you choose. Create backups periodically and before major changes."""),
    ("Restore Backup — Warning", """Restore replaces current working data with the selected valid Job Tracker backup. The application validates the database, requires confirmation, and attempts to create a safety backup of current data before restoration. Review the selected file carefully."""),
    ("Local Data and Privacy", """Job Tracker is local-first. Application information is stored on your computer. There is no account, cloud synchronization, telemetry, analytics, or AI data transmission. Opening a Job URL is the exception because it launches an external website.

Linux data: ~/.local/share/JobTracker/ (or XDG_DATA_HOME when configured)
Windows data: %LOCALAPPDATA%\\JobTracker\\"""),
    ("Troubleshooting", """Application does not open — Confirm the application was installed/built for your operating system. Check job_tracker.log in the local data directory for diagnostic information.

Invalid date — Use YYYY-MM-DD, for example 2026-09-07, or select a date with the calendar.

Job URL does not open — Confirm it starts with http:// or https://, the default browser works, and internet connectivity is available.

Backup cannot be restored — Select a readable .db backup created by Job Tracker. Invalid or incompatible databases are rejected.

CSV cannot be saved — Choose a writable folder and ensure the destination file is not locked by another application.

Data appears missing — Confirm you are using the same operating-system user account and application environment. Restore from a known backup where appropriate. Do not manually edit the database."""),
)

HELP_SECTION_TITLES = tuple(title for title, _content in HELP_TOPICS)
