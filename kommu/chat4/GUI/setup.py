from cx_Freeze import setup, Executable
import sys
import os

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
tcl_library = os.path.join(sys.base_prefix, 'tcl', 'tcl8.6')
tk_library = os.path.join(sys.base_prefix, 'tcl', 'tk8.6')

# List of additional files to include in the build
include_files = [
    r'C:\\Users\\Steve\\Documents\\Scripts\\Projekt_Arbet\\Quantum\\projekt_Quantik\\.env\\Lib\\site-packages\\qiskit\\qasm\\libs',r'C:\\Users\\Steve\\Documents\\Scripts\\Projekt_Arbet\\Quantum\\projekt_Quantik\\.env\\Lib\\site-packages\\qiskit\\VERSION.txt', 
    r'C:\\Users\\Steve\\Documents\\Scripts\\Projekt_Arbet\\Quantum\\projekt_Quantik\\.env\\Lib\\site-packages\\qiskit_aer\\VERSION.txt',r'C:\\Users\\Steve\\Documents\\Scripts\\Projekt_Arbet\\Quantum\\projekt_Quantik\\.env\\Lib\\site-packages\\qiskit_ibm_provider\\VERSION.txt', 
    r'C:\\Users\\Steve\\Documents\\Scripts\\Projekt_Arbet\\Quantum\\projekt_Quantik\\kommu\\chat4\\GUI\\token.txt',
    (tcl_library, os.path.join('lib', 'tcl8.6')),
    (tk_library, os.path.join('lib', 'tk8.6')),
]

build_exe_options = {
    'packages': packages,
    'include_files': include_files,
    'includes': ['tkinter'],
    'excludes': []
}
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="middleman",
    version="0.1",
    description="middleman implementation",
    options={"build_exe": build_exe_options},
    executables=[Executable("middleman.py", base=base)],
         
)
