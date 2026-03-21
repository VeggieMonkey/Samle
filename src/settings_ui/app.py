"""Settings window for pypdf-combiner.

Built with customtkinter so it follows the Windows 11 light/dark system theme
automatically.  Displays a live preview of the output filename template.
"""

import sys

try:
    import customtkinter as ctk
except ImportError:
    raise ImportError(
        "customtkinter is required for the settings UI. "
        "Install it with: pip install customtkinter"
    )

# Use sys.path manipulation only when running the module directly during dev.
# In the PyInstaller bundle the package structure is already flat.
if __name__ == "__main__":
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.combiner.config import load_config, save_config
from src.combiner.i18n import LANGUAGE_LABELS, STRINGS, get
from src.combiner.namer import preview_output_name
from src.combiner.registry import register, unregister


_EXAMPLE_STEM = "Tilbud Hansen"
_WINDOW_W = 520
_WINDOW_H = 420


class SettingsApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self._config = load_config()
        self._lang = self._config.get("language", "no")
        self._lang_codes = list(LANGUAGE_LABELS.keys())  # ["no", "en"]

        self.title(get("settings_title", self._lang))
        self.geometry(f"{_WINDOW_W}x{_WINDOW_H}")
        self.resizable(False, False)

        self._build_ui()
        self._update_preview()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        pad = {"padx": 20, "pady": 6}

        # --- Language row ---
        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.pack(fill="x", **pad)

        self._lang_label = ctk.CTkLabel(
            lang_frame, text=get("settings_language", self._lang), anchor="w"
        )
        self._lang_label.pack(side="left")

        self._lang_var = ctk.StringVar(
            value=LANGUAGE_LABELS[self._lang]
        )
        self._lang_menu = ctk.CTkOptionMenu(
            lang_frame,
            variable=self._lang_var,
            values=list(LANGUAGE_LABELS.values()),
            command=self._on_language_change,
            width=120,
        )
        self._lang_menu.pack(side="right")

        ctk.CTkSeparator(self, orientation="horizontal").pack(
            fill="x", padx=20, pady=4
        )

        # --- Template label + entry ---
        self._template_label = ctk.CTkLabel(
            self, text=get("settings_template_label", self._lang), anchor="w"
        )
        self._template_label.pack(fill="x", **pad)

        self._template_var = ctk.StringVar(
            value=self._config.get("output_template", get("default_template", self._lang))
        )
        self._template_entry = ctk.CTkEntry(
            self, textvariable=self._template_var, width=_WINDOW_W - 40
        )
        self._template_entry.pack(fill="x", padx=20, pady=(0, 4))
        self._template_var.trace_add("write", lambda *_: self._update_preview())

        self._hint_label = ctk.CTkLabel(
            self,
            text=get("settings_template_hint", self._lang),
            anchor="w",
            text_color="gray",
            font=ctk.CTkFont(size=12),
        )
        self._hint_label.pack(fill="x", padx=20, pady=(0, 6))

        # --- Preview ---
        self._preview_label = ctk.CTkLabel(
            self, text=get("settings_preview_label", self._lang), anchor="w"
        )
        self._preview_label.pack(fill="x", **pad)

        self._preview_value = ctk.CTkLabel(
            self,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._preview_value.pack(fill="x", padx=20, pady=(0, 6))

        ctk.CTkSeparator(self, orientation="horizontal").pack(
            fill="x", padx=20, pady=4
        )

        # --- Toggles ---
        self._notify_var = ctk.BooleanVar(
            value=self._config.get("notify_on_success", True)
        )
        self._notify_switch = ctk.CTkSwitch(
            self,
            text="",  # set below via _refresh_labels
            variable=self._notify_var,
        )
        self._notify_switch.pack(fill="x", **pad)

        self._open_var = ctk.BooleanVar(
            value=self._config.get("open_after_merge", False)
        )
        self._open_switch = ctk.CTkSwitch(
            self,
            text="",
            variable=self._open_var,
        )
        self._open_switch.pack(fill="x", **pad)

        ctk.CTkSeparator(self, orientation="horizontal").pack(
            fill="x", padx=20, pady=8
        )

        # --- Buttons ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 12))

        self._cancel_btn = ctk.CTkButton(
            btn_frame,
            text=get("settings_cancel", self._lang),
            command=self.destroy,
            fg_color="gray",
            hover_color="darkgray",
            width=100,
        )
        self._cancel_btn.pack(side="right", padx=(8, 0))

        self._save_btn = ctk.CTkButton(
            btn_frame,
            text=get("settings_save", self._lang),
            command=self._on_save,
            width=100,
        )
        self._save_btn.pack(side="right")

        # --- About ---
        ctk.CTkLabel(
            self,
            text="pypdf-combiner v1.0.0",
            text_color="gray",
            font=ctk.CTkFont(size=11),
        ).pack(side="bottom", pady=6)

        self._refresh_labels()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _refresh_labels(self) -> None:
        """Update all translatable labels to the current language."""
        lang = self._lang
        self.title(get("settings_title", lang))
        self._lang_label.configure(text=get("settings_language", lang))
        self._template_label.configure(text=get("settings_template_label", lang))
        self._hint_label.configure(text=get("settings_template_hint", lang))
        self._preview_label.configure(text=get("settings_preview_label", lang))
        self._notify_switch.configure(text=get("settings_notify", lang))
        self._open_switch.configure(text=get("settings_open", lang))
        self._save_btn.configure(text=get("settings_save", lang))
        self._cancel_btn.configure(text=get("settings_cancel", lang))
        self._update_preview()

    def _update_preview(self) -> None:
        template = self._template_var.get()
        preview = preview_output_name(template, example_stem=_EXAMPLE_STEM)
        self._preview_value.configure(
            text=f"{_EXAMPLE_STEM}.pdf  →  {preview}"
        )

    def _on_language_change(self, label: str) -> None:
        # Find the lang code that matches the selected label
        for code, lbl in LANGUAGE_LABELS.items():
            if lbl == label:
                self._lang = code
                break
        self._refresh_labels()

    def _on_save(self) -> None:
        new_lang = self._lang
        old_lang = self._config.get("language", "no")

        self._config.update(
            {
                "output_template": self._template_var.get(),
                "notify_on_success": self._notify_var.get(),
                "open_after_merge": self._open_var.get(),
                "language": new_lang,
            }
        )
        save_config(self._config)

        # Re-register context menu if language changed (updates labels)
        if new_lang != old_lang and sys.platform == "win32":
            from src.combiner.i18n import get as t

            exe = sys.executable if getattr(sys, "frozen", False) else sys.argv[0]
            try:
                register(
                    exe=exe,
                    combine_label=t("context_menu_combine", new_lang),
                    settings_label=t("context_menu_settings", new_lang),
                )
            except Exception:
                pass  # Non-fatal; user can re-register manually

        self.destroy()


def main() -> None:
    app = SettingsApp()
    app.mainloop()


if __name__ == "__main__":
    main()
