from cx_Freeze import setup, Executable

setup(
    name = "bb84",
    version = "0.1",
    description = "Quantum BB84 protocol implementation",
    executables = [Executable("bb84.py")],
    options = {
        'build_exe': {
            'packages': ['qiskit', 'qiskit_aer', 'qiskit.compiler', 'qiskit.providers', 'qiskit.transpiler', 'qiskit.visualization'],
            'include_files': [
                '/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit_ibm_provider/VERSION.txt',
                '/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit/VERSION.txt',
                '/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit_aer/VERSION.txt',
                '/home/steve/Dokumente/Script/projekt_Quantik/kommu/chat4/GUI/token.txt',
                '/home/steve/Dokumente/Script/projekt_Quantik/.venv/lib/python3.11/site-packages/qiskit/qasm/libs',
            ],
        }
    }
)
