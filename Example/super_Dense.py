import qiskit as q
import qiskit_aer as qe
from qiskit.compiler import transpile
import matplotlib.pyplot as plt
import qiskit.visualization as v

# quantum machine
simulator = qe.Aer.get_backend('qasm_simulator')
# setting up a circuit
circuit = q.QuantumCircuit(2, 2)
# preparation of the bell report
circuit.h(0)
circuit.cx(0,1)

msg_alice = '00' # choix: 00 01 10 11

# encoding msg
if msg_alice == '00':
    circuit.i(0) # gate identity
elif msg_alice == '01':
    circuit.z(0) 
elif msg_alice == '10':
    circuit.x(0)
elif msg_alice == '11':
    circuit.x(0)
    circuit.z(0)
    
# decoding msg by bob
circuit.cx(0, 1)
circuit.h(0)

# mesure
circuit.measure([0,1], [0,1])
print(circuit.draw(output='text'))

# execution
job = simulator.run(transpile(circuit, simulator), shots=1)
result = job.result()

# counting
counts = result.get_counts(circuit)
print(f"number 00, 01, 10, 11 : {counts}")

v.plot_histogram(counts)
plt.show()