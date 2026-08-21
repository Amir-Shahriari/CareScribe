; Inno Setup script for CareScribe.
;
; Wraps the PyInstaller output in a single installer so a clinician runs one
; file, gets a desktop icon and a Start-menu entry, and launches the app like
; anything else on their machine.
;
; Build (after PyInstaller has produced dist\CareScribe\):
;     "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" packaging\carescribe.iss
;
; Inno Setup 6 is a one-time install:
;     winget install -e --id JRSoftware.InnoSetup
; or download from https://jrsoftware.org/isdl.php
;
; Output: packaging\Output\CareScribeSetup.exe

#define AppName        "CareScribe"
#define AppVersion     "1.0.0"
#define AppPublisher   "CareScribe"
#define AppExeName     "CareScribe.exe"
#define SourceDir      "..\dist\CareScribe"

[Setup]
AppId={{8E4C2F1A-7B3D-4A6E-9C15-CA7E5C21BE00}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=CareScribeSetup
SetupIconFile=carescribe.ico
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; The app is 64-bit only.
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Per-machine install if elevated, per-user if not — so a clinician without
; admin rights on a clinic laptop can still install it.
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; The whole PyInstaller folder, including _internal.
Source: "{#SourceDir}\*"; DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start menu, always.
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; \
    IconFilename: "{app}\{#AppExeName}"
; Desktop, if the user left the task ticked.
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; \
    IconFilename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; \
    Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]
; PyInstaller unpacks to a temp dir at runtime; nothing else is left behind.
; Documents the app wrote to %LOCALAPPDATA%\CareScribe are the clinician's own
; output and are deliberately NOT removed by the uninstaller.
Type: dirifempty; Name: "{app}"
