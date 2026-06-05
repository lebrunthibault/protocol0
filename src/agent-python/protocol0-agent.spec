# -*- mode: python ; coding: utf-8 -*-
# Spec PyInstaller de l'agent Protocol0.
#
# Build : depuis src/agent-python,  poetry run pyinstaller --clean --noconfirm protocol0-agent.spec
# Sortie : dist/Protocol0.exe (binaire autonome, sans Python ni Poetry requis sur la cible).
#
# Notes :
# - L'exe sert un site web LOCAL (127.0.0.1:9010 : home + keymapper + api docs + /api + /status),
#   capture le clavier ET porte l'icône systray (agent/tray.py). Aucun appel réseau sortant, aucun
#   download/lancement d'exe : le profil antivirus reste proche du Jalon 1. http.server/json sont
#   stdlib (statiquement visibles), requests est déjà embarqué.
# - La SPA Vue 3 (build statique src/frontend/dist) est embarquée via datas (dossier "frontend")
#   et lue via sys._MEIPASS par agent/web/static_files.py. Le build DOIT exister avant PyInstaller
#   (cf. scripts/windows/build_installer.ps1, étape Vite).
# - protocol0.ico est embarqué via datas (lu via sys._MEIPASS par agent/tray.py pour le systray).
#   Il est généré par scripts/windows/generate_icon.py AVANT ce build (cf. build_agent_exe.ps1).
# - console=False : l'exe est lancé caché au logon (raccourci Startup folder) ; pas de flash console.
#   Lancé à la main (raccourci Menu Démarrer) il reçoit --open : ouvre la page config, puis devient
#   résident ou sort via le mutex single-instance.
# - hiddenimports : pynput charge son backend plateforme paresseusement (pynput.keyboard._win32 /
#   pynput.mouse._win32) ; pystray choisit son backend plateforme au runtime (pystray._win32). Ni
#   l'un ni l'autre n'est vu par l'analyse statique -> sans ça l'exe gelé lèverait un ImportError.
# - upx=False : la compression UPX déclenche des faux positifs antivirus, d'autant qu'un agent
#   à hook clavier est déjà un profil sensible.

block_cipher = None

# PE version metadata (read from the root VERSION file -> never drifts). Populated
# metadata is a positive trust signal for AV heuristics on an unsigned exe.
from version_info import version_resource

a = Analysis(
    ['agent\\main_entry.py'],
    pathex=[],
    binaries=[],
    # VERSION (racine du repo) -> lu via sys._MEIPASS par agent/version.py.
    # frontend/dist (build Vite de la SPA) -> dossier "frontend", lu par agent/web/static_files.py.
    datas=[
        ('..\\..\\VERSION', '.'),
        ('..\\..\\src\\frontend\\dist', 'frontend'),
        ('..\\..\\installer\\assets\\protocol0.ico', '.'),
    ],
    hiddenimports=['pynput.keyboard._win32', 'pynput.mouse._win32', 'pystray._win32'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    # name='Protocol0' -> l'exe est "Protocol0.exe" (sans espace). C'est ce nom que Windows
    # affiche dans l'Explorateur et dans Gestionnaire des tâches -> Démarrage (qui prend le nom
    # du fichier cible du raccourci, pas le nom du .lnk).
    name='Protocol0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    # icon : l'icône "P" en RESSOURCE PE de l'exe -> affichée par l'Explorateur, les raccourcis
    # et Gestionnaire des tâches. (Le même .ico est AUSSI embarqué en datas ci-dessus pour que
    # le systray le charge au runtime via _MEIPASS ; les deux usages sont distincts.)
    icon='..\\..\\installer\\assets\\protocol0.ico',
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=version_resource("Protocol0", "Protocol0.exe"),
)
