"""Tests for the PDF merger module.

Uses minimal valid PDF bytes to avoid requiring actual PDF fixtures.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
import pytest

# Skip all tests that require pypdf if the library cannot be imported cleanly
# (e.g. broken cryptography native module in the test environment).
try:
    import pypdf  # noqa: F401
    _PYPDF_AVAILABLE = True
except BaseException:
    _PYPDF_AVAILABLE = False

requires_pypdf = pytest.mark.skipif(
    not _PYPDF_AVAILABLE, reason="pypdf not importable in this environment"
)

# Minimal 1-page PDF that pypdf can read
_MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
    b"xref\n0 4\n0000000000 65535 f \n"
    b"0000000009 00000 n \n"
    b"0000000058 00000 n \n"
    b"0000000115 00000 n \n"
    b"trailer\n<< /Size 4 /Root 1 0 R >>\n"
    b"startxref\n190\n%%EOF\n"
)


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    p = tmp_path / "sample.pdf"
    p.write_bytes(_MINIMAL_PDF)
    return p


@pytest.fixture
def sample_pdf2(tmp_path: Path) -> Path:
    p = tmp_path / "vedlegg 1.pdf"
    p.write_bytes(_MINIMAL_PDF)
    return p


class TestMergePdfs:
    @requires_pypdf
    def test_merge_two_files(self, tmp_path, sample_pdf, sample_pdf2):
        from src.combiner.merger import merge_pdfs

        output = tmp_path / "merged.pdf"
        warnings = merge_pdfs([sample_pdf, sample_pdf2], output)
        assert output.exists()
        assert warnings == []

    @requires_pypdf
    def test_output_is_valid_pdf(self, tmp_path, sample_pdf, sample_pdf2):
        from src.combiner.merger import merge_pdfs
        from pypdf import PdfReader

        output = tmp_path / "merged.pdf"
        merge_pdfs([sample_pdf, sample_pdf2], output)
        reader = PdfReader(str(output))
        assert len(reader.pages) == 2

    def test_raises_if_output_equals_input(self, tmp_path, sample_pdf):
        from src.combiner.merger import merge_pdfs

        with pytest.raises(ValueError, match="same as input"):
            merge_pdfs([sample_pdf], sample_pdf)

    @requires_pypdf
    def test_creates_output_directory(self, tmp_path, sample_pdf):
        from src.combiner.merger import merge_pdfs

        output = tmp_path / "subdir" / "merged.pdf"
        merge_pdfs([sample_pdf], output)
        assert output.exists()
