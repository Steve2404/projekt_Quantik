# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['bb84.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit/VERSION.txt', 'qiskit/'), ('/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit_aer/VERSION.txt', 'qiskit_aer/'), ('/home/steve/Dokumente/Script/projekt_Quantik/kommu/chat4/GUI/token.txt', 'kommu/chat4/GUI'), ('/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit/qasm/libs', 'qiskit/qasm/libs'), ('/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit_ibm_provider/VERSION.txt', 'qiskit_ibm_provider/')
    ],
    hiddenimports=[
        'qiskit',
        'qiskit_aer',
    ],
    hookspath=['/home/steve/Dokumente/Script/projekt_Quantik/kommu/chat4/GUI/hook-qiskit.py'],
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
    name='bb84',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
