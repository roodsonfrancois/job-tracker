"""SQLite setup and persistence operations."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

from app.config import get_database_path
from app.models import ALLOWED_STATUSES, JobApplication, validate_status


def _status_check_sql() -> str:
    allowed = ", ".join(f"'{status}'" for status in ALLOWED_STATUSES)
    return f"CHECK (status IN ({allowed}))"


def initialize_database(database_path: Path | str | None = None) -> Path:
    """Create the data directory and schema if absent, preserving all data."""
    path = Path(database_path) if database_path is not None else get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(path)) as connection:
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS job_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL CHECK (length(trim(company)) > 0),
                position TEXT NOT NULL CHECK (length(trim(position)) > 0),
                location TEXT,
                job_url TEXT,
                status TEXT NOT NULL DEFAULT 'Saved' {_status_check_sql()},
                date_applied TEXT,
                follow_up_date TEXT,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    return path


class JobApplicationRepository:
    """Small persistence boundary for job applications."""

    def __init__(self, database_path: Path | str | None = None) -> None:
        self.database_path = initialize_database(database_path)

    def add(self, application: JobApplication) -> int:
        validate_status(application.status)
        with closing(sqlite3.connect(self.database_path)) as connection:
            cursor = connection.execute(
                """
                INSERT INTO job_applications (
                    company, position, location, job_url, status,
                    date_applied, follow_up_date, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    application.company,
                    application.position,
                    application.location,
                    application.job_url,
                    application.status,
                    application.date_applied.isoformat() if application.date_applied else None,
                    application.follow_up_date.isoformat() if application.follow_up_date else None,
                    application.notes,
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def list_all(self) -> list[sqlite3.Row]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(
                "SELECT * FROM job_applications ORDER BY created_at DESC, id DESC"
            ).fetchall()

    def search(
        self,
        query: str = "",
        status: str | None = None,
        sort_by: str = "created_at",
        descending: bool = True,
    ) -> list[sqlite3.Row]:
        sort_columns = {
            "company": "company COLLATE NOCASE",
            "position": "position COLLATE NOCASE",
            "status": "status COLLATE NOCASE",
            "date_applied": "date_applied",
            "follow_up_date": "follow_up_date",
            "created_at": "created_at",
        }
        if sort_by not in sort_columns:
            raise ValueError(f"Unsupported sort field: {sort_by}")
        conditions: list[str] = []
        parameters: list[str] = []
        query = query.strip()
        if query:
            conditions.append(
                "(company LIKE ? COLLATE NOCASE OR position LIKE ? COLLATE NOCASE "
                "OR location LIKE ? COLLATE NOCASE)"
            )
            pattern = f"%{query}%"
            parameters.extend((pattern, pattern, pattern))
        if status:
            validate_status(status)
            conditions.append("status = ?")
            parameters.append(status)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        direction = "DESC" if descending else "ASC"
        column = sort_columns[sort_by]
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(
                f"SELECT * FROM job_applications {where} "
                f"ORDER BY {column} {direction}, id DESC",
                parameters,
            ).fetchall()

    def get_by_id(self, application_id: int) -> sqlite3.Row | None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(
                "SELECT * FROM job_applications WHERE id = ?", (application_id,)
            ).fetchone()

    def update(self, application_id: int, application: JobApplication) -> bool:
        validate_status(application.status)
        with closing(sqlite3.connect(self.database_path)) as connection:
            cursor = connection.execute(
                """
                UPDATE job_applications
                SET company = ?, position = ?, location = ?, job_url = ?,
                    status = ?, date_applied = ?, follow_up_date = ?, notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    application.company, application.position, application.location,
                    application.job_url, application.status,
                    application.date_applied.isoformat() if application.date_applied else None,
                    application.follow_up_date.isoformat() if application.follow_up_date else None,
                    application.notes, application_id,
                ),
            )
            connection.commit()
            return cursor.rowcount == 1

    def delete(self, application_id: int) -> bool:
        with closing(sqlite3.connect(self.database_path)) as connection:
            cursor = connection.execute(
                "DELETE FROM job_applications WHERE id = ?", (application_id,)
            )
            connection.commit()
            return cursor.rowcount == 1

    def summary(self) -> dict[str, int]:
        counts = {"Total": 0, "Applied": 0, "Interviews": 0, "Offers": 0}
        with closing(sqlite3.connect(self.database_path)) as connection:
            rows = connection.execute(
                "SELECT status, COUNT(*) FROM job_applications GROUP BY status"
            ).fetchall()
        by_status = dict(rows)
        counts["Total"] = sum(by_status.values())
        counts["Applied"] = by_status.get("Applied", 0)
        counts["Interviews"] = by_status.get("Interview", 0)
        counts["Offers"] = by_status.get("Offer", 0)
        return counts

    def backup_to(self, destination: Path | str) -> Path:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.database_path)) as source:
            with closing(sqlite3.connect(destination)) as target:
                source.backup(target)
        return destination
