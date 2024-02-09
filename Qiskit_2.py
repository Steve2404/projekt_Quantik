import qiskit as q
import qiskit_aer as qe
from qiskit.compiler import transpile
import matplotlib.pyplot as plt
import qiskit.visualization as v
import PIL

# simulation de quantenComputer
simulator = qe.Aer.get_backend('qasm_simulator')
# circuit Q avec 1 Qbit
circuit = q.QuantumCircuit(2, 2)
circuit.h(0)
circuit.x(1)
circuit.cx(0,1)
circuit.h(1)
circuit.measure([0,1], [0, 1])

img_circuit = circuit.draw(output='latex')
img_circuit.show() 

# execution
job = simulator.run(transpile(circuit, simulator), shots=100)
result = job.result()
counts = result.get_counts(circuit)
print(f"Nbre de '00', '01', '10' et de '11':  {counts}")

# visualisation
v.plot_histogram(counts)
plt.show()
