"""Merge a list of PDF files into a single output PDF using pypdf."""

from pathlib import Path


def merge_pdfs(ordered_paths: list[Path], output_path: Path) -> list[str]:
    """Merge *ordered_paths* into *output_path*.

    Returns a list of warning strings for any files that were skipped
    (e.g. encrypted PDFs).

    Raises:
        ValueError  – if output_path is the same as one of the inputs.
        RuntimeError – if pypdf is not installed or the write fails.
    """
    resolved_output = output_path.resolve()
    for p in ordered_paths:
        if p.resolve() == resolved_output:
            raise ValueError(
                f"Output path '{output_path}' is the same as input '{p}'. "
                "Cannot merge a file into itself."
            )

    from pypdf import PdfWriter
    from pypdf.errors import PdfReadError

    writer = PdfWriter()
    warnings: list[str] = []

    for p in ordered_paths:
        try:
            writer.append(str(p))
        except PdfReadError as exc:
            if "encrypt" in str(exc).lower():
                warnings.append(str(p))
            else:
                raise

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)
    writer.close()

    return warnings
