"""CSV export and safe SQLite backup/restore operations."""

from __future__ import annotations

import csv
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from app.database import JobApplicationRepository

CSV_COLUMNS = (
    ("company", "Company"), ("position", "Position"), ("location", "Location"),
    ("job_url", "Job URL"), ("status", "Status"), ("date_applied", "Date Applied"),
    ("follow_up_date", "Follow-up Date"), ("notes", "Notes"),
    ("created_at", "Created At"), ("updated_at", "Updated At"),
)
EXPECTED_COLUMNS = {"id", *(column for column, _ in CSV_COLUMNS)}


class FileService:
    def __init__(self, repository: JobApplicationRepository) -> None:
        self.repository = repository

    def export_csv(self, destination: Path | str) -> int:
        rows = self.repository.list_all()
        if not rows:
            return 0
        with Path(destination).open("w", encoding="utf-8-sig", newline="") as output:
            writer = csv.writer(output)
            writer.writerow([heading for _, heading in CSV_COLUMNS])
            writer.writerows(
                [(row[column] if row[column] is not None else "") for column, _ in CSV_COLUMNS]
                for row in rows
            )
        return len(rows)

    def create_backup(self, destination: Path | str) -> Path:
        return self.repository.backup_to(destination)

    def default_backup_name(self, now: datetime | None = None) -> str:
        stamp = (now or datetime.now()).strftime("%Y-%m-%d_%H%M%S")
        return f"job_tracker_backup_{stamp}.db"

    def validate_backup(self, source: Path | str) -> None:
        source = Path(source)
        if not source.is_file():
            raise ValueError("The selected backup file does not exist.")
        try:
            with closing(sqlite3.connect(f"{source.resolve().as_uri()}?mode=ro", uri=True)) as connection:
                if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("The selected file is not a valid SQLite database.")
                table = connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' "
                    "AND name = 'job_applications'"
                ).fetchone()
                if table is None:
                    raise ValueError("The selected database is not a Job Tracker backup.")
                columns = {
                    row[1] for row in connection.execute("PRAGMA table_info(job_applications)")
                }
                if not EXPECTED_COLUMNS.issubset(columns):
                    raise ValueError("The selected database has an incompatible schema.")
        except sqlite3.Error as error:
            raise ValueError("The selected file is not a readable SQLite database.") from error

    def restore_backup(self, source: Path | str, safety_directory: Path | str) -> Path:
        if Path(source).resolve() == self.repository.database_path.resolve():
            raise ValueError("The active database cannot be restored onto itself.")
        self.validate_backup(source)
        safety_path = Path(safety_directory) / self.default_backup_name()
        counter = 1
        while safety_path.exists():
            safety_path = safety_path.with_stem(f"{safety_path.stem}_{counter}")
            counter += 1
        self.create_backup(safety_path)
        try:
            source_uri = f"{Path(source).resolve().as_uri()}?mode=ro"
            with closing(sqlite3.connect(source_uri, uri=True)) as backup:
                with closing(sqlite3.connect(self.repository.database_path)) as current:
                    backup.backup(current)
        except Exception:
            with closing(sqlite3.connect(safety_path)) as safety:
                with closing(sqlite3.connect(self.repository.database_path)) as current:
                    safety.backup(current)
            raise
        return safety_path
