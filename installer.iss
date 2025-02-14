#define MyAppName "HITSZ Connect Verge"
#define MyAppPublisher "Kowyo"
#define MyAppURL "https://github.com/kowyo/hitsz-connect-verge"
#define MyAppExeName "HITSZ Connect Verge.exe"

[Setup]
AppId={{4BA3EC9B-F383-4A7F-8354-32951FC2A417}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=dist
OutputBaseFilename=hitsz-connect-verge-windows-{#Architecture}-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed={#ArchitecturesAllowed}
ArchitecturesInstallIn64BitMode={#ArchitecturesInstallIn64BitMode}
CloseApplications=force
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=assets\icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove the entire application directory after uninstalling.
Type: filesandordirs; Name: "{app}"

[Code]
procedure CurUninstallStepsChange(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    // Force-kill the main executable and any child processes
    if Exec('taskkill.exe', '/f /t /im "HITSZ Connect Verge.exe"', '', SW_HIDE,
      ewWaitUntilTerminated, ResultCode) then
    begin
      if ResultCode <> 0 then
        Log('Warning: taskkill returned error code ' + IntToStr(ResultCode));
    end
    else
      Log('Error: failed to execute taskkill.exe');
  end;
end;
