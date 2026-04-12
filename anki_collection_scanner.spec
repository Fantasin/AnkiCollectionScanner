# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for anki_collection_scanner
# Build with: pyinstaller anki_collection_scanner.spec
#
# After building, copy local_audio_static/ next to the .exe:
#   dist\anki_collection_scanner\local_audio_static\

a = Analysis(
    ['anki_collection_scanner/main.py'],
    pathex=[],
    binaries=[],
    # local_audio_static/ is intentionally NOT bundled here — it is too large
    # and must be distributed as an external folder next to the .exe.
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'requests',
        'bs4',
    ],
    hookspath=[],
    hooksconfig={},
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='anki_collection_scanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # set True temporarily when debugging to see tracebacks
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='anki_collection_scanner',
)
