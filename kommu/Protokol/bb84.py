from qiskit import QuantumCircuit
from qiskit.compiler import transpile
from qiskit_ibm_provider import IBMProvider
import qiskit_aer as qe
import numpy as np

def prepare_qubits(bits, bases):
    """Alice prepares the qubits"""
    IBMProvider.save_account('356c98ef861f7b5562320e3782b24ac7f0a7f2990b93038fb7e19a1a0ec422e0785152bb4ad77b0fdc6b7df3b977ff03ce6ec663b41e9b37429f064eb9d185bf', overwrite=True)

    
    qc = QuantumCircuit(len(bits), len(bases))
    for i in range(len(bits)): 
        if bits[i] == 1: # Apply Gate X if the bit is 1 to put it in the state |1>
            qc.x(i)
        if bases[i] == 1: # Diagonale Basis
            qc.h(i)
    
    qc.barrier()
    return qc

def intercept_measure(qc, bases):
    """Eve intercepts and measures the qubits"""
    for i in range(len(bases)):
        if bases[i] == 1: # Eve chooses a basis
            qc.h(i)
        # qc.measure(i, i) # Eve measure the qubit
        
    qc.barrier()
    return qc

def bob_measure(qc, bases):
    """Bob measures the qubits"""
    for i in range(len(bases)):
        if bases[i] == 1: # Diagonal basis chosen by Bob
            qc.h(i)
    qc.barrier() # end for this line
    
    for i in range(len(bases)):
        qc.measure(i, i)
    

    return qc


if __name__ == '__main__':
    
    # simulation parameter
    nb_bits     = 8
    #alice_bits  = np.random.randint(2, size=nb_bits)
    #alice_basis = np.random.randint(2, size=nb_bits)
    #bob_basis   = np.random.randint(2, size=nb_bits)
    eve_basis   = np.random.randint(2, size=nb_bits)
    
    # test manually
    alice_bits  =  [0, 0, 0, 1, 1, 0, 1, 0]
    alice_basis =  [1, 0, 0, 0, 1, 0, 0, 1]
    bob_basis   =  [0, 1, 0, 0, 1, 0, 0, 1]
    


    # preparation qc
    qc = prepare_qubits(alice_bits, alice_basis)
    #qc = intercept_measure(qc, eve_basis) # Eve interception
    qc = bob_measure(qc, bob_basis) # measure by Bob

    print(qc.draw())

    provider = IBMProvider()

    # Execution of the circuit
    simulator = provider.get_backend('simulator_mps')

    job = simulator.run(transpile(qc, simulator), shots=1, memory=True)
    job_id = job.job_id()
    retrieved_job = provider.retrieve_job(job_id)
    result = retrieved_job.result()
    measurements = result.get_memory()[0]
    
    # invert the bits of Bob
    bob_bits = [int(measurements[i]) for i in range(len(measurements))]
    bob_bits.reverse()


    #simulation = qe.Aer.get_backend('qasm_simulator')
    #job = simulation.run(transpile(qc, simulation), shots=1, memory=True)
    #result = job.result()
    #measurements = result.get_memory()[0]

    key_alice_bob = [
        bob_bits[i]
        for i in range(nb_bits)
        if alice_basis[i] == bob_basis[i]
    ]
    print(f"Cle between the Alice-Bob: {key_alice_bob}\nThe length: {len(key_alice_bob)}")
    print(f"bob bit                  : {bob_bits}")
    print(f"alice bit                : {alice_bits}") 

    # Estimation of QBER (simplified here for the example)

    x_bits_to_check = 3
    matching_indices = [i for i in range(nb_bits) if alice_basis[i] == bob_basis[i]]
    check_indices = np.random.choice(matching_indices, x_bits_to_check, replace=False)

    print(f"matching_indices: {matching_indices}")
    print(f"Alice Basis     : {alice_basis}")
    print(f"BOB   Basis     : {bob_basis}")
    print(f"selected index  : {check_indices}")

    alice_check_bits = [
        alice_bits[i] 
        for i in check_indices 
        if alice_basis[i] == bob_basis[i]
    ]

    bob_check_bits = [
        bob_bits[i]
        for i in check_indices
        if alice_basis[i] == bob_basis[i]
    ]

    # Addition of an error checking step 

    # QBER calculation
    errors = sum(
        alice_check_bits[i] != bob_check_bits[i]
        for i in range(len(alice_check_bits))
    )
    print(f"number of errors      : {errors}")
    print(f"number of bits to test: {len(alice_check_bits)}")
    
    try:
        qber = errors / (len(alice_check_bits))
    except ZeroDivisionError:
        print("Impossible : division by zero")


    print(f"Alice's bit for verification: {alice_check_bits}")
    print(f"Bob's bit for verification  : {bob_check_bits}")

    print(f"QBER: {qber}")

    # Decision based on QBER
    if qber > 0.2: # Hypothetical QBER tolerance limit
        print("Interception detected, give up the key !!!")
    else:
        print("The key is secure, proceed to distillation of the key.")

    # Alice and Bob exclude the verified bits from their final secret key
    final_key = [bit 
                 for i, bit in enumerate(key_alice_bob)
                 if i not in check_indices]

    print(f"Final shared key: {final_key}")