#define AppName "Crane Vehicle BOM Manager"
#define AppVersion "1.0.0"
#define AppExeName "CraneVehicleBOMManager.exe"

[Setup]
AppId={{9E430E42-EF1A-41DE-98D6-41E19F5AC928}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Crane Vehicle Engineering Tool
DefaultDirName={autopf}\Crane Vehicle BOM Manager
DefaultGroupName={#AppName}
OutputDir=output
OutputBaseFilename=CraneVehicleBOMManager_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#AppExeName}

[Files]
Source: "dist\CraneVehicleBOMManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "เปิด {#AppName}"; Flags: postinstall nowait skipifsilent
