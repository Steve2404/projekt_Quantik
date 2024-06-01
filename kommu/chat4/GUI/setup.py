from cx_Freeze import setup, Executable

# List of packages to include in the build
packages = [
    'qiskit', 
    'qiskit_aer', 
    'qiskit.compiler', 
    'qiskit.providers', 
    'qiskit.transpiler', 
    'qiskit.visualization',
    'numpy',
    'matplotlib'
]

# List of additional files to include in the build
include_files = [
    '/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit_ibm_provider/VERSION.txt',
    '/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit/VERSION.txt',
    '/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit_aer/VERSION.txt',
    '/home/steve/Dokumente/Script/projekt_Quantik/kommu/chat4/GUI/token.txt',
    '/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit/qasm/libs'
]

build_exe_options = {
    'packages': packages,
    'include_files': include_files,
    'excludes': []
}

setup(
    name="bb84",
    version="0.1",
    description="Quantum BB84 protocol implementation",
    options={"build_exe": build_exe_options},
    executables=[Executable("bb84.py")],
    build_base="build_base", 
    build_exe="build_exe"     
)
