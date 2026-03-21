"""Tests for the PDF sorter module."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
import pytest
from src.combiner.sorter import sort_pdfs, _vedlegg_number


class TestVedleggNumber:
    def test_no_vedlegg(self):
        assert _vedlegg_number(Path("Tilbud Hansen.pdf")) is None

    def test_vedlegg_with_space(self):
        assert _vedlegg_number(Path("vedlegg 1 Tegninger.pdf")) == 1

    def test_vedlegg_no_space(self):
        assert _vedlegg_number(Path("vedlegg1.pdf")) == 1

    def test_vedlegg_uppercase(self):
        assert _vedlegg_number(Path("Vedlegg 2 - Prisliste.pdf")) == 2

    def test_vedlegg_all_caps(self):
        assert _vedlegg_number(Path("VEDLEGG 12.pdf")) == 12

    def test_vedlegg_multi_digit(self):
        assert _vedlegg_number(Path("Vedlegg 10.pdf")) == 10


class TestSortPdfs:
    def _p(self, *names) -> list[Path]:
        return [Path(n) for n in names]

    def test_typical_case(self):
        paths = self._p(
            "Vedlegg 3.pdf",
            "Tilbud Hansen.pdf",
            "vedlegg 1 Tegninger.pdf",
            "Vedlegg 2 - Prisliste.pdf",
        )
        sorted_paths, main_doc = sort_pdfs(paths)
        assert main_doc == Path("Tilbud Hansen.pdf")
        assert sorted_paths[0] == Path("Tilbud Hansen.pdf")
        assert sorted_paths[1] == Path("vedlegg 1 Tegninger.pdf")
        assert sorted_paths[2] == Path("Vedlegg 2 - Prisliste.pdf")
        assert sorted_paths[3] == Path("Vedlegg 3.pdf")

    def test_single_file_no_vedlegg(self):
        paths = self._p("Dokument.pdf")
        sorted_paths, main_doc = sort_pdfs(paths)
        assert sorted_paths == [Path("Dokument.pdf")]
        assert main_doc == Path("Dokument.pdf")

    def test_all_vedlegg_uses_first_as_main(self):
        paths = self._p("Vedlegg 2.pdf", "Vedlegg 1.pdf")
        sorted_paths, main_doc = sort_pdfs(paths)
        assert sorted_paths[0] == Path("Vedlegg 1.pdf")
        assert main_doc == Path("Vedlegg 1.pdf")

    def test_empty_list(self):
        sorted_paths, main_doc = sort_pdfs([])
        assert sorted_paths == []
        assert main_doc is None

    def test_multiple_non_vedlegg_alphabetical(self):
        paths = self._p("Z file.pdf", "A file.pdf", "vedlegg 1.pdf")
        sorted_paths, main_doc = sort_pdfs(paths)
        assert main_doc == Path("A file.pdf")
        assert sorted_paths[0] == Path("A file.pdf")
        assert sorted_paths[1] == Path("vedlegg 1.pdf")
        assert sorted_paths[2] == Path("Z file.pdf")

    def test_vedlegg_sorted_numerically_not_lexically(self):
        """Vedlegg 10 should come after vedlegg 9, not before vedlegg 2."""
        paths = self._p(
            "Main.pdf",
            "vedlegg 10.pdf",
            "vedlegg 9.pdf",
            "vedlegg 2.pdf",
        )
        sorted_paths, _ = sort_pdfs(paths)
        names = [p.name for p in sorted_paths]
        assert names.index("vedlegg 2.pdf") < names.index("vedlegg 9.pdf")
        assert names.index("vedlegg 9.pdf") < names.index("vedlegg 10.pdf")
