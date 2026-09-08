# Job Tracker

Job Tracker 1.0 is a simple local-first desktop application for managing job
applications. It runs from one Python codebase on Linux and Windows and requires no
account, web server, or internet connection.

## Features

- Create, view, edit, and delete applications with confirmation
- Search company, position, and location; combine search with status filtering
- Sort by company, position, status, date applied, or follow-up date
- Summary counts for total applications, applied, interviews, and offers
- Visual emphasis for overdue and today follow-ups
- Open validated HTTP/HTTPS job-posting links in the default browser
- Export all records to UTF-8 CSV
- Create consistent SQLite backups and safely restore validated backups
- Local diagnostic logging
- Visual calendar selection for application and follow-up dates
- Complete offline Help available from the dashboard

Application records never leave the computer. There is no analytics, telemetry,
cloud synchronization, or external transmission. **Open Job Posting** is the only
feature that intentionally launches an external website.

## Local data

The application automatically creates its data directory and keeps both the database
and diagnostic log outside the source or executable directory:

- Linux: `~/.local/share/JobTracker/` (or `$XDG_DATA_HOME/JobTracker/`)
- Windows: `%LOCALAPPDATA%\JobTracker\`
- Database: `job_tracker.db`
- Log: `job_tracker.log`

Normal launches and upgrades do not overwrite existing records.

## Setup and development

Python 3.12 is used for builds. Python 3, Tk, and virtual-environment support are
required. On Debian/Ubuntu the relevant packages are commonly `python3`,
`python3-tk`, and `python3-venv`.

Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Run from source or run tests:

```bash
python -m app.main
python -m pytest -q
```

Dates use `YYYY-MM-DD`. Blank optional dates are valid.
Dates can be typed manually or selected with the Calendar button. Follow-up dates
can be cleared directly from the application form. The in-application **Help** window
documents fields, statuses, dashboard behavior, export, backup/restore, privacy, and
troubleshooting without requiring an internet connection.

## CSV and backups

**Export All CSV** exports every persisted application, regardless of the active
search or filter. The CSV includes URLs, notes, and timestamps and is encoded as
UTF-8 with spreadsheet-compatible Unicode support.

**Create Backup** uses SQLite's online backup API. **Restore Backup** first validates
the selected database and schema, asks for confirmation, and creates a timestamped
safety backup of current data before restoring.

## Standalone builds

Install the development requirements, then build on the target operating system:

```bash
python -m PyInstaller --clean --noconfirm JobTracker.spec
```

Linux produces `dist/JobTracker`; Windows produces `dist/JobTracker.exe`. PyInstaller
does not cross-compile, so Windows builds must run on Windows. The included GitHub
Actions workflow tests and builds the Windows executable and uploads it as a workflow
artifact. Generated `build/` and `dist/` directories are intentionally ignored.

The standalone executable continues using the per-user data locations above; it does
not store the database beside the executable.
