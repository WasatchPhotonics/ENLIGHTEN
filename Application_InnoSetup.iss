#define MyAppName "ENLIGHTEN"
#define MyAppExeName "enlighten.exe"
#define MyAppPublisher "Wasatch Photonics"
#define MyAppURL "https://wasatchphotonics.com"

[Setup]
AppId={{4B74A30D-C158-4D4F-8244-DC4579A4E414}

; ENLIGHTEN_VERSION and COMPRESSION are passed to iscc.exe via /D command-line argument
AppVersion={#ENLIGHTEN_VERSION}
OutputBaseFilename={#MyAppName}-Setup64-{#ENLIGHTEN_VERSION}
AppName={#MyAppName}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
Compression={#COMPRESSION}
DefaultDirName={commonpf}\Wasatch Photonics\{#MyAppName}
DisableDirPage=yes
DefaultGroupName=Wasatch Photonics
OutputDir=.
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=..\src\wp_enlighten\assets\uic_qrc\images\EnlightenIcon.ico
UninstallDisplayIcon="{app}\{#MyAppName}\{#MyAppExeName}"
PrivilegesRequired=poweruser
WizardStyle=modern

; write installation logfile to %TEMP% (when the installer is run, not built)
SetupLogging=yes

; disable warning about "PrivilegesRequired is set to poweruser but per-user areas (userdocs) are used" 
UsedUserAreasWarning=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; "Regular" files
Source: "pyinstaller-build\dist\enlighten\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

; possibly for https://pyinstaller.org/en/v6.0.0/usage.html#windows
; MZ: Source: "support_files\msvcr100.dll"; DestDir: "{app}\enlighten\"; Flags: recursesubdirs ignoreversion

; Include libusb dll's. Note this is only required for appveyor builds. Building
; on Windows with the libusb drivers installed seems to copy them over for 
; backend usage during the executable build. That's right, x86 for all platforms. 
; This may be correct because it's 32bit python on 64bit windows?
Source: "dist\support_files\libusb_drivers\amd64\libusb0.dll"; DestDir: "{app}\enlighten\"; Flags: recursesubdirs ignoreversion

; Files and directories to be copied as-is into the destination directory tree
; MZ: Source: "src\wp_enlighten\assets\stylesheets\*"; DestDir: "{app}\enlighten\enlighten\assets\stylesheets\"; Flags: recursesubdirs ignoreversion
; MZ: Source: "src\wp_enlighten\assets\example_data\*"; DestDir: "{app}\enlighten\enlighten\assets\example_data\"; Flags: recursesubdirs ignoreversion
Source: "src\wp_enlighten\assets\uic_qrc\images\EnlightenIcon.ico"; DestDir: "{app}\enlighten"; DestName: "default_icon.ico"
Source: "dist\CyUSB3-Win10.zip"; DestDir: "{app}\enlighten"
Source: "dist\DFU_Drivers.zip"; DestDir: "{app}\enlighten"

; Signed LIBUSB drivers
Source: "dist\support_files\libusb_drivers\*"; Flags: recursesubdirs; DestDir: "{app}\enlighten\libusb_drivers"

; Andor drivers
Source: "dist\Andor\*"; DestDir: "{app}\enlighten\"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName} {#ENLIGHTEN_VERSION}"; Filename: "{app}\{#MyAppName}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppName}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName} {#ENLIGHTEN_VERSION}"; Filename: "{app}\{#MyAppName}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Install LibUsb signed drivers
Filename: "{code:GetPnpUtilDir}\pnputil.exe"; Parameters: "-i -a ""{app}\enlighten\libusb_drivers\WPLibUsb.inf"" "; StatusMsg: "Installing .inf file (this may take a few seconds) ..."; Flags: runhidden

[Code]

{ ///////////////////////////////////////////////////////////////////// }
function GetPnpUtilDir(Param: String): String;
begin
    if DirExists('C:\Windows\sysnative') then
        Result := 'C:\Windows\sysnative'
    else
        Result := 'C:\Windows\System32';
end;

{ ///////////////////////////////////////////////////////////////////// }
{ //  https://stackoverflow.com/a/2099805/6436775                       }
{ ///////////////////////////////////////////////////////////////////// }
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

{ ///////////////////////////////////////////////////////////////////// }
function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

{ ///////////////////////////////////////////////////////////////////// }
function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  { Return Values: }
  { 1 - uninstall string is empty }
  { 2 - error executing the UnInstallString }
  { 3 - successfully executed the UnInstallString }

  { default return value }
  Result := 0;

  { get the uninstall string of the old app }
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

{ ///////////////////////////////////////////////////////////////////// }
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (IsUpgrade()) then
    begin
      UnInstallOldVersion();
    end;
  end;
end;
