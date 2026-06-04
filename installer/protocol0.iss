; Protocol0 Windows installer (install + autostart).
; Inspired by SyncthingWindowsSetup. Build: ISCC.exe installer\protocol0.iss
;
; Lays down:
;   - protocol0-agent.exe     -> {app} (Program Files\Protocol0): resident agent (autostart)
;   - protocol0-launcher.exe  -> {app}: the clicked "shortcut" (opens the web page). Carries
;                                the "P" icon -> Start Menu + desktop shortcuts point to it.
;   - Protocol_0\             -> <Ableton>\MIDI Remote Scripts\Protocol_0 (pure copy)
;   - task scripts            -> {app}\scripts (so the uninstaller calls its own copy)
; Then creates the scheduled task at logon. The desktop shortcut is OPTIONAL (checkbox).
; On uninstall: removes the task, deletes the files ([Icons] are removed automatically),
; BUT preserves %APPDATA%\Protocol0\shortcuts.json (never referenced).
;
; Build prerequisites: src\agent\dist\protocol0-agent.exe (which embeds src\frontend\dist),
; src\agent\dist\protocol0-launcher.exe and build\stage\Protocol_0\ must exist
; (see scripts\windows\build_installer.ps1).

#define MyAppName "Protocol 0"
; Version read from the root VERSION file (single source of truth, bumped by /commit)
; at ISCC compile time. Avoids a hardcoded version that would drift.
#define VersionFile = FileOpen(SourcePath + "..\VERSION")
#if VersionFile
  #define MyAppVersion = Trim(FileRead(VersionFile))
  #expr FileClose(VersionFile)
#else
  #error VERSION file not found at repo root
#endif
#define MyAppPublisher "Thibault Lebrun"
; Major Ableton Live version Protocol 0 supports. Auto-detection only matches
; "Live <this>*" folders. Bump here when moving to a new Live (e.g. "13").
; Keep in sync with scripts/_pyfind.py SUPPORTED_LIVE_VERSION.
#define SupportedLiveVersion "12"

