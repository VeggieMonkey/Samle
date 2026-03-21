"""Tests for the output filename template engine."""

import sys
import os
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
from unittest.mock import patch
import pytest
from src.combiner.namer import render_output_name, preview_output_name


_FIXED_DATE = datetime.date(2025, 3, 21)


class TestPreviewOutputName:
    def test_default_template_norwegian(self):
        result = preview_output_name("{name} med vedlegg", "Tilbud Hansen")
        assert result == "Tilbud Hansen med vedlegg.pdf"

    def test_default_template_english(self):
        result = preview_output_name("{name} with attachments", "Document")
        assert result == "Document with attachments.pdf"

    def test_date_variable(self):
        with patch("src.combiner.namer.datetime.date") as mock_date:
            mock_date.today.return_value = _FIXED_DATE
            mock_date.side_effect = lambda *a, **kw: datetime.date(*a, **kw)
            result = preview_output_name("{name} {date}", "Doc")
        assert result == "Doc 2025-03-21.pdf"

    def test_date_no_variable(self):
        with patch("src.combiner.namer.datetime.date") as mock_date:
            mock_date.today.return_value = _FIXED_DATE
            mock_date.side_effect = lambda *a, **kw: datetime.date(*a, **kw)
            result = preview_output_name("{name} {date_no}", "Doc")
        assert result == "Doc 21.03.2025.pdf"

    def test_unknown_variable_fallback(self):
        result = preview_output_name("{name} {unknown_var}", "Doc")
        assert result == "Doc med vedlegg.pdf"

    def test_default_example_stem(self):
        result = preview_output_name("{name} med vedlegg")
        assert result.startswith("Dokument")


class TestRenderOutputName:
    def _tmp(self, tmp_path: Path, name: str) -> Path:
        return tmp_path / name

    def test_no_conflict(self, tmp_path):
        main_doc = tmp_path / "Tilbud.pdf"
        result = render_output_name("{name} med vedlegg", main_doc, tmp_path)
        assert result == tmp_path / "Tilbud med vedlegg.pdf"
        assert not result.exists()

    def test_conflict_adds_counter(self, tmp_path):
        main_doc = tmp_path / "Tilbud.pdf"
        # Create the file that would be the default output
        (tmp_path / "Tilbud med vedlegg.pdf").touch()
        result = render_output_name("{name} med vedlegg", main_doc, tmp_path)
        assert result == tmp_path / "Tilbud med vedlegg (2).pdf"

    def test_multiple_conflicts(self, tmp_path):
        main_doc = tmp_path / "Tilbud.pdf"
        (tmp_path / "Tilbud med vedlegg.pdf").touch()
        (tmp_path / "Tilbud med vedlegg (2).pdf").touch()
        result = render_output_name("{name} med vedlegg", main_doc, tmp_path)
        assert result == tmp_path / "Tilbud med vedlegg (3).pdf"
