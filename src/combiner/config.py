"""Configuration management for pypdf-combiner.

Config is stored as JSON in %APPDATA%\\pypdf-combiner\\config.json on Windows.
Falls back to the user home directory on other platforms (for development).
"""

import json
import os
import sys
from pathlib import Path


def _config_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", Path.home())
    else:
        base = Path.home() / ".config"
    return Path(base) / "samle-pdf"


def _config_path() -> Path:
    return _config_dir() / "config.json"


def get_default_config() -> dict:
    return {
        "output_template": "{name} med vedlegg {date_no}",
        "notify_on_success": True,
        "open_after_merge": True,
        "language": "no",
    }


def load_config() -> dict:
    """Load config from disk, merging with defaults for missing keys."""
    defaults = get_default_config()
    path = _config_path()
    if not path.exists():
        return defaults
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge: keep defaults for any keys missing from disk
        return {**defaults, **data}
    except (json.JSONDecodeError, OSError):
        return defaults


def save_config(config: dict) -> None:
    """Save config dict to disk, creating the directory if needed."""
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
