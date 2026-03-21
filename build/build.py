"""Master build script for pypdf-combiner.

Usage
-----
  python build/build.py                # EXE only (PyInstaller)
  python build/build.py --full         # EXE + installer (requires Inno Setup 6)
  python build/build.py --clean        # Remove previous build artefacts, then build
  python build/build.py --full --clean # Clean, build EXE, build installer

Environment
-----------
  ISCC_PATH  – override path to ISCC.exe if not in one of the default locations
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT  = Path(__file__).parent.parent
SPEC  = ROOT / "build" / "pypdf_combiner.spec"
DIST  = ROOT / "dist"
WORK  = ROOT / "build" / "_work"
ISS   = ROOT / "installer" / "pypdf_combiner.iss"

ISCC_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
    Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
]

# ── Terminal colour helpers ────────────────────────────────────────────────

def _c(code: str, text: str) -> str:
    """Wrap text in ANSI colour if stdout is a tty."""
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"

ok    = lambda t: print(_c("92", f"  ✓  {t}"))
info  = lambda t: print(_c("94", f"  ·  {t}"))
warn  = lambda t: print(_c("93", f"  !  {t}"))
err   = lambda t: print(_c("91", f"  ✗  {t}"), file=sys.stderr)
head  = lambda t: print(_c("1;97", f"\n{'═' * 54}\n  {t}\n{'═' * 54}"))


# ── Helpers ────────────────────────────────────────────────────────────────

def _run(cmd: list[str | Path], **kwargs) -> None:
    info(" ".join(str(c) for c in cmd))
    t0 = time.monotonic()
    result = subprocess.run(cmd, **kwargs)
    elapsed = time.monotonic() - t0
    if result.returncode != 0:
        err(f"Command failed (exit {result.returncode})")
        sys.exit(result.returncode)
    ok(f"Done in {elapsed:.1f}s")


def _find_iscc() -> Path | None:
    # 1. Env override
    env = os.environ.get("ISCC_PATH")
    if env and Path(env).exists():
        return Path(env)
    # 2. Well-known install paths
    for c in ISCC_CANDIDATES:
        if c.exists():
            return c
    # 3. PATH
    found = shutil.which("ISCC")
    return Path(found) if found else None


# ── Steps ──────────────────────────────────────────────────────────────────

def step_clean() -> None:
    head("Clean")
    for d in [DIST / "pypdf_combiner", DIST / "installer", WORK]:
        if d.exists():
            shutil.rmtree(d)
            ok(f"Removed {d.relative_to(ROOT)}")
    ok("Clean complete")


def step_assets() -> None:
    head("Generate assets")
    _run([sys.executable, str(ROOT / "build" / "generate_assets.py")])


def step_pyinstaller() -> None:
    head("Build EXE  (PyInstaller)")
    _run([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(SPEC),
        "--distpath", str(DIST),
        "--workpath", str(WORK),
    ])

    exe = DIST / "pypdf_combiner" / "pypdf_combiner.exe"
    if not exe.exists():
        err(f"Expected EXE not found: {exe}")
        sys.exit(1)

    size_mb = exe.stat().st_size / 1_048_576
    ok(f"EXE built: {exe.relative_to(ROOT)}  ({size_mb:.1f} MB)")


def step_inno() -> None:
    head("Build installer  (Inno Setup)")
    iscc = _find_iscc()
    if iscc is None:
        err(
            "ISCC.exe not found.\n"
            "  Install Inno Setup 6 from https://jrsoftware.org/isinfo.php\n"
            "  or set ISCC_PATH=/path/to/ISCC.exe"
        )
        sys.exit(1)

    out_dir = DIST / "installer"
    out_dir.mkdir(parents=True, exist_ok=True)

    _run([str(iscc), str(ISS)])

    setup_exe = next(out_dir.glob("*.exe"), None)
    if setup_exe:
        size_mb = setup_exe.stat().st_size / 1_048_576
        ok(f"Installer: {setup_exe.relative_to(ROOT)}  ({size_mb:.1f} MB)")
    else:
        warn("Installer EXE not found in dist/installer/ — check Inno Setup output.")


# ── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]
    clean = "--clean" in args
    full  = "--full"  in args

    os.chdir(ROOT)

    if clean:
        step_clean()

    # Re-generate assets if icon is missing
    if not (ROOT / "assets" / "icon.ico").exists():
        step_assets()

    step_pyinstaller()

    if full:
        step_inno()

    head("Build complete")
    exe = DIST / "pypdf_combiner" / "pypdf_combiner.exe"
    ok(f"EXE → {exe.relative_to(ROOT)}")
    if full:
        setup_exe = next((DIST / "installer").glob("*.exe"), None)
        if setup_exe:
            ok(f"Installer → {setup_exe.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
