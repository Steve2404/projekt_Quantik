# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['spion.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit_ibm_provider/VERSION.txt', 'qiskit_ibm_provider/'), ('/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit/VERSION.txt', 'qiskit/'), ('/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit_aer/VERSION.txt', 'qiskit_aer/'), ('/home/steve/Dokumente/Script/projekt_Quantik/kommu/chat4/token.txt', 'kommu/chat4/'), ('/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit/qasm/libs', 'qiskit/qasm/libs')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='spion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
