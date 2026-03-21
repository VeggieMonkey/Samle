"""Windows registry management for context menu integration.

Writes/removes keys under:
    HKCU\\Software\\Classes\\SystemFileAssociations\\.pdf\\shell\\

This module is a no-op on non-Windows platforms.
"""

import sys
from pathlib import Path


_SHELL_BASE = r"Software\Classes\SystemFileAssociations\.pdf\shell"
_COMBINE_KEY = _SHELL_BASE + r"\CombinePDFs"
_SETTINGS_KEY = _SHELL_BASE + r"\CombinePDFsSettings"
_MULTI_INVOKE_KEY = (
    r"Software\Microsoft\Windows\CurrentVersion\Explorer"
)


def _exe_path() -> str:
    """Return the path to the running executable."""
    import os
    if getattr(sys, "frozen", False):
        # PyInstaller bundle
        return sys.executable
    # Running as a plain Python script — find main.py
    return str(Path(sys.executable))


def register(exe: str, combine_label: str, settings_label: str) -> None:
    """Write context menu registry keys.

    Args:
        exe: Full path to pypdf_combiner.exe (or the script when developing).
        combine_label: Localised label for the "combine" menu entry.
        settings_label: Localised label for the "settings" menu entry.
    """
    if sys.platform != "win32":
        print("Registry registration is only supported on Windows.")
        return

    import winreg

    def _set(key_path: str, name: str, value: str, vtype=winreg.REG_SZ) -> None:
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path) as k:
            winreg.SetValueEx(k, name, 0, vtype, value)

    icon_val = f'"{exe}",0'

    # --- Combine entry ---
    _set(_COMBINE_KEY, "", combine_label)
    _set(_COMBINE_KEY, "Icon", icon_val)
    _set(_COMBINE_KEY, "MultiSelectModel", "Player")
    _set(_COMBINE_KEY + r"\command", "", f'"{exe}" "%1"')

    # --- Settings entry ---
    _set(_SETTINGS_KEY, "", settings_label)
    _set(_SETTINGS_KEY, "Icon", icon_val)
    _set(_SETTINGS_KEY + r"\command", "", f'"{exe}" "--settings"')

    # --- Raise the multi-file selection limit to 100 ---
    _set(
        _MULTI_INVOKE_KEY,
        "MultipleInvokePromptMinimum",
        100,  # type: ignore[arg-type]
        winreg.REG_DWORD,
    )

    print(f"Context menu registered for: {exe}")


def unregister() -> None:
    """Remove context menu registry keys."""
    if sys.platform != "win32":
        print("Registry operations are only supported on Windows.")
        return

    import winreg

    def _delete_tree(root, path: str) -> None:
        try:
            # winreg.DeleteKeyEx does not recurse; delete leaf first
            with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as k:
                while True:
                    try:
                        subkey = winreg.EnumKey(k, 0)
                        _delete_tree(k, subkey)
                    except OSError:
                        break
            winreg.DeleteKey(root, path)
        except FileNotFoundError:
            pass

    _delete_tree(winreg.HKEY_CURRENT_USER, _COMBINE_KEY)
    _delete_tree(winreg.HKEY_CURRENT_USER, _SETTINGS_KEY)
    print("Context menu entries removed.")
