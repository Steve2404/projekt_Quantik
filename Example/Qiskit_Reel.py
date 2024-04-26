import qiskit as q 
import qiskit.visualization as v
from qiskit_ibm_provider import IBMProvider
import matplotlib.pyplot as plt
from qiskit.compiler import transpile

# code a donner une fois seulement, ensuite commenter la ligne
#IBMProvider.save_account('356c98ef861f7b5562320e3782b24ac7f0a7f2990b93038fb7e19a1a0ec422e0785152bb4ad77b0fdc6b7df3b977ff03ce6ec663b41e9b37429f064eb9d185bf', overwrite=True)

provider = IBMProvider()
#print(provider.backends()) # Affiche les ordinateurs disponibles

backend = provider.get_backend('simulator_mps') # choix d un ordinateur disponible

# construire un circuit
circuit = q.QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)

# circuit.measure(ligne qubit, ligne sortie)
circuit.measure([0, 1], [0, 1])

# execution
job = backend.run(transpile(circuits=circuit, backend=backend), shots=100)
job_id = job.job_id()


# attendre que le travail soit termine
retrieved_job = provider.retrieve_job(job_id)

result = retrieved_job.result()

# visualisation
counts = result.get_counts(circuit)
print(counts)

v.plot_histogram(counts)
plt.show()