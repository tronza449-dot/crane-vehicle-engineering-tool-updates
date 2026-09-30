# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

project = Path(SPECPATH)
source = project / 'CraneVehicleEngineeringTool.py'
icon = project / 'assets' / 'CraneEngineeringTool.ico'

hidden = ['PySide6.QtPrintSupport','serial','serial.tools.list_ports']

analysis = Analysis(
    [str(source)],
    pathex=[str(project)],
    binaries=[],
    datas=[(str(icon), 'assets')],
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(analysis.pure)
exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name='CraneEngineeringTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon),
)
coll = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='CraneEngineeringTool',
)
