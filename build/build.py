#!/usr/bin/env python3
"""Master build script.

Usage:
    python build/build.py            # PyInstaller only
    python build/build.py --full     # PyInstaller + Inno Setup installer
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SPEC = ROOT / "build" / "pypdf_combiner.spec"
DIST = ROOT / "dist"
ISS = ROOT / "installer" / "pypdf_combiner.iss"


def run(cmd: list[str], **kwargs) -> None:
    print(f">>> {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, **kwargs)


def build_exe() -> None:
    print("\n=== Building EXE with PyInstaller ===")
    run([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        str(SPEC),
        "--distpath", str(DIST),
        "--workpath", str(ROOT / "build" / "_work"),
    ])
    exe = DIST / "pypdf_combiner" / "pypdf_combiner.exe"
    if not exe.exists():
        raise RuntimeError(f"Build failed: {exe} not found")
    print(f"\nEXE built: {exe}")


def build_installer() -> None:
    print("\n=== Building installer with Inno Setup ===")
    # Try common Inno Setup install locations
    candidates = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
    ]
    iscc = next((c for c in candidates if c.exists()), None)
    if iscc is None:
        print("ISCC.exe not found. Install Inno Setup 6 and add it to PATH.")
        sys.exit(1)

    (ROOT / "dist" / "installer").mkdir(parents=True, exist_ok=True)
    run([str(iscc), str(ISS)])
    print(f"\nInstaller built: {ROOT / 'dist' / 'installer' / 'pypdf-combiner-setup.exe'}")


def main() -> None:
    os.chdir(ROOT)
    build_exe()
    if "--full" in sys.argv:
        build_installer()
    print("\nDone.")


if __name__ == "__main__":
    main()
