"""Windows VERSIONINFO resource for the pypdf_combiner EXE.

PyInstaller reads this file via the `version` argument in the .spec file.
Generated format: https://pyinstaller.org/en/stable/usage.html#capturing-windows-version-data
"""

# fmt: off
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,           # VOS_NT_WINDOWS32
    fileType=0x1,         # VFT_APP
    subtype=0x0,
    date=(0, 0),
  ),
  kids=[
    StringFileInfo([
      StringTable(
        "040904B0",       # US English / Unicode
        [
          StringStruct("CompanyName",      "pypdf-combiner"),
          StringStruct("FileDescription",  "PDF merging for Windows Explorer"),
          StringStruct("FileVersion",      "1.0.0.0"),
          StringStruct("InternalName",     "pypdf_combiner"),
          StringStruct("LegalCopyright",   "MIT License"),
          StringStruct("OriginalFilename", "pypdf_combiner.exe"),
          StringStruct("ProductName",      "pypdf-combiner"),
          StringStruct("ProductVersion",   "1.0.0.0"),
        ]
      ),
    ]),
    VarFileInfo([VarStruct("Translation", [0x0409, 1200])]),
  ]
)
# fmt: on
