# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for samle-pdf
# Build:  pyinstaller build/samle_pdf.spec --distpath dist --workpath build/_work

import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent   # repo root

block_cipher = None

a = Analysis(
    [str(ROOT / "src" / "combiner" / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "assets" / "icon.ico"), "."),
    ],
    hiddenimports=[
        # pypdf lazy-imports its crypto providers
        "pypdf",
        "pypdf._crypt_providers",
        "pypdf._crypt_providers._fallback",
        "pypdf._crypt_providers._cryptography",
        # customtkinter loads themes at runtime
        "customtkinter",
        "customtkinter.windows",
        "customtkinter.windows.widgets",
        "customtkinter.windows.widgets.theme",
        # winotify and runtime deps
        "winotify",
        "psutil",
        "psutil._pswindows",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter.test", "unittest", "pydoc", "doctest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="samle_pdf",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,              # Silent — no console window from Explorer
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "assets" / "icon.ico"),
    version=str(ROOT / "build" / "version_info.py"),
    uac_admin=False,            # Explicitly no UAC elevation
    uac_uiaccess=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=["vcruntime*.dll", "msvcp*.dll"],
    name="samle_pdf",
)
