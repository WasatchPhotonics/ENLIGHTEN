; See the file py2exe_application.py for details on how to create a
; windows installer

; Redefine these for the application to be built
#define MyAppName "ENLIGHTEN"
#define module_name "enlighten"
#define MyAppExeName "ENLIGHTEN.exe"
#define MyAppPublisher "Wasatch Photonics"
#define MyAppURL "https://wasatchphotonics.com"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{4B74A30D-C158-4D4F-8244-DC4579A4E414}

; ENLIGHTEN_VERSION is passed to iscc.exe via /D command-line argument
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
OutputDir=..\windows_installer
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=..\src\{#module_name}\assets\uic_qrc\images\EnlightenIcon.ico
UninstallDisplayIcon="{app}\{#MyAppName}\{#MyAppExeName}"
PrivilegesRequired=poweruser
WizardStyle=modern
WizardImageFile=..\src\enlighten\assets\uic_qrc\images\logos\wp-314.bmp,..\src\enlighten\assets\uic_qrc\images\logos\wp-386.bmp

; use standard compression defaults (lzma2/max)
; @see https://jrsoftware.org/ishelp/index.php?topic=setup_compression

; will write installation logfile to %TEMP% (based on when the installer is run, not built)
SetupLogging=yes

; disable warning about "PrivilegesRequired is set to poweruser but per-user areas (userdocs) are used" 
UsedUserAreasWarning=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; "Regular" files
Source: "..\dist\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

; possibly for https://pyinstaller.org/en/v6.0.0/usage.html#windows
Source: "support_files\msvcr100.dll"; DestDir: "{app}\enlighten\"; Flags: recursesubdirs ignoreversion

; Include libusb dll's. Note this is only required for appveyor builds. Building on a Windows 10
; Home Premium system with the libusb drivers installed seems to copy them over for back end
; usage during the executable build. That's right, x86 for all platforms. This may be correct
; because it's 32bit python on 64bit windows.
Source: "support_files\libusb_drivers\amd64\libusb0.dll"; DestDir: "{app}\enlighten\"; Flags: recursesubdirs ignoreversion

; Files and directories to be copied as-is into the destination directory tree
Source: "..\src\enlighten\assets\stylesheets\*"; DestDir: "{app}\enlighten\enlighten\assets\stylesheets\"; Flags: recursesubdirs ignoreversion
Source: "..\src\enlighten\assets\example_data\*"; DestDir: "{app}\enlighten\enlighten\assets\example_data\"; Flags: recursesubdirs ignoreversion
Source: "..\src\enlighten\assets\uic_qrc\images\EnlightenIcon.ico"; DestDir: "{app}\enlighten"; DestName: "default_icon.ico"
Source: "..\dist\KIAConsole.exe"; DestDir: "{app}\enlighten"
Source: "..\dist\CyUSB3-Win10.zip"; DestDir: "{app}\enlighten"
Source: "..\dist\DFU_Drivers.zip"; DestDir: "{app}\enlighten"

; Signed LIBUSB drivers
Source: "support_files\libusb_drivers\*"; Flags: recursesubdirs; DestDir: "{app}\enlighten\libusb_drivers"

; Andor drivers
Source: "..\dist\Andor\*"; DestDir: "{app}\enlighten\"; Flags: recursesubdirs ignoreversion

; Manifest file for HiDPI mitigation - see above
; Source: "support_files\Enlighten.exe.manifest"; DestDir: "{app}\Enlighten\"; Flags: recursesubdirs ignoreversion

; ------------------------------------------------------------------------------
; Visual C++ redistributable, apparently needed by KnowItAll
; ------------------------------------------------------------------------------

; standard 2015/17/19 runtime. Extracted by VCRedistNeedsInstall(), if needed. (used by KnowItAll)
Source: "..\dist\VC_redist.x86.exe"; DestDir: {tmp}; Flags: dontcopy

; 64-bit -> System32 ({sysnative} on 64-bit...)
Source: "..\dist\Windows\System32\*"; DestDir: "{sysnative}"

; 32-bit -> SysWOW64 ({sys} or {syswow64})
Source: "..\dist\Windows\SysWOW64\*"; DestDir: "{sys}"

; installer Wizard logos
Source: "..\src\enlighten\assets\uic_qrc\images\logos\*"; DestDir: "{app}\enlighten\enlighten\assets\uic\images\logos\"

; ENLIGHTEN Plug-In examples
; Note that under Mac Parallels, this lands into the Mac Documents folder, not on C:
Source: "..\src\enlighten\plugins\*"; DestDir: "{app}\enlighten\plugins"; Flags: recursesubdirs

[Icons]
Name: "{group}\{#MyAppName} {#ENLIGHTEN_VERSION}"; Filename: "{app}\{#MyAppName}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppName}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName} {#ENLIGHTEN_VERSION}"; Filename: "{app}\{#MyAppName}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Install LibUsb signed drivers
Filename: "{code:GetPnpUtilDir}\pnputil.exe"; Parameters: "-i -a ""{app}\enlighten\libusb_drivers\WPLibUsb.inf"" "; StatusMsg: "Installing WP LIBUSB drivers (this may take a few seconds) ..."; Flags: runhidden

; install Visual C++ redistributable, if necessary (used by KnowItAll)
Filename: "{tmp}\VC_redist.x86.exe"; StatusMsg: "Installing VC++ redistributable"; Parameters: "/quiet"; Check: VCRedistNeedsInstall ; Flags: waituntilterminated

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
function VCRedistNeedsInstall: Boolean;
var
  Version: String;
begin
  if (RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x86', 'Version', Version)) then
      begin
          // Is the installed version at least 14.14 ?
          Log('VC Redist Version check : found ' + Version);
          Result := (CompareStr(Version, 'v14.14.26429.03')<0);
      end
  else
      begin
          // Not even an old version installed
          Result := True;
      end;
  if (Result) then
    begin
        ExtractTemporaryFile('VC_redist.x86.exe');
    end;
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
