"""Application configuration and cross-platform data paths."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "JobTracker"
DISPLAY_NAME = "Job Tracker"
APP_VERSION = "1.0.2"
DATABASE_FILENAME = "job_tracker.db"
LOG_FILENAME = "job_tracker.log"


def get_app_data_dir(
    *, platform: str | None = None, environ: dict[str, str] | None = None
) -> Path:
    """Return the per-user application data directory for this platform.

    ``platform`` and ``environ`` are injectable so path behaviour can be tested
    without changing the current machine or the user's real data directory.
    """
    platform = platform or sys.platform
    environ = os.environ if environ is None else environ

    if platform == "win32":
        local_app_data = environ.get("LOCALAPPDATA")
        if local_app_data:
            base_dir = Path(local_app_data)
        else:
            user_profile = environ.get("USERPROFILE")
            if not user_profile:
                raise RuntimeError("LOCALAPPDATA and USERPROFILE are not set")
            base_dir = Path(user_profile) / "AppData" / "Local"
    else:
        base_dir = Path(environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    return base_dir / APP_NAME


def get_database_path(**kwargs: object) -> Path:
    """Return the path to the application's SQLite database."""
    return get_app_data_dir(**kwargs) / DATABASE_FILENAME


def get_log_path(**kwargs: object) -> Path:
    """Return the local diagnostic log path."""
    return get_app_data_dir(**kwargs) / LOG_FILENAME


def get_resource_path(relative_path: str | Path, *, frozen_root: Path | None = None) -> Path:
    """Resolve a bundled resource when frozen, or a source-tree resource otherwise."""
    bundle_root = frozen_root or getattr(sys, "_MEIPASS", None)
    base = Path(bundle_root) if bundle_root else Path(__file__).resolve().parent.parent
    return base / relative_path


def get_icon_path(*, platform: str | None = None, frozen_root: Path | None = None) -> Path:
    """Return the preferred application-window icon for the current platform."""
    suffix = ".ico" if (platform or sys.platform) == "win32" else ".png"
    return get_resource_path(f"app/assets/job_tracker_icon{suffix}", frozen_root=frozen_root)
