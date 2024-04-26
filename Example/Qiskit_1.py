import qiskit as q

import matplotlib.pyplot as plt
import qiskit_aer as qe
from qiskit.compiler import transpile




#q.Aer = AerProvider()
# simulation de quantenComputer
simulator = qe.Aer.get_backend('qasm_simulator')

# circuit Q avec 1 Qbit
circuit = q.QuantumCircuit(2, 2)

# 1 porte de Hadamard
circuit.h(0)
circuit.cx(0,1)

# mesure de du qubit
circuit.measure([0,1], [0,1])

# Affichage du circuit
print(circuit.draw(output='text'))

# lancer 100 simulation
job = simulator.run(transpile(circuit, simulator), shots=100)
result = job.result()

# comptage
counts = result.get_counts(circuit)
print(f"Nombre de '0' et '1' : {counts}")

# Visualisation
q.visualization.plot_histogram(counts)
plt.show()