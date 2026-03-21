# pypdf-combiner Implementation Plan

## Summary

A Windows desktop tool that adds a right-click context menu entry for PDF files, letting users select multiple PDFs and merge them in the correct order. Files named "vedlegg N" (Norwegian for attachment N) are sorted numerically after the main document. A settings dialog lets users configure the output filename template and language.

---

## Technology Decisions

| Concern | Choice | Reason |
|---|---|---|
| PDF merging | `pypdf >= 4.0` | PyPDF2 is unmaintained; pypdf is the successor |
| Settings UI | `customtkinter` | Follows Windows 11 light/dark mode; bundles cleanly with PyInstaller; best practice for Python desktop apps |
| Context menu | `winreg` (stdlib) | 20 lines, no extra dependency, full control |
| Notifications | `winotify` | Pure-Python Windows 10/11 toast notifications |
| Multi-file IPC | Temp-file accumulator + `psutil` | No named pipes; reliable for same-machine right-click |
| Installer | PyInstaller + Inno Setup | Per-user install (no admin); clean uninstall |
| Settings storage | JSON in `%APPDATA%` | No admin rights; roaming-profile friendly |

**Settings UI note:** True integration into the Windows Settings app requires MSIX/UWP packaging with a signed certificate—not practical for a Python app. A `customtkinter` window is the correct best practice, and it automatically follows the system theme.

---

## Project File Structure

```
/home/user/Pypdf-combiner/
├── src/
│   ├── combiner/
│   │   ├── __init__.py
│   │   ├── main.py           # Entry point dispatcher
│   │   ├── merger.py         # pypdf merge logic
│   │   ├── sorter.py         # vedlegg number extraction + sort
│   │   ├── namer.py          # Output filename template engine
│   │   ├── accumulator.py    # Multi-file IPC via temp files
│   │   └── config.py         # JSON config read/write
│   └── settings_ui/
│       ├── __init__.py
│       └── app.py            # customtkinter settings window
├── installer/
│   └── pypdf_combiner.iss    # Inno Setup script
├── build/
│   └── pypdf_combiner.spec   # PyInstaller spec
├── tests/
│   ├── test_sorter.py
│   ├── test_namer.py
│   └── test_merger.py
├── assets/
│   └── icon.ico
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## Implementation Steps

### Phase 1 — Core Logic

**1.1 `sorter.py`**
- Regex: `r'vedlegg\s*(\d+)'` with `re.IGNORECASE`
- Sort key: `(has_vedlegg: bool, number: int, filename: str)`
- Files without vedlegg = main document (position 0); multiple non-vedlegg files → alphabetical, first used as base name

**1.2 `namer.py`**
- Template variables: `{name}`, `{date}` (ISO), `{date_no}` (DD.MM.YYYY)
- Default template: `{name} med vedlegg` (Norwegian) or `{name} with attachments` (English) per locale setting
- Uses `str.format_map()` — no Jinja2 dependency needed
- Output goes to same directory as inputs; appends counter if file exists: `{name} med vedlegg (2).pdf`

**1.3 `merger.py`**
- Uses `pypdf.PdfWriter.append()` for each file in sorted order
- Skips encrypted PDFs with a warning toast
- Checks output path != any input path

**1.4 `config.py`**
- Location: `%APPDATA%\pypdf-combiner\config.json`
- Schema:
  ```json
  {
    "output_template": "{name} med vedlegg",
    "notify_on_success": true,
    "open_after_merge": false,
    "language": "no"
  }
  ```
- Exposes `load_config()`, `save_config()`, `get_default_config()`

**1.5 `accumulator.py`**
- Session ID = `<explorer_parent_pid>_<timestamp_rounded_to_2s>` (via `psutil`)
- First invocation = "leader": waits 500ms for others to write paths, then merges all
- Subsequent invocations write their path and exit immediately
- Leader cleans up temp dir after merge

### Phase 2 — Windows Integration

**2.1 `main.py` — Entry point**
```
sys.argv contains "--settings"  → launch settings UI
sys.argv contains "--register-menu"  → write registry keys
sys.argv contains "--unregister-menu"  → remove registry keys
sys.argv contains a file path  → accumulator → merge
no args  → launch settings UI
```

**2.2 Registry keys (written by `--register-menu`)**

Under `HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\`:

```
CombinePDFs\
  (Default)        = "Kombiner PDF-er" / "Combine PDFs"  (locale-aware)
  Icon             = "<install_dir>\pypdf_combiner.exe,0"
  MultiSelectModel = "Player"
  command\
    (Default)      = '"<install_dir>\pypdf_combiner.exe" "%1"'

