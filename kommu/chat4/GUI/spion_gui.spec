# -*- mode: python ; coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.join('C:\\', 'path_to_your_virtualenv', 'Lib', 'site-packages'))


a = Analysis(
    ['spion_gui.py'],
    pathex=[r'C:\\Users\\Steve\\Documents\\Scripts\\Projekt_Arbet\\Quantum\\projekt_Quantik\\kommu\\chat4\\GUI'],
    binaries=[],
    datas=[
            (r'C:\\Users\\Steve\\Documents\\Scripts\\Projekt_Arbet\\Quantum\\projekt_Quantik\\.env\\Lib\\site-packages\\qiskit\\qasm\\libs', 'qiskit\\qasm\\libs'),
            (r'C:\\Users\\Steve\\Documents\\Scripts\\Projekt_Arbet\\Quantum\\projekt_Quantik\\.env\\Lib\\site-packages\\qiskit\\VERSION.txt', 'qiskit\\'),
            (r'C:\\Users\\Steve\\Documents\\Scripts\\Projekt_Arbet\\Quantum\\projekt_Quantik\\.env\\Lib\\site-packages\\qiskit_aer\\VERSION.txt', 'qiskit_aer\\'),
            (r'C:\\Users\\Steve\\Documents\\Scripts\\Projekt_Arbet\\Quantum\\projekt_Quantik\\.env\\Lib\\site-packages\\qiskit_ibm_provider\\VERSION.txt', 'qiskit_ibm_provider\\'),
            (r'C:\\Users\\Steve\\Documents\\Scripts\\Projekt_Arbet\\Quantum\\projekt_Quantik\\kommu\\chat4\\GUI\\token.txt', 'token\\')
        ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='spion_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='spion_gui',
)
