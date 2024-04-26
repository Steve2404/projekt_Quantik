import qiskit as q
import qiskit_aer as qe
from qiskit.compiler import transpile
import numpy as np

# simulateur
simulator = qe.Aer.get_backend('statevector_simulator')
# construction du circuit
circuit = q.QuantumCircuit(1)
# initialisation de alpha et beta
alpha0 = np.sqrt(3)/2
beta0 = (1-1j)/(2*np.sqrt(2))
norme = np.sqrt(abs(alpha0)**2 + abs(beta0)**2)
# normaliser
alpha, beta = alpha0/norme, beta0/norme
# definition de l etat initiale
etat_initial = [alpha, beta]
qubit_initial = circuit.initialize(etat_initial, circuit.qubits)

# insertion dune porte X
circuit.x(0)
circuit.x(0)
circuit.y(0)
print(circuit.draw())

# execution
job = simulator.run(transpile(circuit, simulator))

# Resultat
result = job.result()
coef = result.get_statevector()
print(f"Coefficient alpha: {coef[0]}")
print(f"Coefficient beta: {coef[1]}")