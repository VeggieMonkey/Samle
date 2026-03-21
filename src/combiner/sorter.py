"""Sort PDF file paths for merging.

Ordering rules:
1. The "main document" (no vedlegg number) comes first.
2. Files with vedlegg N are sorted numerically after it.
3. Any additional files without a vedlegg number are sorted alphabetically
   and appended at the end.

Examples of recognised vedlegg patterns (case-insensitive):
    vedlegg 1, Vedlegg1, VEDLEGG 12, vedlegg 2 - Prisliste
"""

import re
from pathlib import Path

_VEDLEGG_RE = re.compile(r"vedlegg\s*(\d+)", re.IGNORECASE)


def _vedlegg_number(path: Path) -> int | None:
    """Return the vedlegg number from a filename, or None if absent."""
    match = _VEDLEGG_RE.search(path.name)
    return int(match.group(1)) if match else None


def sort_pdfs(paths: list[Path]) -> tuple[list[Path], Path | None]:
    """Sort *paths* for merging.

    Returns:
        (sorted_paths, main_document)

    *main_document* is the path identified as the main file (no vedlegg number).
    If multiple files have no vedlegg number the alphabetically first is used as
    the main document; the rest are appended alphabetically at the end.
    If all files have a vedlegg number the first in numeric order is used as the
    main document (and is still position 0 in the sorted list).
    """
    with_vedlegg = sorted(
        [p for p in paths if _vedlegg_number(p) is not None],
        key=lambda p: (_vedlegg_number(p), p.name),
    )
    without_vedlegg = sorted(
        [p for p in paths if _vedlegg_number(p) is None],
        key=lambda p: p.name,
    )

    if without_vedlegg:
        main_doc = without_vedlegg[0]
        extras = without_vedlegg[1:]
        sorted_paths = [main_doc] + with_vedlegg + extras
    elif with_vedlegg:
        # No clear main document — use numerically first vedlegg file
        main_doc = with_vedlegg[0]
        sorted_paths = with_vedlegg
    else:
        return [], None

    return sorted_paths, main_doc
