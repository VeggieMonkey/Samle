# Samle

Right-click any PDF file(s) in Windows Explorer and choose **"Kombiner PDF-er"** (or "Combine PDFs") to merge them into a single file. Files named `vedlegg N` are automatically sorted numerically after the main document.

## Features

- **Context menu integration** — appears when right-clicking PDF files
- **Smart ordering** — `vedlegg 1`, `vedlegg 2`, … are sorted correctly after the main document
- **Configurable output name** — uses a template like `{name} med vedlegg` (Norwegian) or `{name} with attachments` (English)
- **Windows 11 native look** — settings window follows system light/dark mode
- **Per-user install** — no administrator rights required
- **Bilingual** — Norwegian and English, switchable in settings

## Usage

1. Select one or more PDF files in Windows Explorer
2. Right-click → **Kombiner PDF-er**
3. A merged PDF appears in the same folder

To open settings: right-click any PDF → **Innstillinger for PDF-kombinering…**

## File naming

Given files:
- `Tilbud Hansen.pdf` (main document)
- `vedlegg 1 Tegninger.pdf`
- `Vedlegg 2 - Prisliste.pdf`
- `VEDLEGG 3.pdf`

Output (default template): **`Tilbud Hansen med vedlegg.pdf`**

## Settings

| Setting | Default | Description |
|---|---|---|
| Language | Norwegian | UI and context menu language |
| Output template | `{name} med vedlegg` | Variables: `{name}`, `{date}`, `{date_no}` |
| Show notification | Yes | Windows toast after merging |
| Open after merging | No | Open merged PDF in default viewer |

## Development

```bash
pip install -r requirements-dev.txt
pytest tests/
```

## Building

```bash
# EXE only (PyInstaller)
python build/build.py

# EXE + Installer (requires Inno Setup 6)
python build/build.py --full
```

## Project structure

```
src/
  combiner/
    main.py         Entry point dispatcher
    merger.py       PDF merge logic (pypdf)
    sorter.py       vedlegg ordering
    namer.py        Output filename template engine
    accumulator.py  Multi-file IPC for right-click
    config.py       JSON config in %APPDATA%
    registry.py     Windows context menu registration
    notify.py       Windows toast notifications
    i18n.py         Norwegian/English strings
  settings_ui/
    app.py          customtkinter settings window
installer/
  samle_pdf.iss       Inno Setup script
build/
  samle_pdf.spec      PyInstaller spec
  build.py            Master build script
```
