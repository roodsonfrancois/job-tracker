from pathlib import Path

from app.config import APP_VERSION, get_app_data_dir


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INSTALLER_DEFINITION = PROJECT_ROOT / "packaging" / "windows" / "JobTracker.iss"
WINDOWS_WORKFLOW = PROJECT_ROOT / ".github" / "workflows" / "build-windows.yml"


def test_windows_installer_definition_uses_expected_files_and_per_user_mode():
    content = INSTALLER_DEFINITION.read_text(encoding="utf-8")
    assert '#define MyAppExeName "JobTracker.exe"' in content
    assert "app\\assets\\job_tracker_icon.ico" in content
    assert "DefaultDirName={localappdata}\\Programs\\JobTracker" in content
    assert "PrivilegesRequired=lowest" in content
    assert "desktopicon" in content
    assert "[UninstallDelete]" not in content
    assert "job_tracker.db" not in content


def test_installer_version_comes_from_central_application_version():
    installer = INSTALLER_DEFINITION.read_text(encoding="utf-8")
    workflow = WINDOWS_WORKFLOW.read_text(encoding="utf-8")
    assert APP_VERSION == "1.0.2"
    assert "AppVersion={#MyAppVersion}" in installer
    assert "OutputBaseFilename=JobTracker-v{#MyAppVersion}-Windows-Setup" in installer
    assert "from app.config import APP_VERSION" in workflow
    assert '"/DMyAppVersion=$env:APP_VERSION"' in workflow


def test_windows_workflow_retains_standalone_and_builds_installer():
    workflow = WINDOWS_WORKFLOW.read_text(encoding="utf-8")
    assert "python -m PyInstaller --clean --noconfirm JobTracker.spec" in workflow
    assert "packaging\\windows\\JobTracker.iss" in workflow
    assert "dist/JobTracker.exe" in workflow
    assert "dist/JobTracker-v*-Windows-Setup.exe" in workflow


def test_windows_application_data_path_remains_local_app_data(tmp_path):
    result = get_app_data_dir(
        platform="win32", environ={"LOCALAPPDATA": str(tmp_path)}
    )
    assert result == tmp_path / "JobTracker"
