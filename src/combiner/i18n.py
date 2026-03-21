"""Simple dict-based internationalization for pypdf-combiner."""

STRINGS = {
    "no": {
        "context_menu_combine": "Kombiner PDF-er",
        "context_menu_settings": "Innstillinger for PDF-kombinering...",
        "toast_success_title": "PDF kombinert",
        "toast_success_msg": "Lagret som: {filename}",
        "toast_error_title": "Feil ved kombinering",
        "toast_error_msg": "Kunne ikke kombinere PDF-er: {error}",
        "toast_warn_encrypted": "Advarsel: Kryptert fil hoppet over: {filename}",
        "default_template": "{name} med vedlegg",
        "settings_title": "Innstillinger",
        "settings_language": "Språk",
        "settings_template_label": "Mal for filnavn:",
        "settings_template_hint": "Tilgjengelig: {name}, {date}, {date_no}",
        "settings_preview_label": "Forhåndsvisning:",
        "settings_notify": "Vis varsling etter sammenslåing",
        "settings_open": "Åpne fil etter sammenslåing",
        "settings_subtitle": "Innstillinger for PDF-kombinering",
        "settings_behaviour": "Atferd",
        "settings_save": "Lagre",
        "settings_cancel": "Avbryt",
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
