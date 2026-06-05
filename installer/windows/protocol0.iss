; Protocol0 Windows installer (install + autostart).
; Inspired by SyncthingWindowsSetup. Build: ISCC.exe installer\windows\protocol0.iss
;
; Lays down:
;   - Protocol0.exe           -> {app} (Program Files\Protocol0): resident agent (keyboard
;                                hook + web UI on :9010 + systray). Carries the "P" icon.
;   - Protocol_0\             -> <Ableton>\MIDI Remote Scripts\Protocol_0 (pure copy)
; Autostart = a shortcut in the user's Startup folder ([Icons] -> {userstartup}, NOT a
; scheduled task), created when the "Start at login" checkbox is ticked. The Start Menu /
; desktop shortcuts launch the agent with --open (start-on-click, AutoHotkey style); the
; desktop one is OPTIONAL. All shortcuts are [Icons], so the uninstaller removes them
; automatically. On uninstall: kills the agent, deletes the files, BUT preserves
; %APPDATA%\Protocol0\shortcuts.json.
;
; Build prerequisites: src\agent\target\release\Protocol0.exe (the native Rust agent,
; which embeds src\frontend\dist AND installer\windows\assets\protocol0.ico) and build\stage\Protocol_0\
; must exist (see installer\windows\build_installer.ps1). The agent is a Rust binary now; no Python
; is shipped.

