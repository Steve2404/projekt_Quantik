from qiskit import QuantumCircuit
from qiskit.compiler import transpile
from qiskit_ibm_provider import IBMProvider
import qiskit_aer as qe
import numpy as np
from read_file import read_file

token = read_file("Quantum/projekt_Quantik/kommu/chat4/token.txt")
# token = read_file("kommu/chat4/token.txt")


def prepare_qubits(bits, bases, token):
    """Alice prepares the qubits"""
    IBMProvider.save_account(token, overwrite=True)

    
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

def checking(nb_bits, alice_basis, bob_basis, bits, bit_choice, choice_index=None):
    key = [bits[i] for i in range(nb_bits) if alice_basis[i] == bob_basis[i]]
    
    # Index selection management for the selection of verification bits
    if choice_index is None:
        if len(key) < bit_choice:
            raise ValueError("The number of bits to be selected is greater than the number of bits available.")
        choice_index = np.random.choice(len(key), bit_choice, replace=False)  # Random choice without replacement

    # Recovery of verification bits according to selected indices
    check_bits = [key[i] for i in choice_index]

    return choice_index, check_bits, key

    
def qber_key(expeditor_key, receiver_key, choice_index, key):
        # QBER_alice calculation
        errors = sum(
        expeditor_key[i] != receiver_key[i]
        for i in range(len(choice_index))
        )

        try:
            qber_key = errors / (len(expeditor_key))
        except ZeroDivisionError:
            print("Impossible : division by zero")

        if qber_key > 0.1:
            # return "Interception detected, give up the key !!!", qber_key
            return False, qber_key, None
        print("The key is secure, proceed to distillation of the key.")

        # expeditor and receiver exclude the verified bits from their final secret key
        final_key = [bit for i, bit in enumerate(key)if i not in choice_index]
        
        return True, qber_key, final_key
    
    
def calcul(qc):
        provider = IBMProvider()

        # Execution of the circuit
        simulator = provider.get_backend('simulator_mps')

        job = simulator.run(transpile(qc, simulator), shots=1, memory=True)
        job_id = job.job_id()
        retrieved_job = provider.retrieve_job(job_id)
        result = retrieved_job.result()
        measurements = result.get_memory()[0]

        # invert the bits of Bob
        bits = [int(measurements[i]) for i in range(len(measurements))]
        bits.reverse()
        return bits


if __name__ == '__main__':
    
    # simulation parameter
    nb_bits     = 20
    alice_bits  = np.random.randint(2, size=nb_bits)
    alice_basis = np.random.randint(2, size=nb_bits)
    bob_basis   = np.random.randint(2, size=nb_bits)
    eve_basis   = np.random.randint(2, size=nb_bits)

    # test manually
    #alice_bits  =  [0, 0, 0, 1, 1, 0, 1, 0]
    #alice_basis =  [1, 0, 0, 0, 1, 0, 0, 1]
    #bob_basis   =  [1, 0, 0, 0, 1, 0, 0, 1]



    # preparation qc
    qc = prepare_qubits(alice_bits, alice_basis, token)
    qc = intercept_measure(qc, eve_basis) # Eve interception
    qc = bob_measure(qc, bob_basis) # measure by Bob

    print(qc.draw())
    bob_bits = calcul(qc)
    print(f"bit de bob{bob_bits}")

    


    #simulation = qe.Aer.get_backend('qasm_simulator')
    #job = simulation.run(transpile(qc, simulation), shots=1, memory=True)
    #result = job.result()
    #measurements = result.get_memory()[0]
    # ******************** Alice Seite: ***************************
    
    print("********************** Alice Seite ********************************")
    choice_index_alice, check_bits_alice, alice_key= checking(nb_bits=nb_bits, alice_basis=alice_basis, bob_basis=bob_basis, bits=alice_bits, bit_choice=5)
    
    
    choice_index_bob, check_bits_bob, bob_key= checking(nb_bits=nb_bits, alice_basis=alice_basis, bob_basis=bob_basis, bits=bob_bits, bit_choice=5, choice_index=choice_index_alice)
    
    print(f"Alice key            : {alice_key}")
    print(f"Alice Basis          : {alice_basis}")
    print(f"BOB   Basis          : {bob_basis}")
    print(f"selected index Alice : {choice_index_alice}")
    print(f"Alice Check          : {check_bits_alice}")
    
    
    response_alice, qber_alice = qber_key(check_bits_alice, check_bits_bob, choice_index_alice, alice_key)
    
    print(f"QBER of Alice: {qber_alice}")
    print(response_alice)
    
    # ********************** BoB ********************************
    
    print("********************** Bob Seite ********************************")   
    print(f"bob key              : {bob_key}")
    print(f"BOB   Basis          : {bob_basis}")
    print(f"selected index Bob   : {choice_index_bob}")
    print(f"Bob Check            : {check_bits_bob}")
    
    response_bob, qber_bob = qber_key(check_bits_alice, check_bits_bob, choice_index_alice, bob_key)
    print(f"QBER of Bob          : {qber_bob}")
    print(response_bob)
    
    
    
    