[Setup]
AppId={{E7A2C3D4-5B6F-4A1E-9C8D-0F1A2B3C4D5E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Protocol0
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Admin required: writes to Program Files + to %ProgramData%\Ableton\...
PrivilegesRequired=admin
OutputDir=..\dist-installer
OutputBaseFilename=Protocol0-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
; Required so the standard messages {cm:CreateDesktopIcon} / {cm:AdditionalIcons}
; (used by [Tasks]) resolve. Default.isl = English, consistent with the rest of the wizard.
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; Optional desktop shortcut: the user chooses (it used to be created unconditionally).
; The Start Menu shortcut ([Icons] without Tasks) is always created.
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[InstallDelete]
; Empty the target folder BEFORE the copy to wipe residue from an old dev install
; (make install_script leaves .venv\, __pycache__\, poetry.toml, poetry.lock, pyproject.toml,
; .python-version). Without this, a stale __pycache__\__init__.cpython-311.pyc can mask the
; new prod __init__.py. We delete the contents (\*), not the folder; shortcuts.json lives
; in %APPDATA%, never touched.
Type: filesandordirs; Name: "{code:GetRemoteScriptsDir}\Protocol_0\*"
; Upgrade from a version that laid down an Internet shortcut (.url): remove it BEFORE
; creating the new .lnk, otherwise both coexist (duplicate "Protocol 0").
Type: files; Name: "{group}\Protocol 0.url"
Type: files; Name: "{autodesktop}\Protocol 0.url"

[Dirs]
; Grant Users the Modify right on the remote script folder (and inherit to its contents).
; Without this, the installer (elevated process) lays down files with Administrators-only
; ACLs: a dev reinstall via `make install` (not elevated) can then neither overwrite nor
; delete __init__.py -> "Access denied". With users-modify, the folder stays manageable by
; a dev install without admin.
Name: "{code:GetRemoteScriptsDir}\Protocol_0"; Permissions: users-modify

[Files]
Source: "..\src\agent\dist\protocol0-agent.exe"; DestDir: "{app}"; Flags: ignoreversion
; The clickable launcher, with its embedded "P" icon. The [Icons] point to it.
Source: "..\src\agent\dist\protocol0-launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
; users-modify: each laid-down file inherits the Modify right for Users (see [Dirs]),
; so `make install` in dev can replace them without elevation.
Source: "..\build\stage\Protocol_0\*"; DestDir: "{code:GetRemoteScriptsDir}\Protocol_0"; Permissions: users-modify; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\scripts\windows\install_protocol0_agent_task.ps1"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\scripts\windows\uninstall_protocol0_agent_task.ps1"; DestDir: "{app}\scripts"; Flags: ignoreversion

[Run]
; Create + start the scheduled task at logon. runhidden: no PowerShell window.
Filename: "powershell.exe"; \
  Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\scripts\install_protocol0_agent_task.ps1"" -ExePath ""{app}\protocol0-agent.exe"""; \
  StatusMsg: "Registering startup task..."; \
  Flags: runhidden waituntilterminated
; Final wizard page: a checkbox (ticked by default) to open Protocol 0. The launcher
; deep-links to /shortcuts (see launcher_entry.py), so this lands the user straight on
; the keymapper. nowait: don't block the wizard from closing; skipifsilent: no UI in
; silent installs.
Filename: "{app}\protocol0-launcher.exe"; \
  Description: "Open Protocol 0"; \
  Flags: postinstall nowait skipifsilent

[Icons]
; Shortcuts pointing to protocol0-launcher.exe (no longer a .url): it carries the "P" icon
; and opens the web page served by the agent (port 9010). Advantage over .url: a real app
; icon instead of the browser icon, and no console flash. The icon comes from the exe itself
; (embedded by protocol0-launcher.spec).
; Start Menu: always created. Desktop: gated on the "desktopicon" task.
Name: "{group}\Protocol 0"; Filename: "{app}\protocol0-launcher.exe"; Comment: "Open Protocol 0"
Name: "{autodesktop}\Protocol 0"; Filename: "{app}\protocol0-launcher.exe"; Comment: "Open Protocol 0"; Tasks: desktopicon

[UninstallRun]
; Remove the task BEFORE the files are deleted.
Filename: "powershell.exe"; \
  Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\scripts\uninstall_protocol0_agent_task.ps1"""; \
  RunOnceId: "RemoveAgentTask"; \
  Flags: runhidden waituntilterminated

[UninstallDelete]
; The Protocol_0 folder lives outside {app} (in the Ableton folder): delete it explicitly.
; shortcuts.json (in %APPDATA%) is never touched -> preserved.
Type: filesandordirs; Name: "{code:GetRemoteScriptsDir}\Protocol_0"
; The .lnk shortcuts created via [Icons] are removed automatically by the uninstaller.
; We additionally clean up the old .url shortcuts (created via [INI] before this change),
; so an upgrade from an earlier version does not leave a duplicate.
Type: files; Name: "{group}\Protocol 0.url"
Type: files; Name: "{autodesktop}\Protocol 0.url"

[Code]
var
  RemoteScriptsPage: TInputDirWizardPage;
  { Set by DetectRemoteScripts: True when the pre-filled path is a Beta build, so the
    wizard can tell the user it picked a Beta and let them switch. }
  DetectedBeta: Boolean;
  { Inline notice shown on the folder page (instead of a pop-up) when a Beta was picked. }
  BetaNotice: TNewStaticText;

{ True if a Live folder name denotes a Beta build, e.g. "Live 12 Beta". }
function IsBetaName(Name: String): Boolean;
begin
  Result := Pos('beta', Lowercase(Name)) > 0;
end;

{ Returns the "MIDI Remote Scripts" folder of the supported Live version found under
  %ProgramData%\Ableton (only "Live {#SupportedLiveVersion}*" folders, any edition).
  When both a stable and a Beta build of that version are present, the Beta is
  preferred (and DetectedBeta is set). Returns '' if none found. }
function DetectRemoteScripts(): String;
var
  AbletonRoot, Candidate, StableMatch, BetaMatch: String;
  FindRec: TFindRec;
begin
  Result := '';
  StableMatch := '';
  BetaMatch := '';
  DetectedBeta := False;
  AbletonRoot := ExpandConstant('{commonappdata}\Ableton');
  if not DirExists(AbletonRoot) then
    Exit;

  if FindFirst(AbletonRoot + '\Live {#SupportedLiveVersion}*', FindRec) then
  begin
    try
      repeat
        if (FindRec.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0 then
        begin
          Candidate := AbletonRoot + '\' + FindRec.Name + '\Resources\MIDI Remote Scripts';
          if DirExists(Candidate) then
          begin
            if IsBetaName(FindRec.Name) then
              BetaMatch := Candidate
            else
              StableMatch := Candidate;
          end;
        end;
      until not FindNext(FindRec);
    finally
      FindClose(FindRec);
    end;
  end;

  { Prefer Beta when present, then flag it so the wizard can warn the user. }
  if BetaMatch <> '' then
  begin
    Result := BetaMatch;
    DetectedBeta := True;
  end
  else
    Result := StableMatch;
end;

procedure InitializeWizard();
begin
  RemoteScriptsPage := CreateInputDirPage(
    wpSelectDir,
    'Ableton MIDI Remote Scripts',
    'Where should the Protocol 0 control surface be installed?',
    'Select your Ableton Live {#SupportedLiveVersion} MIDI Remote Scripts folder. ' +
    'The detected path is pre-filled (any edition: Intro, Standard, Suite); correct it if needed.',
    False, '');
  RemoteScriptsPage.Add('');
  RemoteScriptsPage.Values[0] := DetectRemoteScripts();

  { A discreet inline notice (no pop-up): created hidden, sits below the folder field
    and only appears on this page when a Beta build was pre-filled. }
  BetaNotice := TNewStaticText.Create(RemoteScriptsPage);
  BetaNotice.Parent := RemoteScriptsPage.Surface;
  BetaNotice.Left := 0;
  BetaNotice.Top := RemoteScriptsPage.Edits[0].Top + RemoteScriptsPage.Edits[0].Height + ScaleY(12);
  BetaNotice.Width := RemoteScriptsPage.SurfaceWidth;
  BetaNotice.AutoSize := False;
  BetaNotice.WordWrap := True;
  BetaNotice.Height := ScaleY(40);
  BetaNotice.Font.Color := clMaroon;
  BetaNotice.Caption :=
    'A Beta build of Ableton Live {#SupportedLiveVersion} was detected and pre-filled above. '
    + 'If you prefer a stable Live {#SupportedLiveVersion}, change the folder before clicking Next.';
  BetaNotice.Visible := False;
end;

{ Reveal the Beta notice on the folder page only; hide it everywhere else. No pop-up. }
procedure CurPageChanged(CurPageID: Integer);
begin
  BetaNotice.Visible := (CurPageID = RemoteScriptsPage.ID) and DetectedBeta;
end;

function GetRemoteScriptsDir(Param: String): String;
begin
  Result := RemoteScriptsPage.Values[0];
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = RemoteScriptsPage.ID then
  begin
    if not DirExists(RemoteScriptsPage.Values[0]) then
    begin
      MsgBox('That folder does not exist. Please select your Ableton MIDI Remote Scripts folder.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

{ Before the copy: stop the scheduled task THEN kill the process. Without stopping the
  task, the scheduler would relaunch the just-killed exe (RestartCount) and Setup would
  hit a locked file ("unable to close all the applications"). Order matters:
  Stop-ScheduledTask first (cuts the automatic relaunch), taskkill next (frees the .exe).
  The task is recreated by [Run] at the end of install. }
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Result := '';
  Exec('schtasks.exe', '/End /TN "Protocol0"',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('taskkill.exe', '/F /IM protocol0-agent.exe',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;
