"""Windows toast notifications via winotify.

Falls back to a no-op on non-Windows platforms or when winotify is unavailable.
"""

import sys


def _show(title: str, msg: str) -> None:
    if sys.platform != "win32":
        return
    try:
        from winotify import Notification

        toast = Notification(
            app_id="samle-pdf",
            title=title,
            msg=msg,
            duration="short",
        )
        toast.show()
    except Exception:
        pass  # Never crash the merge process due to a notification failure


def notify_success(title: str, msg: str) -> None:
    _show(title, msg)


def notify_error(title: str, msg: str) -> None:
    _show(title, msg)


def notify_warning(title: str, msg: str) -> None:
    _show(title, msg)
