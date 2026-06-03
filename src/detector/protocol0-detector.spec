# -*- mode: python ; coding: utf-8 -*-
# Spec PyInstaller du détecteur Protocol0.
#
# Build : depuis src/detector,  poetry run pyinstaller --clean --noconfirm protocol0-detector.spec
# Sortie : dist/protocol0-detector.exe (binaire autonome, sans Python ni Poetry requis sur la cible).
#
# Notes :
# - L'exe ouvre désormais un socket d'écoute LOCAL (127.0.0.1:9010, page launcher) en plus de
#   capturer le clavier. Aucun appel réseau sortant, aucun download/lancement d'exe : le profil
#   antivirus reste proche du Jalon 1. http.server/json sont stdlib (statiquement visibles),
#   requests est déjà embarqué -> pas de nouvel hiddenimport requis.
# - console=False : l'exe est lancé caché par la tâche planifiée au logon ; pas de flash de console.
# - hiddenimports : pynput charge son backend plateforme paresseusement (pynput.keyboard._win32 /
#   pynput.mouse._win32), que l'analyse statique de PyInstaller ne voit pas -> sans ça l'exe gelé
#   lèverait un ImportError au runtime.
# - upx=False : la compression UPX déclenche des faux positifs antivirus, d'autant qu'un détecteur
#   clavier est déjà un profil sensible.

block_cipher = None

a = Analysis(
    ['detector\\main_entry.py'],
    pathex=[],
    binaries=[],
    # VERSION (racine du repo) embarqué dans le bundle -> lu via sys._MEIPASS par
    # detector/version.py, l'exe n'ayant pas d'arbre source pour remonter jusqu'à lui.
    datas=[('..\\..\\VERSION', '.')],
    hiddenimports=['pynput.keyboard._win32', 'pynput.mouse._win32'],
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
    name='protocol0-detector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
