# hook-qiskit.py

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('qiskit')
hiddenimports = collect_submodules('qiskit')

print(datas)
