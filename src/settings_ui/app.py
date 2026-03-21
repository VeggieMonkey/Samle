"""Settings window for pypdf-combiner.

Built with customtkinter — follows the Windows 11 system light/dark theme
automatically and uses Fluent-style rounded controls.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import customtkinter as ctk
except ImportError:
    raise ImportError(
        "customtkinter is required. Install it with: pip install customtkinter"
    )

if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.combiner.config import load_config, save_config
from src.combiner.i18n import LANGUAGE_LABELS, get
from src.combiner.namer import preview_output_name

APP_VERSION = "1.0.0"
WINDOW_W    = 540
WINDOW_H    = 480

# Brand colours (match the icon/installer palette)
_BLUE       = "#2D6EDC"
_BLUE_HOVER = "#1E50A2"
_BLUE_DARK  = "#1E50A2"


def _icon_path() -> str | None:
    """Return path to icon.ico if it can be found."""
    candidates = [
        Path(__file__).parent.parent.parent / "assets" / "icon.ico",
        Path(sys.executable).parent / "icon.ico",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


class SettingsApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self._config = load_config()
        self._lang   = self._config.get("language", "no")

        self.title(get("settings_title", self._lang))
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.resizable(False, False)
        self.minsize(WINDOW_W, WINDOW_H)

        icon = _icon_path()
        if icon and sys.platform == "win32":
            try:
                self.iconbitmap(icon)
            except Exception:
                pass

        self._build_ui()
        self._refresh_labels()
        self._update_preview()

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_body()
        self._build_footer()

    def _build_header(self) -> None:
        """Blue gradient header bar with app name and icon."""
        header = ctk.CTkFrame(self, fg_color=_BLUE, corner_radius=0, height=72)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        # Try to show a small PNG icon in the header
        self._header_icon_label = None
        try:
            from PIL import Image as PILImage
            icon_file = _icon_path()
            if icon_file and icon_file.endswith(".ico"):
                pil_img = PILImage.open(icon_file)
                # Find the 48px frame
                for frame_idx in range(100):
                    try:
                        pil_img.seek(frame_idx)
                        if pil_img.size[0] >= 48:
                            break
                    except EOFError:
                        break
                pil_img = pil_img.resize((40, 40), PILImage.LANCZOS).convert("RGBA")
                ctk_img = ctk.CTkImage(pil_img, size=(40, 40))
                self._header_icon_label = ctk.CTkLabel(
                    header, image=ctk_img, text="", fg_color="transparent"
                )
                self._header_icon_label.grid(row=0, column=0, padx=(18, 0), pady=16, sticky="w")
        except Exception:
            pass

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w",
                         padx=(66 if self._header_icon_label else 20, 20), pady=0)

        self._header_title = ctk.CTkLabel(
            title_frame,
            text="pypdf-combiner",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white",
            fg_color="transparent",
        )
        self._header_title.pack(anchor="w")

        self._header_sub = ctk.CTkLabel(
            title_frame,
            text="",          # filled by _refresh_labels
            font=ctk.CTkFont(size=12),
            text_color="#C8D8F8",
            fg_color="transparent",
        )
        self._header_sub.pack(anchor="w")

    def _build_body(self) -> None:
        """Scrollable body with all settings controls."""
        body = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        body.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        body.grid_columnconfigure(0, weight=1)
        self._body = body

        row = 0

        # ── Language ──────────────────────────────────────────────────────
        row = self._section_label(body, row, "settings_language")

        lang_row = ctk.CTkFrame(body, fg_color="transparent")
        lang_row.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 12))
        lang_row.grid_columnconfigure(0, weight=1)
        row += 1

        self._lang_var = ctk.StringVar(value=LANGUAGE_LABELS[self._lang])
        self._lang_seg = ctk.CTkSegmentedButton(
            lang_row,
            values=list(LANGUAGE_LABELS.values()),
            variable=self._lang_var,
            command=self._on_language_change,
            font=ctk.CTkFont(size=13),
            height=34,
        )
        self._lang_seg.grid(row=0, column=0, sticky="w")

        # ── Separator ─────────────────────────────────────────────────────
        ctk.CTkFrame(body, height=1, fg_color=("gray85", "gray25")).grid(
            row=row, column=0, sticky="ew", padx=24, pady=4
        )
        row += 1

        # ── Output template ───────────────────────────────────────────────
        row = self._section_label(body, row, "settings_template_label")

        self._template_var = ctk.StringVar(
            value=self._config.get(
                "output_template", get("default_template", self._lang)
            )
        )
        self._template_entry = ctk.CTkEntry(
            body,
            textvariable=self._template_var,
            height=38,
            font=ctk.CTkFont(size=14),
            border_width=1,
        )
        self._template_entry.grid(
            row=row, column=0, sticky="ew", padx=24, pady=(0, 4)
        )
        self._template_var.trace_add("write", lambda *_: self._update_preview())
        row += 1

        self._hint_label = ctk.CTkLabel(
            body,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
            anchor="w",
        )
        self._hint_label.grid(row=row, column=0, sticky="ew", padx=26, pady=(0, 8))
        row += 1

        # ── Preview card ──────────────────────────────────────────────────
        preview_card = ctk.CTkFrame(
            body,
            fg_color=("gray95", "gray17"),
            corner_radius=8,
            border_width=1,
            border_color=("gray80", "gray30"),
        )
        preview_card.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 14))
        preview_card.grid_columnconfigure(0, weight=1)
        row += 1

        self._preview_heading = ctk.CTkLabel(
            preview_card,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray45", "gray55"),
            anchor="w",
        )
        self._preview_heading.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 2))

        self._preview_value = ctk.CTkLabel(
            preview_card,
            text="",
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color=(_BLUE_DARK, "#7EB3FF"),
            anchor="w",
            wraplength=WINDOW_W - 80,
        )
        self._preview_value.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))

        # ── Separator ─────────────────────────────────────────────────────
        ctk.CTkFrame(body, height=1, fg_color=("gray85", "gray25")).grid(
            row=row, column=0, sticky="ew", padx=24, pady=4
        )
        row += 1

        # ── Behaviour toggles ─────────────────────────────────────────────
        row = self._section_label(body, row, "settings_behaviour")

        self._notify_var = ctk.BooleanVar(
            value=self._config.get("notify_on_success", True)
        )
        self._notify_switch = ctk.CTkSwitch(
            body,
            text="",
            variable=self._notify_var,
            onvalue=True,
            offvalue=False,
            font=ctk.CTkFont(size=13),
            button_color=_BLUE,
            button_hover_color=_BLUE_HOVER,
            progress_color=_BLUE,
        )
        self._notify_switch.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 6))
        row += 1

        self._open_var = ctk.BooleanVar(
            value=self._config.get("open_after_merge", False)
        )
        self._open_switch = ctk.CTkSwitch(
            body,
            text="",
            variable=self._open_var,
            onvalue=True,
            offvalue=False,
            font=ctk.CTkFont(size=13),
            button_color=_BLUE,
            button_hover_color=_BLUE_HOVER,
            progress_color=_BLUE,
        )
        self._open_switch.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 16))
        row += 1

    def _build_footer(self) -> None:
        """Footer bar with version info and Save/Cancel buttons."""
        footer = ctk.CTkFrame(
            self,
            fg_color=("gray92", "gray18"),
            corner_radius=0,
            height=56,
        )
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)
        footer.grid_columnconfigure(0, weight=1)

        self._version_label = ctk.CTkLabel(
            footer,
            text=f"pypdf-combiner  v{APP_VERSION}",
            font=ctk.CTkFont(size=11),
            text_color=("gray55", "gray55"),
            anchor="w",
        )
        self._version_label.grid(row=0, column=0, padx=20, pady=16, sticky="w")

        btn_frame = ctk.CTkFrame(footer, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=16, pady=10)

        self._cancel_btn = ctk.CTkButton(
            btn_frame,
            text="",
            command=self.destroy,
            width=100,
            height=34,
            fg_color=("gray80", "gray30"),
            hover_color=("gray70", "gray40"),
            text_color=("gray20", "gray90"),
            font=ctk.CTkFont(size=13),
            corner_radius=6,
        )
        self._cancel_btn.pack(side="left", padx=(0, 8))

        self._save_btn = ctk.CTkButton(
            btn_frame,
            text="",
            command=self._on_save,
            width=110,
            height=34,
            fg_color=_BLUE,
            hover_color=_BLUE_HOVER,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=6,
        )
        self._save_btn.pack(side="left")

    # ── Helpers ────────────────────────────────────────────────────────────

    def _section_label(self, parent, row: int, key: str) -> int:
        """Insert a small section heading and return the next row index."""
        lbl = ctk.CTkLabel(
            parent,
            text="",          # filled by _refresh_labels
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray50", "gray55"),
            anchor="w",
        )
        lbl.grid(row=row, column=0, sticky="ew", padx=26, pady=(14, 4))
        # Store reference so _refresh_labels can update it
        attr = f"_section_{key}"
        setattr(self, attr, lbl)
        return row + 1

    def _refresh_labels(self) -> None:
        lang = self._lang
        self.title(get("settings_title", lang))
        self._header_sub.configure(text=get("settings_subtitle", lang))

        # Section headings
        self._section_settings_language.configure(
            text=get("settings_language", lang).upper()
        )
        self._section_settings_template_label.configure(
            text=get("settings_template_label", lang).upper()
        )
        self._section_settings_behaviour.configure(
            text=get("settings_behaviour", lang).upper()
        )

        self._hint_label.configure(text=get("settings_template_hint", lang))
        self._preview_heading.configure(text=get("settings_preview_label", lang))
        self._notify_switch.configure(text=get("settings_notify", lang))
        self._open_switch.configure(text=get("settings_open", lang))
        self._save_btn.configure(text=get("settings_save", lang))
        self._cancel_btn.configure(text=get("settings_cancel", lang))
        self._update_preview()

    def _update_preview(self) -> None:
        template = self._template_var.get()
        example  = "Tilbud Hansen" if self._lang == "no" else "Contract Smith"
        preview  = preview_output_name(template, example_stem=example)
        self._preview_value.configure(text=f"{example}.pdf  →  {preview}")

    def _on_language_change(self, label: str) -> None:
        for code, lbl in LANGUAGE_LABELS.items():
            if lbl == label:
                self._lang = code
                break
        self._refresh_labels()

    def _on_save(self) -> None:
        old_lang = self._config.get("language", "no")
        self._config.update(
            {
                "output_template": self._template_var.get(),
                "notify_on_success": self._notify_var.get(),
                "open_after_merge":  self._open_var.get(),
                "language":          self._lang,
            }
        )
        save_config(self._config)

        # Re-register context menu if language changed so labels update
        if self._lang != old_lang and sys.platform == "win32":
            exe = sys.executable if getattr(sys, "frozen", False) else sys.argv[0]
            try:
                from src.combiner.registry import register
                from src.combiner.i18n import get as t
                register(
                    exe=exe,
                    combine_label=t("context_menu_combine", self._lang),
                    settings_label=t("context_menu_settings", self._lang),
                )
            except Exception:
                pass

        self.destroy()


def main() -> None:
    app = SettingsApp()
    app.mainloop()


if __name__ == "__main__":
    main()
