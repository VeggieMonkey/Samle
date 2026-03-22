"""Entry point for pypdf-combiner.

Dispatch table based on sys.argv:

    (no args)               → open settings UI
    --settings              → open settings UI
    --register-menu         → write Windows registry context menu keys
    --unregister-menu       → remove Windows registry context menu keys
    <file.pdf> [...]        → accumulate paths, then merge (context menu flow)
"""

import sys
from pathlib import Path


def _launch_settings() -> None:
    from src.settings_ui.app import SettingsApp  # type: ignore[import]

    app = SettingsApp()
    app.mainloop()


def _do_merge(file_path: str) -> None:
    from src.combiner.accumulator import collect_or_register
    from src.combiner.config import load_config
    from src.combiner.i18n import get
    from src.combiner.merger import merge_pdfs
    from src.combiner.namer import render_output_name
    from src.combiner.notify import notify_error, notify_success, notify_warning
    from src.combiner.sorter import sort_pdfs

    paths = collect_or_register(file_path)
    if not paths:
        return  # We are a follower; leader will handle merging

    config = load_config()
    lang = config.get("language", "no")

    try:
        sorted_paths, main_doc = sort_pdfs(paths)
        if not sorted_paths or main_doc is None:
            notify_error(
                get("toast_error_title", lang),
                get("toast_error_msg", lang, error="No valid PDF files found"),
            )
            return

        output_dir = main_doc.parent
        output_path = render_output_name(
            config.get("output_template", get("default_template", lang)),
            main_doc,
            output_dir,
        )

        skipped = merge_pdfs(sorted_paths, output_path)

        for s in skipped:
            notify_warning(
                get("toast_error_title", lang),
                get("toast_warn_encrypted", lang, filename=Path(s).name),
            )

        if config.get("notify_on_success", True):
            notify_success(
                get("toast_success_title", lang),
                get("toast_success_msg", lang, filename=output_path.name),
            )

        if config.get("open_after_merge", False):
            import os
            import subprocess

            if sys.platform == "win32":
                os.startfile(str(output_path))  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(output_path)])

    except Exception as exc:
        notify_error(
            get("toast_error_title", lang),
            get("toast_error_msg", lang, error=str(exc)),
        )
        raise


def _register_menu() -> None:
    from src.combiner.config import load_config
    from src.combiner.i18n import get
    from src.combiner.registry import register

    config = load_config()
    lang = config.get("language", "no")
    exe = sys.executable if getattr(sys, "frozen", False) else sys.argv[0]
    register(
        exe=exe,
        combine_label=get("context_menu_combine", lang),
        settings_label=get("context_menu_settings", lang),
    )


def _unregister_menu() -> None:
    from src.combiner.registry import unregister

    unregister()


def main() -> None:
    args = sys.argv[1:]

    if not args or "--settings" in args:
        _launch_settings()
    elif "--register-menu" in args:
        _register_menu()
    elif "--unregister-menu" in args:
        _unregister_menu()
    else:
        # Assume first arg is a PDF file path from the context menu
        _do_merge(args[0])


if __name__ == "__main__":
    main()