CombinePDFsSettings\
  (Default)        = "Innstillinger for PDF-kombinering..." / "PDF Combiner Settings..."
  Icon             = "<install_dir>\pypdf_combiner.exe,0"
  command\
    (Default)      = '"<install_dir>\pypdf_combiner.exe" "--settings"'
```

Also sets `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\MultipleInvokePromptMinimum = 100` to support selecting more than 15 files.

**2.3 Notifications** via `winotify` — shown after successful merge or on error.

### Phase 3 — Settings UI

**3.1 `settings_ui/app.py`** — `customtkinter.CTk()` window, 480×380, non-resizable

Layout:
```
[ pypdf-combiner Settings ]
────────────────────────────────────
Language: [ Norwegian ▼ ] [ English ▼ ]

Output filename template:
[ {name} med vedlegg                ]

Available: {name}, {date}, {date_no}

Preview:
  Tilbud.pdf → Tilbud med vedlegg.pdf  (live, updates as you type)

○ Show notification after merging
○ Open file after merging

              [ Save ]  [ Cancel ]
────────────────────────────────────
pypdf-combiner v1.0.0
```

- `set_appearance_mode("System")` — follows Windows light/dark mode automatically
- Language switch immediately updates all UI labels and the default template hint
- Changing language updates `config["language"]` and re-registers context menu with translated label

### Phase 4 — Build & Installer

**4.1 PyInstaller** — `--onedir --noconsole --icon=assets/icon.ico`

**4.2 Inno Setup** — key settings:
- `PrivilegesRequired=lowest` (per-user install, no admin UAC)
- Install dir: `{localappdata}\pypdf-combiner`
- `[Run]`: calls `pypdf_combiner.exe --register-menu` after install
- `[UninstallRun]`: calls `pypdf_combiner.exe --unregister-menu` before uninstall

---

## Internationalization

| Key | Norwegian (default) | English |
|---|---|---|
| Context menu label | Kombiner PDF-er | Combine PDFs |
| Settings menu label | Innstillinger... | Settings... |
| Default template | {name} med vedlegg | {name} with attachments |
| Success toast title | PDF kombinert | PDF combined |
| Settings window title | Innstillinger | Settings |

Language stored in config.json as `"no"` or `"en"`. A simple dict-based i18n module (no gettext needed at this scale).

---

## Sort + Naming Example

Input files (user selects all):
- `Tilbud Hansen.pdf` → no vedlegg → main document
- `vedlegg 1 Tegninger.pdf` → vedlegg 1
- `Vedlegg 2 - Prisliste.pdf` → vedlegg 2
- `Vedlegg 3.pdf` → vedlegg 3

Merge order: `Tilbud Hansen.pdf`, `vedlegg 1 Tegninger.pdf`, `Vedlegg 2 - Prisliste.pdf`, `Vedlegg 3.pdf`

Output: `Tilbud Hansen med vedlegg.pdf` (same folder)

---

## Dependencies

**requirements.txt**
```
pypdf>=4.0.0
customtkinter>=5.2.0
winotify>=1.1.0
psutil>=5.9.0
```

**requirements-dev.txt**
```
pyinstaller>=6.0.0
pytest>=7.0.0
pytest-mock>=3.0.0
```
