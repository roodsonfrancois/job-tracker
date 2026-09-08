from pathlib import Path

from app.config import APP_VERSION, get_app_data_dir, get_database_path, get_log_path


def test_linux_default_data_path(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert get_app_data_dir(platform="linux", environ={}) == tmp_path / ".local/share/JobTracker"


def test_linux_honors_xdg_data_home(tmp_path):
    assert get_app_data_dir(
        platform="linux", environ={"XDG_DATA_HOME": str(tmp_path)}
    ) == tmp_path / "JobTracker"


def test_windows_uses_local_app_data(tmp_path):
    assert get_app_data_dir(
        platform="win32", environ={"LOCALAPPDATA": str(tmp_path)}
    ) == tmp_path / "JobTracker"


def test_database_filename(tmp_path):
    assert get_database_path(
        platform="win32", environ={"LOCALAPPDATA": str(tmp_path)}
    ) == tmp_path / "JobTracker/job_tracker.db"


def test_log_path_and_version(tmp_path):
    assert get_log_path(
        platform="win32", environ={"LOCALAPPDATA": str(tmp_path)}
    ) == tmp_path / "JobTracker/job_tracker.log"
    assert APP_VERSION == "1.0.0"
