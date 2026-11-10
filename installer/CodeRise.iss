; CodeRise 0.3 — локальный установщик Inno Setup 6

#define AppName "CodeRise"
#define AppVersion "0.3.0"
#define AppPublisher "LeemonSun"
#define AppExe "CodeRise.exe"

[Setup]
AppId={{B71E73B0-E2AD-42B8-82AD-ABAAFC6F53E4}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppVerName={#AppName} {#AppVersion}
DefaultDirName={localappdata}\Programs\CodeRise
DefaultGroupName=CodeRise
UninstallDisplayIcon={app}\{#AppExe}
OutputDir=..\release
OutputBaseFilename=CodeRise-Setup-{#AppVersion}
SetupIconFile=..\build\coderise.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
ChangesAssociations=no
CloseApplications=yes
RestartApplications=no
MinVersion=10.0.17763
ArchitecturesAllowed=x64compatible
UsePreviousAppDir=yes
UsePreviousTasks=yes
SetupLogging=yes

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Ярлыки:"; Flags: unchecked

[Files]
Source: "..\dist\CodeRise\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\CodeRise"; Filename: "{app}\{#AppExe}"; WorkingDir: "{app}"
Name: "{autodesktop}\CodeRise"; Filename: "{app}\{#AppExe}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Запустить CodeRise"; Flags: nowait postinstall skipifsilent
