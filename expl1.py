from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_histogram

# Génération d'une paire de qubits pour Alice et Bob
qc = QuantumCircuit(2, 2)
qc.h(0)  # Hadamard gate pour le qubit d'Alice
qc.cx(0, 1)  # Porte CNOT pour le qubit d'Alice à celui de Bob

# Mesure des qubits
qc.measure([0, 1], [0, 1])

# Simulation du circuit quantique
simulator = Aer.get_backend('qasm_simulator')
job = execute(qc, simulator, shots=1)
result = job.result()
counts = result.get_counts(qc)

# Affichage des résultats
print(counts)
plot_histogram(counts)
