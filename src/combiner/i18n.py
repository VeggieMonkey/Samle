"""Simple dict-based internationalization for Samle."""

STRINGS = {
    "no": {
        "context_menu_combine": "Samle PDF'er",
        "context_menu_settings": "Samle-innstillinger...",
        "toast_success_title": "PDF kombinert",
        "toast_success_msg": "Lagret som: {filename}",
        "toast_error_title": "Feil ved kombinering",
        "toast_error_msg": "Kunne ikke kombinere PDF-er: {error}",
        "toast_warn_encrypted": "Advarsel: Kryptert fil hoppet over: {filename}",
        "default_template": "{name} med vedlegg {date_no}",
        "settings_title": "Innstillinger",
        "settings_language": "Språk",
        "settings_template_label": "Mal for filnavn:",
        "settings_template_hint": "Tilgjengelig: {name}, {date}, {date_no}",
        "settings_preview_label": "Forhåndsvisning:",
        "settings_notify": "Vis varsling etter sammenslåing",
        "settings_open": "Åpne fil etter sammenslåing",
        "settings_subtitle": "Innstillinger for Samle",
        "settings_behaviour": "Atferd",
        "settings_save": "Lagre",
        "settings_cancel": "Avbryt",
        "update_available": "Oppdatering tilgjengelig: v{version} — klikk for å laste ned",
        "order_dialog_title": "Velg rekkefølge",
        "order_dialog_subtitle": "Sorter filene manuelt før sammenslåing",
        "order_dialog_info": (
            "Flere av filene mangler vedlegg-nummerering (f.eks. «Vedlegg 1», «Vedlegg 2»), "
            "så rekkefølgen kan ikke bestemmes automatisk.\n\n"
            "Dra filene til ønsket rekkefølge, eller bruk pilene. "
            "Den øverste filen brukes som hoveddokument."
        ),
        "order_dialog_merge_btn": "Samle",
    },
    "en": {
        "context_menu_combine": "Combine PDFs",
        "context_menu_settings": "PDF Combiner Settings...",
        "toast_success_title": "PDF combined",
        "toast_success_msg": "Saved as: {filename}",
        "toast_error_title": "Combine error",
        "toast_error_msg": "Could not combine PDFs: {error}",
        "toast_warn_encrypted": "Warning: Encrypted file skipped: {filename}",
        "default_template": "{name} with attachments",
        "settings_title": "Settings",
        "settings_language": "Language",
        "settings_template_label": "Output filename template:",
        "settings_template_hint": "Available: {name}, {date}, {date_no}",
        "settings_preview_label": "Preview:",
        "settings_notify": "Show notification after merging",
        "settings_open": "Open file after merging",
        "settings_subtitle": "PDF merge settings",
        "settings_behaviour": "Behaviour",
        "settings_save": "Save",
        "settings_cancel": "Cancel",
        "update_available": "Update available: v{version} — click to download",
        "order_dialog_title": "Choose order",
        "order_dialog_subtitle": "Sort files manually before merging",
        "order_dialog_info": (
            "Several files lack vedlegg numbering (e.g. \"Vedlegg 1\", \"Vedlegg 2\"), "
            "so the order cannot be determined automatically.\n\n"
            "Drag files into the desired order, or use the arrows. "
            "The top file will be used as the main document."
        ),
        "order_dialog_merge_btn": "Merge",
    },
}

LANGUAGE_LABELS = {
    "no": "Norsk",
    "en": "English",
}


def get(key: str, lang: str = "no", **kwargs) -> str:
    """Return a translated string, optionally formatting with kwargs."""
    lang_strings = STRINGS.get(lang, STRINGS["no"])
    template = lang_strings.get(key, STRINGS["no"].get(key, key))
    if kwargs:
        return template.format(**kwargs)
    return template
