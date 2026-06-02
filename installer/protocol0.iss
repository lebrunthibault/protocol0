; Installeur Windows de Protocol0 (Jalon 1 : install + autostart).
; Inspiré de SyncthingWindowsSetup. Build : ISCC.exe installer\protocol0.iss
;
; Dépose :
;   - protocol0-detector.exe  -> {app} (Program Files\Protocol0)
;   - Protocol_0\             -> <Ableton>\MIDI Remote Scripts\Protocol_0 (copie pure)
;   - scripts de tâche        -> {app}\scripts (pour que l'uninstaller appelle sa copie)
; Puis crée la tâche planifiée au logon. À la désinstallation : retire la tâche, supprime
; les fichiers, MAIS préserve %APPDATA%\Protocol0\shortcuts.json (jamais référencé).
;
; Prérequis de build : src\detector\dist\protocol0-detector.exe et build\stage\Protocol_0\
; doivent exister (cf. scripts\build_installer.ps1).

#define MyAppName "Protocol 0"
; Version lue depuis le fichier VERSION racine (source de vérité unique, bumpée par /commit)
; au moment de la compilation ISCC. Évite une version hardcodée qui dériverait.
#define VersionFile = FileOpen(SourcePath + "..\VERSION")
#if VersionFile
  #define MyAppVersion = Trim(FileRead(VersionFile))
  #expr FileClose(VersionFile)
#else
  #error VERSION file not found at repo root
#endif
#define MyAppPublisher "Thibault Lebrun"

[Setup]
AppId={{E7A2C3D4-5B6F-4A1E-9C8D-0F1A2B3C4D5E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Protocol0
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Admin requis : écriture dans Program Files + dans %ProgramData%\Ableton\...
PrivilegesRequired=admin
OutputDir=..\dist-installer
OutputBaseFilename=Protocol0-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[InstallDelete]
; Vide le dossier cible AVANT la copie pour effacer les résidus d'une ancienne install dev
; (make install_script laisse .venv\, __pycache__\, poetry.toml, poetry.lock, pyproject.toml,
; .python-version). Sans ça, un __pycache__\__init__.cpython-311.pyc périmé peut masquer le
; nouveau __init__.py prod. On supprime le contenu (\*), pas le dossier ; shortcuts.json est
; en %APPDATA%, jamais touché.
Type: filesandordirs; Name: "{code:GetRemoteScriptsDir}\Protocol_0\*"

[Dirs]
; Donne aux Users le droit Modify sur le dossier du remote script (et héritage vers
; le contenu). Sans ça, l'installeur (process élevé) pose des fichiers en ACL
; Administrators-only : une réinstall dev par `make install` (non élevée) ne peut alors
; ni écraser ni supprimer __init__.py -> "Access denied". Avec users-modify, le dossier
; reste géré par une install dev sans admin.
Name: "{code:GetRemoteScriptsDir}\Protocol_0"; Permissions: users-modify

[Files]
Source: "..\src\detector\dist\protocol0-detector.exe"; DestDir: "{app}"; Flags: ignoreversion
; users-modify : chaque fichier déposé hérite du droit Modify pour les Users (cf. [Dirs]),
; pour que `make install` en dev puisse les remplacer sans élévation.
Source: "..\build\stage\Protocol_0\*"; DestDir: "{code:GetRemoteScriptsDir}\Protocol_0"; Permissions: users-modify; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\scripts\install_protocol0_detector_task.ps1"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\scripts\uninstall_protocol0_detector_task.ps1"; DestDir: "{app}\scripts"; Flags: ignoreversion

[Run]
; Crée + démarre la tâche planifiée au logon. runhidden : pas de fenêtre PowerShell.
Filename: "powershell.exe"; \
  Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\scripts\install_protocol0_detector_task.ps1"" -ExePath ""{app}\protocol0-detector.exe"""; \
  StatusMsg: "Registering startup task..."; \
  Flags: runhidden waituntilterminated

[UninstallRun]
; Retire la tâche AVANT que les fichiers ne soient supprimés.
Filename: "powershell.exe"; \
  Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\scripts\uninstall_protocol0_detector_task.ps1"""; \
  RunOnceId: "RemoveDetectorTask"; \
  Flags: runhidden waituntilterminated

[UninstallDelete]
; Le dossier Protocol_0 vit hors de {app} (dans le dossier Ableton) : à supprimer
; explicitement. shortcuts.json (dans %APPDATA%) n'est jamais touché -> préservé.
Type: filesandordirs; Name: "{code:GetRemoteScriptsDir}\Protocol_0"

[Code]
var
  RemoteScriptsPage: TInputDirWizardPage;

{ Renvoie le dossier "MIDI Remote Scripts" de la version de Live la plus récente
  trouvée sous %ProgramData%\Ableton\Live*, ou '' si rien. Tri décroissant sur le
  nom de dossier -> "Live 12 Suite" passe avant "Live 11 ...". }
function DetectRemoteScripts(): String;
var
  AbletonRoot, Best, Candidate: String;
  FindRec: TFindRec;
begin
  Result := '';
  Best := '';
  AbletonRoot := ExpandConstant('{commonappdata}\Ableton');
  if not DirExists(AbletonRoot) then
    Exit;

  if FindFirst(AbletonRoot + '\Live*', FindRec) then
  begin
    try
      repeat
        if (FindRec.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0 then
        begin
          Candidate := AbletonRoot + '\' + FindRec.Name + '\Resources\MIDI Remote Scripts';
          if DirExists(Candidate) then
          begin
            { Compare sur le nom de version (FindRec.Name) pour garder le plus récent. }
            if (Best = '') or (FindRec.Name > Best) then
            begin
              Best := FindRec.Name;
              Result := Candidate;
            end;
          end;
        end;
      until not FindNext(FindRec);
    finally
      FindClose(FindRec);
    end;
  end;
end;

procedure InitializeWizard();
begin
  RemoteScriptsPage := CreateInputDirPage(
    wpSelectDir,
    'Ableton MIDI Remote Scripts',
    'Where should the Protocol 0 control surface be installed?',
    'Select your Ableton MIDI Remote Scripts folder. The detected path is pre-filled with the latest Ableton version found; correct it if needed.',
    False, '');
  RemoteScriptsPage.Add('');
  RemoteScriptsPage.Values[0] := DetectRemoteScripts();
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

{ Avant la copie : arrêter la tâche planifiée PUIS tuer le process. Sans l'arrêt
  de la tâche, le scheduler relancerait l'exe aussitôt tué (RestartCount) et Setup
  retomberait sur un fichier verrouillé ("unable to close all the applications").
  L'ordre compte : Stop-ScheduledTask d'abord (coupe le relancement automatique),
  taskkill ensuite (libère le .exe). La tâche est recréée par [Run] en fin d'install. }
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Result := '';
  Exec('schtasks.exe', '/End /TN "Protocol0"',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('taskkill.exe', '/F /IM protocol0-detector.exe',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;
