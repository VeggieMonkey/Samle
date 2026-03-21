"""Generate the output filename from a template.

Template variables:
    {name}      – stem of the main document (without .pdf)
    {date}      – today's date, ISO format (YYYY-MM-DD)
    {date_no}   – today's date, Norwegian format (DD.MM.YYYY)

If the rendered filename already exists in the output directory a counter
suffix is appended: "name (2).pdf", "name (3).pdf", etc.
"""

import datetime
from pathlib import Path


def render_output_name(template: str, main_doc: Path, output_dir: Path) -> Path:
    """Render *template* using *main_doc* and today's date.

    The output file is placed in *output_dir*. If the file already exists a
    numeric suffix is added to avoid silent overwrites.
    """
    today = datetime.date.today()
    variables = {
        "name": main_doc.stem,
        "date": today.strftime("%Y-%m-%d"),
        "date_no": today.strftime("%d.%m.%Y"),
    }
    try:
        base_name = template.format_map(variables)
    except KeyError:
        base_name = f"{main_doc.stem} med vedlegg"

    candidate = output_dir / f"{base_name}.pdf"
    if not candidate.exists():
        return candidate

    counter = 2
    while True:
        candidate = output_dir / f"{base_name} ({counter}).pdf"
        if not candidate.exists():
            return candidate
        counter += 1


def preview_output_name(template: str, example_stem: str = "Dokument") -> str:
    """Return a preview string (no filesystem check) for the settings UI."""
    today = datetime.date.today()
    variables = {
        "name": example_stem,
        "date": today.strftime("%Y-%m-%d"),
        "date_no": today.strftime("%d.%m.%Y"),
    }
    try:
        return template.format_map(variables) + ".pdf"
    except KeyError:
        return f"{example_stem} med vedlegg.pdf"
