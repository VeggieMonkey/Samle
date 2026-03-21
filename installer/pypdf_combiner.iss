; ============================================================================
;  pypdf-combiner  –  Inno Setup installer script
;  Per-user install: no administrator rights required.
; ============================================================================

#define AppName        "pypdf-combiner"
#define AppVersion     "1.0.0"
#define AppPublisher   "pypdf-combiner"
#define AppURL         "https://github.com/VeggieMonkey/Pypdf-combiner"
#define AppExeName     "pypdf_combiner.exe"
#define AppDescription "PDF merging for Windows Explorer"

[Setup]
; Unique application ID — do NOT change after first release
AppId={{A3B7F2E1-4C9D-4F8A-B2E3-1D5C7A9F0E2B}

AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases

; Per-user install — no UAC prompt
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline

; Install location
DefaultDirName={localappdata}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes

; Output
OutputDir=..\dist\installer
OutputBaseFilename=pypdf-combiner-{#AppVersion}-setup
SetupIconFile=..\assets\icon.ico

; Wizard images
WizardImageFile=..\assets\installer_side.bmp
WizardSmallImageFile=..\assets\installer_header.bmp
WizardImageStretch=no
WizardStyle=modern

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Require Windows 10 1809 or later (build 17763)
MinVersion=10.0.17763

; Uninstaller
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName} {#AppVersion}

; Misc
ShowLanguageDialog=auto
ChangesAssociations=yes

[Languages]
Name: "norwegian"; MessagesFile: "compiler:Languages\Norwegian.isl"
Name: "english";   MessagesFile: "compiler:Default.isl"

[Messages]
; Override wizard title and subtitle for a cleaner look
english.WelcomeLabel1=Welcome to the {#AppName} Setup Wizard
english.WelcomeLabel2=This will install {#AppName} {#AppVersion} on your computer.%n%nThis tool adds a right-click context menu entry to Windows Explorer so you can merge PDF files with a single click.%n%nClick Next to continue.

norwegian.WelcomeLabel1=Velkommen til installasjonsveiledningen for {#AppName}
norwegian.WelcomeLabel2=Dette vil installere {#AppName} {#AppVersion} på datamaskinen din.%n%nVerktøyet legger til et høyreklikk-menyvalg i Windows Utforsker slik at du kan slå sammen PDF-filer med ett klikk.%n%nKlikk Neste for å fortsette.

[Tasks]
Name: "desktopicon"; \
  Description: "{cm:CreateDesktopIcon}"; \
  GroupDescription: "{cm:AdditionalIcons}"; \
  Flags: unchecked

[Files]
; Main application bundle (PyInstaller --onedir output)
Source: "..\dist\pypdf_combiner\*"; \
  DestDir: "{app}"; \
  Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\{#AppName} Settings"; \
  Filename: "{app}\{#AppExeName}"; \
  Parameters: "--settings"; \
  Comment: "{#AppDescription}"; \
  IconFilename: "{app}\{#AppExeName}"

Name: "{group}\{cm:UninstallProgram,{#AppName}}"; \
  Filename: "{uninstallexe}"; \
  IconFilename: "{app}\{#AppExeName}"

; Optional desktop shortcut
Name: "{commondesktop}\{#AppName} Settings"; \
  Filename: "{app}\{#AppExeName}"; \
  Parameters: "--settings"; \
  Comment: "{#AppDescription}"; \
  IconFilename: "{app}\{#AppExeName}"; \
  Tasks: desktopicon

[Registry]
; Raise the Windows multi-file selection limit to 100 files
Root: HKCU; \
  Subkey: "Software\Microsoft\Windows\CurrentVersion\Explorer"; \
  ValueType: dword; \
  ValueName: "MultipleInvokePromptMinimum"; \
  ValueData: 100; \
  Flags: uninsdeletevalue

[Run]
; Register the right-click context menu entry after installation
Filename: "{app}\{#AppExeName}"; \
  Parameters: "--register-menu"; \
  WorkingDir: "{app}"; \
  StatusMsg: "Registering PDF context menu..."; \
  Flags: runhidden waituntilterminated

; Offer to open Settings when install finishes
Filename: "{app}\{#AppExeName}"; \
  Parameters: "--settings"; \
  WorkingDir: "{app}"; \
  Description: "Open {#AppName} Settings"; \
  Flags: nowait postinstall skipifsilent

[UninstallRun]
; Remove context menu entries before files are deleted
Filename: "{app}\{#AppExeName}"; \
  Parameters: "--unregister-menu"; \
  WorkingDir: "{app}"; \
  Flags: runhidden waituntilterminated

[UninstallDelete]
; Clean up the config directory on uninstall (optional — comment out to preserve user config)
; Type: filesandordirs; Name: "{localappdata}\pypdf-combiner-config"