#define MyAppName "Protocol 0"
; Version read from the root VERSION file (single source of truth, bumped by /commit)
; at ISCC compile time. Avoids a hardcoded version that would drift.
#define VersionFile = FileOpen(SourcePath + "..\..\VERSION")
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
; AppVerName drives the name shown in Settings -> Apps / Add-Remove Programs. Without it,
; Windows shows "Protocol 0 version 0.18.3"; pin it to the bare name. (AppVersion is still
; recorded and shown in the separate Version column.)
AppVerName={#MyAppName}
AppPublisher={#MyAppPublisher}
; Icon shown next to the app in Settings -> Apps / Add-Remove Programs (the "P" badge).
; Points at the installed agent exe, which carries the icon as a PE resource.
UninstallDisplayIcon={app}\Protocol0.exe
DefaultDirName={autopf}\Protocol0
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Admin required: writes to Program Files + to %ProgramData%\Ableton\...
PrivilegesRequired=admin
; We intentionally create a per-user shortcut in {userstartup} (the autostart) and start the
; agent as the original user (runasoriginaluser) while the install itself is elevated. This is
; deliberate for a single-user desktop tool, so silence Inno's generic per-user-area warning.
UsedUserAreasWarning=no
OutputDir=..\..\dist-installer
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
; Start at login: creates the Startup-folder shortcut (the autostart). Ticked by default,
; but the user explicitly consents (espanso-style) -- and can untick it, or later remove it
; from Task Manager -> Startup. GroupDescription left blank -> its own group at the top.
Name: "startuplogin"; Description: "Start Protocol 0 at login"
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
; The resident agent (native Rust exe), with its embedded "P" icon. The [Icons] point to it
; (with --open). Built by installer\windows\build_agent_exe.ps1 (cargo build --release).
Source: "..\..\src\agent\target\release\Protocol0.exe"; DestDir: "{app}"; Flags: ignoreversion
; users-modify: each laid-down file inherits the Modify right for Users (see [Dirs]),
; so `make install` in dev can replace them without elevation.
Source: "..\..\build\stage\Protocol_0\*"; DestDir: "{code:GetRemoteScriptsDir}\Protocol_0"; Permissions: users-modify; Flags: ignoreversion recursesubdirs createallsubdirs

[Run]
; Start the agent now (resident: keyboard hook + web UI + systray) and open the config page.
; runasoriginaluser: the installer is elevated, but the agent must run as the LOGGED-ON user
; (a low-level keyboard hook + the foreground check live in the user's interactive session,
; not the elevated/admin context). It also needs no admin rights. --open lands on /shortcuts.
; nowait: don't block the wizard; skipifsilent: no UI in silent installs.
Filename: "{app}\Protocol0.exe"; Parameters: "--open"; \
  Description: "Launch Protocol 0"; \
  Flags: postinstall nowait skipifsilent runasoriginaluser

[Icons]
; Clickable shortcuts launch the agent with --open (start-on-click, AutoHotkey style): if the
; agent is not running, this starts it (resident: keyboard hook + web UI + systray); either way
; it opens the config page (/shortcuts) in the browser. The "P" icon comes from the agent exe
; itself (embedded as a PE resource by src\agent\build.rs); IconFilename pins it explicitly on the .lnk too.
; Start Menu: always created. Desktop: gated on the "desktopicon" task.
Name: "{group}\Protocol 0"; Filename: "{app}\Protocol0.exe"; Parameters: "--open"; Comment: "Launch Protocol 0"; IconFilename: "{app}\Protocol0.exe"
Name: "{autodesktop}\Protocol 0"; Filename: "{app}\Protocol0.exe"; Parameters: "--open"; Comment: "Launch Protocol 0"; IconFilename: "{app}\Protocol0.exe"; Tasks: desktopicon
; Autostart shortcut in the user's Startup folder (NO --open: the logon launch must be silent,
; not pop a browser tab every session). Gated on the "Start at login" task. Inno creates it
; under {userstartup} and removes it automatically at uninstall -- no PowerShell, no elevation
; gymnastics. IconFilename pins the "P" icon so the .lnk (and Task Manager -> Startup, which
; reads the shortcut's target exe) shows it. (Under admin install mode {userstartup} targets the
; installing user's profile; for the single-user desktop case this is the intended user.)
Name: "{userstartup}\Protocol 0"; Filename: "{app}\Protocol0.exe"; Comment: "Protocol 0 (auto-start at logon)"; IconFilename: "{app}\Protocol0.exe"; Tasks: startuplogin

[UninstallRun]
; Kill the running agent BEFORE the files are deleted, otherwise its locked exe in {app}
; cannot be removed. The Startup + Start-Menu + desktop shortcuts are [Icons] -> Inno removes
; them automatically. taskkill on a not-running agent just exits non-zero -> harmless.
Filename: "taskkill.exe"; Parameters: "/F /IM Protocol0.exe"; \
  RunOnceId: "KillAgent"; \
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

{ Before the copy: clear any prior autostart and free the .exe so the copy never hits a
  locked file.
  1. Upgrade from a version that used a SCHEDULED TASK: delete it (and end it first, so its
     RestartCount policy does not relaunch the exe we are about to kill). Otherwise the old
     task AND the new Startup shortcut would both launch the agent -> two keyboard hooks.
  2. Remove an existing Startup shortcut: [Icons] recreates it only if the box is ticked, so
     re-installing with the box unticked must not leave a stale one.
  3. Kill the running agent: frees the exe in the app dir for overwrite. We kill BOTH the new
     image name ("Protocol0.exe") and the OLD one ("protocol0-agent.exe"), so upgrading from a
     pre-rename version stops the old resident agent too.
  4. Delete the OLD exe ("protocol0-agent.exe") left in the app dir by a pre-rename version: the
     new build no longer ships it, so [Files] would not overwrite it and it would linger.
  schtasks/taskkill on a non-existent target just exit non-zero -> harmless (ResultCode ignored). }
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
  OldLink, OldExe: String;
begin
  Result := '';
  Exec('schtasks.exe', '/End /TN "Protocol0"',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('schtasks.exe', '/Delete /TN "Protocol0" /F',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  OldLink := ExpandConstant('{userstartup}\Protocol 0.lnk');
  if FileExists(OldLink) then
    DeleteFile(OldLink);
  Exec('taskkill.exe', '/F /IM Protocol0.exe',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('taskkill.exe', '/F /IM protocol0-agent.exe',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  OldExe := ExpandConstant('{app}\protocol0-agent.exe');
  if FileExists(OldExe) then
    DeleteFile(OldExe);
end;
