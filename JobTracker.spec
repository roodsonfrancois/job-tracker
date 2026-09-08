# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("customtkinter") + collect_data_files("tkcalendar") + [
    ("app/assets/job_tracker_icon.png", "app/assets"),
    ("app/assets/job_tracker_icon.ico", "app/assets"),
]

analysis = Analysis(
    ["app/main.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="JobTracker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="app/assets/job_tracker_icon.ico",
)
