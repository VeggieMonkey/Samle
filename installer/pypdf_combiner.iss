; Inno Setup script for pypdf-combiner
; Per-user install — no administrator rights required.

#define AppName "pypdf-combiner"
#define AppVersion "1.0.0"
#define AppPublisher "pypdf-combiner"
#define AppExeName "pypdf_combiner.exe"

[Setup]
AppId={{A3B7F2E1-4C9D-4F8A-B2E3-1D5C7A9F0E2B}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\{#AppName}
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
OutputDir=..\dist\installer
OutputBaseFilename=pypdf-combiner-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Require Windows 10 or later
MinVersion=10.0.17763

[Languages]
Name: "norwegian"; MessagesFile: "compiler:Languages\Norwegian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\pypdf_combiner\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName} Settings"; Filename: "{app}\{#AppExeName}"; Parameters: "--settings"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#AppName} Settings"; Filename: "{app}\{#AppExeName}"; Parameters: "--settings"; Tasks: desktopicon

[Run]
; Register the right-click context menu after installation
Filename: "{app}\{#AppExeName}"; Parameters: "--register-menu"; \
  Description: "Registering PDF context menu..."; \
  Flags: runhidden waituntilterminated

[UninstallRun]
; Remove context menu entries before uninstall
Filename: "{app}\{#AppExeName}"; Parameters: "--unregister-menu"; \
  Flags: runhidden waituntilterminated

[Code]
// No custom code needed — standard Inno Setup handles everything.
