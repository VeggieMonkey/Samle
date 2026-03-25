"""Manual ordering dialog for Samle.

Shown when multiple files lack vedlegg-N numbering so the merge order
cannot be determined automatically.  The user drags rows or uses the
▲/▼ buttons to set the desired order, then clicks «Samle» or «Avbryt».
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

_BLUE = "#2D6EDC"
_BLUE_HOVER = "#1E50A2"
_ROW_NORMAL = ("gray90", "gray22")
_ROW_DRAG = ("gray78", "gray32")
_ROW_TARGET = ("gray82", "gray28")

WINDOW_W = 500


def _icon_path() -> str | None:
    candidates = [
        Path(__file__).parent.parent.parent / "assets" / "icon.ico",
        Path(sys.executable).parent / "icon.ico",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


class OrderDialog(ctk.CTk):
    """Standalone window for manually ordering PDF files before merging."""

    def __init__(self, paths: list[Path], lang: str = "no") -> None:
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        from src.combiner.i18n import get
        self._get = get
        self._lang = lang
        self._paths = sorted(paths, key=lambda p: p.name)
        self._result: list[Path] | None = None

        # Drag state
        self._drag_index: int | None = None
        self._rows: list[dict] = []

        self.title(get("order_dialog_title", lang))
        self.resizable(False, True)
        self.minsize(WINDOW_W, 320)

        icon = _icon_path()
        if icon and sys.platform == "win32":
            try:
                self.iconbitmap(icon)
            except Exception:
                pass

        self._build_ui()

        # Size and centre
        n = len(self._paths)
        list_h = min(n * 56 + 16, 400)
        total_h = 68 + 80 + list_h + 64  # header + info + list + footer
        self.geometry(f"{WINDOW_W}x{total_h}")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - WINDOW_W) // 2
        y = (self.winfo_screenheight() - total_h) // 2
        self.geometry(f"{WINDOW_W}x{total_h}+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        get = self._get
        lang = self._lang

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Header ────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=_BLUE, corner_radius=0, height=68)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=get("order_dialog_title", lang),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white",
            fg_color="transparent",
        ).grid(row=0, column=0, padx=20, pady=(12, 0), sticky="w")

        ctk.CTkLabel(
            header,
            text=get("order_dialog_subtitle", lang),
            font=ctk.CTkFont(size=11),
            text_color="#C8D8F8",
            fg_color="transparent",
        ).grid(row=1, column=0, padx=20, pady=(0, 12), sticky="w")

        # ── Info box ──────────────────────────────────────────────────────
        info_box = ctk.CTkFrame(
            self,
            fg_color=("gray94", "gray16"),
            corner_radius=0,
        )
        info_box.grid(row=1, column=0, sticky="ew")
        info_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            info_box,
            text=get("order_dialog_info", lang),
            font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70"),
            anchor="w",
            justify="left",
            wraplength=WINDOW_W - 48,
        ).grid(row=0, column=0, padx=24, pady=12, sticky="w")

        # ── Sortable list ─────────────────────────────────────────────────
        self._list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self._list_frame.grid(row=2, column=0, sticky="nsew", padx=14, pady=(8, 4))
        self._list_frame.grid_columnconfigure(0, weight=1)

        self._rebuild_rows()

        # ── Footer ────────────────────────────────────────────────────────
        footer = ctk.CTkFrame(
            self,
            fg_color=("gray92", "gray18"),
            corner_radius=0,
            height=60,
        )
        footer.grid(row=3, column=0, sticky="ew")
        footer.grid_propagate(False)
        footer.grid_columnconfigure(0, weight=1)

        btn_frame = ctk.CTkFrame(footer, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=16, pady=13)

        ctk.CTkButton(
            btn_frame,
            text=get("settings_cancel", lang),
            command=self._on_cancel,
            width=100,
            height=34,
            fg_color=("gray80", "gray30"),
            hover_color=("gray70", "gray40"),
            text_color=("gray20", "gray90"),
            font=ctk.CTkFont(size=13),
            corner_radius=6,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text=get("order_dialog_merge_btn", lang),
            command=self._on_merge,
            width=110,
            height=34,
            fg_color=_BLUE,
            hover_color=_BLUE_HOVER,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=6,
        ).pack(side="left")

    # ── Row management ─────────────────────────────────────────────────────

    def _rebuild_rows(self) -> None:
        """Destroy all rows and recreate them from self._paths."""
        for entry in self._rows:
            entry["frame"].destroy()
        self._rows.clear()

        for i, path in enumerate(self._paths):
            entry = self._make_row(i, path)
            entry["frame"].grid(row=i, column=0, sticky="ew", pady=3)
            self._rows.append(entry)

    def _make_row(self, index: int, path: Path) -> dict:
        """Create one sortable row and return a dict of widget references."""
        n = len(self._paths)

        frame = ctk.CTkFrame(
            self._list_frame,
            fg_color=_ROW_NORMAL,
            corner_radius=8,
            height=48,
        )
        frame.grid_columnconfigure(1, weight=1)

        # Drag grip
        grip = ctk.CTkLabel(
            frame,
            text="⠿",
            font=ctk.CTkFont(size=20),
            text_color=("gray55", "gray50"),
            fg_color="transparent",
            cursor="fleur",
            width=32,
        )
        grip.grid(row=0, column=0, padx=(10, 2), pady=10)

        # Filename
        name_lbl = ctk.CTkLabel(
            frame,
            text=path.name,
            font=ctk.CTkFont(size=13),
            anchor="w",
            fg_color="transparent",
        )
        name_lbl.grid(row=0, column=1, padx=(0, 8), pady=10, sticky="ew")

        # Up / Down buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=(0, 10), pady=8)

        up_btn = ctk.CTkButton(
            btn_frame,
            text="▲",
            width=30,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=("gray78", "gray32"),
            hover_color=("gray65", "gray45"),
            text_color=("gray20", "gray80"),
            corner_radius=5,
            command=lambda i=index: self._move(i, -1),
            state="normal" if index > 0 else "disabled",
        )
        up_btn.pack(side="left", padx=(0, 4))

        down_btn = ctk.CTkButton(
            btn_frame,
            text="▼",
            width=30,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=("gray78", "gray32"),
            hover_color=("gray65", "gray45"),
            text_color=("gray20", "gray80"),
            corner_radius=5,
            command=lambda i=index: self._move(i, +1),
            state="normal" if index < n - 1 else "disabled",
        )
        down_btn.pack(side="left")

        # Drag bindings on the grip label
        grip.bind("<ButtonPress-1>", lambda e, f=frame: self._drag_start(e, f))
        grip.bind("<B1-Motion>", self._drag_motion)
        grip.bind("<ButtonRelease-1>", self._drag_end)

        return {
            "frame": frame,
            "grip": grip,
            "name_lbl": name_lbl,
            "up_btn": up_btn,
            "down_btn": down_btn,
        }

    # ── Reordering ─────────────────────────────────────────────────────────

    def _move(self, index: int, delta: int) -> None:
        """Move item at *index* by *delta* and rebuild."""
        new_idx = index + delta
        if 0 <= new_idx < len(self._paths):
            self._paths[index], self._paths[new_idx] = (
                self._paths[new_idx],
                self._paths[index],
            )
            self._rebuild_rows()

    # ── Drag handlers ──────────────────────────────────────────────────────

    def _row_index(self, frame) -> int | None:
        """Return the current position of *frame* in self._rows."""
        for i, entry in enumerate(self._rows):
            if entry["frame"] is frame:
                return i
        return None

    def _drag_start(self, event, frame) -> None:
        idx = self._row_index(frame)
        if idx is None:
            return
        self._drag_index = idx
        frame.configure(fg_color=_ROW_DRAG)

    def _drag_motion(self, event) -> None:
        if self._drag_index is None:
            return

        # Reset non-dragged rows to normal, highlight the row under the cursor
        for i, entry in enumerate(self._rows):
            if i == self._drag_index:
                continue
            target = False
            try:
                ry = entry["frame"].winfo_rooty()
                rh = entry["frame"].winfo_height()
                if ry <= event.y_root <= ry + rh:
                    target = True
            except Exception:
                pass
            entry["frame"].configure(fg_color=_ROW_TARGET if target else _ROW_NORMAL)

    def _drag_end(self, event) -> None:
        if self._drag_index is None:
            return

        # Find which row the cursor was released over
        target_idx = None
        for i, entry in enumerate(self._rows):
            try:
                ry = entry["frame"].winfo_rooty()
                rh = entry["frame"].winfo_height()
                if ry <= event.y_root <= ry + rh:
                    target_idx = i
                    break
            except Exception:
                pass

        if target_idx is not None and target_idx != self._drag_index:
            item = self._paths.pop(self._drag_index)
            self._paths.insert(target_idx, item)

        self._drag_index = None
        self._rebuild_rows()

    # ── Actions ────────────────────────────────────────────────────────────

    def _on_cancel(self) -> None:
        self._result = None
        self.destroy()

    def _on_merge(self) -> None:
        self._result = list(self._paths)
        self.destroy()

    # ── Public API ─────────────────────────────────────────────────────────

    @classmethod
    def ask_order(cls, paths: list[Path], lang: str = "no") -> list[Path] | None:
        """Show the dialog, block until closed, and return the ordered list.

        Returns ``None`` if the user cancelled.
        """
        dialog = cls(paths, lang)
        dialog.mainloop()
        return dialog._result
