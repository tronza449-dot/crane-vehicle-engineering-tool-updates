#define MyAppName "Crane Vehicle Engineering Tool"
#define MyAppVersion "53.2.1"
#define MyAppPublisher "Mechatronics Engineering Project"
#define MyAppExeName "CraneEngineeringTool.exe"

#define MyDistDir GetEnv("CVET_DIST_DIR")
#define MyOutputDir GetEnv("CVET_OUTPUT_DIR")

[Setup]
AppId={{30EA4D0A-92B3-4B4D-B6CD-CFA8E6427AF4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Crane Vehicle Engineering Tool
DefaultGroupName={#MyAppName}
PrivilegesRequired=admin
OutputDir={#MyOutputDir}
OutputBaseFilename=CraneVehicleEngineeringTool_Setup
SetupIconFile=..\assets\CraneEngineeringTool.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; One-click behavior
DisableStartupPrompt=yes
DisableWelcomePage=yes
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableReadyPage=yes
DisableFinishedPage=yes
AllowNoIcons=no

VersionInfoVersion=53.2.1.0
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#MyDistDir}\CraneEngineeringTool\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Flags: nowait runasoriginaluser

















