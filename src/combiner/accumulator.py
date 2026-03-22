"""Multi-file IPC accumulator.

When Windows invokes the context menu command once per selected file
(MultiSelectModel=Player), each invocation calls this module.  The first
invocation becomes the "leader": it waits a short window for the other
invocations to write their paths, then returns all collected paths.
Subsequent invocations write their path and return an empty list immediately.

Session identity is derived from the Explorer parent-process PID combined
with a 2-second timestamp bucket so that two separate right-click actions
within the same Explorer session are still treated as distinct sessions.
"""

import os
import sys
import tempfile
import time
from pathlib import Path

_WAIT_SECONDS = 0.5  # How long the leader waits for peers
_BUCKET_SECONDS = 2   # Timestamp rounding for session ID


def _session_dir() -> Path:
    """Return the temp directory for the current right-click session."""
    try:
        import psutil
        explorer_pid = psutil.Process(os.getpid()).parent().pid
    except Exception:
        explorer_pid = os.getppid()

    bucket = int(time.time() / _BUCKET_SECONDS)
    session_id = f"{explorer_pid}_{bucket}"
    base = Path(tempfile.gettempdir()) / "samle-pdf" / session_id
    base.mkdir(parents=True, exist_ok=True)
    return base


def collect_or_register(file_path: str) -> list[Path]:
    """Register *file_path* for this session and return the full list if leader.

    If this invocation is the leader it blocks for _WAIT_SECONDS, then reads
    and returns every registered path.  Otherwise returns [].
    """
    session_dir = _session_dir()
    lock_file = session_dir / ".leader"

    # Write our path using PID as filename to avoid collisions
    pid = os.getpid()
    (session_dir / f"{pid}.txt").write_text(file_path, encoding="utf-8")

    # Try to become the leader (atomic: only one process creates the lock)
    try:
        fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
    except FileExistsError:
        # Another invocation is already the leader; we are done
        return []

    # We are the leader — wait for peers
    time.sleep(_WAIT_SECONDS)

    paths: list[Path] = []
    for txt in session_dir.glob("*.txt"):
        try:
            paths.append(Path(txt.read_text(encoding="utf-8").strip()))
        except OSError:
            pass

    # Clean up session directory
    try:
        import shutil
        shutil.rmtree(session_dir, ignore_errors=True)
    except Exception:
        pass

    return paths
