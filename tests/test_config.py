from pathlib import Path

from app.config import (
    APP_VERSION,
    get_app_data_dir,
    get_database_path,
    get_icon_path,
    get_log_path,
    get_resource_path,
)


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
    assert APP_VERSION == "1.0.1"


def test_source_resource_and_icon_assets_exist():
    assert get_resource_path("app/assets/job_tracker_icon.png").is_file()
    assert get_icon_path(platform="linux").is_file()
    assert get_icon_path(platform="win32").is_file()
    assert get_icon_path(platform="linux").suffix == ".png"
    assert get_icon_path(platform="win32").suffix == ".ico"


def test_frozen_resource_resolution(tmp_path):
    expected = tmp_path / "app/assets/job_tracker_icon.png"
    assert get_resource_path(
        "app/assets/job_tracker_icon.png", frozen_root=tmp_path
    ) == expected
    assert get_icon_path(platform="linux", frozen_root=tmp_path) == expected


def test_missing_window_icon_is_nonfatal(monkeypatch, tmp_path):
    from unittest.mock import Mock

    from app.ui.main_window import MainWindow

    monkeypatch.setattr("app.ui.main_window.get_icon_path", lambda: tmp_path / "missing.png")
    MainWindow._set_window_icon(Mock())


def test_linux_icon_is_downsampled_to_x11_safe_size():
    from app.ui.main_window import icon_subsample_factor

    factor = icon_subsample_factor(1254, 1254)
    assert factor == 5
    assert 1254 // factor <= 256
    assert icon_subsample_factor(256, 128) == 1


def test_linux_icon_lifecycle_waits_for_root_map():
    from unittest.mock import Mock

    from app.ui.main_window import MainWindow

    window = Mock()
    window._icon_map_binding = "icon-callback"
    MainWindow._set_linux_icon_after_map(window, Mock(widget=object()))
    window._set_window_icon.assert_not_called()

    MainWindow._set_linux_icon_after_map(window, Mock(widget=window))
    window.unbind.assert_called_once_with("<Map>", "icon-callback")
    window.update_idletasks.assert_called_once_with()
    window._set_window_icon.assert_called_once_with()
