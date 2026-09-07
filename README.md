# Job Tracker

Job Tracker is a simple, reliable desktop application for keeping job application
records locally. It provides local create, read, update, and delete workflows,
status summaries, an offline SQLite database, and a maintainable desktop architecture.

## Technologies

- Python 3
- CustomTkinter desktop GUI
- SQLite local storage (through Python's standard library)
- pytest

The application is designed to work offline on Linux and Windows. Windows support
is a project requirement, but this version has not been runtime-tested on Windows.

## Project structure

```text
app/
├── main.py                    # Application entry point
├── config.py                  # Cross-platform local-data paths
├── database.py                # SQLite schema and repository
├── models.py                  # Domain model and statuses
├── services/
│   └── application_service.py # UI-facing application logic
├── ui/
│   └── main_window.py         # CustomTkinter window shell
└── assets/                    # Future local visual assets
tests/                         # Isolated pytest suite
```

Application data is created outside the source tree. By default it is stored in
`~/.local/share/JobTracker/job_tracker.db` on Linux (or under `XDG_DATA_HOME` when
set) and `%LOCALAPPDATA%\JobTracker\job_tracker.db` on Windows.

## Linux development setup

Install Python 3, its virtual-environment support, and Tk. Package names vary by
distribution; on Debian/Ubuntu these are commonly `python3`, `python3-venv`, and
`python3-tk`.

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the desktop application:

```bash
python -m app.main
```

Use **+ Add Application** to create a record. Select any row to inspect its full
details or to edit or delete it. Dates are optional and, when provided, must use
the `YYYY-MM-DD` format. Deletion always asks for confirmation.

Run tests:

```bash
python -m pytest
```
