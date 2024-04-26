import numpy as np
import time
import socket
import base64
from bb84 import prepare_qubits
import hashlib
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from qiskit import QuantumCircuit, execute
import qiskit_aer as qe
from qiskit_ibm_provider import IBMProvider
from qiskit.compiler import transpile

def name_ask(instruction):
    name = input(instruction)
    while name.strip() == "":
        name = input("Please enter a valid name: ")
    return name


def send(sock, msg_type, msg_content):
    message = f"{msg_type}:{msg_content}".encode()
    sock.sendall(message)
    
    


##******************************************* EVE ********************************************************** 
def send_to_eve(data, msg_type, message):
    # Vérifiez si Eve est connectée
    if 'Eve' in data and data['Eve']['conn']:
        eve_sock = data['Eve']['conn']
        try:
            send(eve_sock, msg_type, message)
        except Exception as e:
            print("Could not send message to Eve:", e)

          
def receive(sock, timeout=15):
    sock.settimeout(timeout)
    try:
        data = sock.recv(4096).decode()
        _, content = decode_message(data.encode())
    
        return content
    except socket.timeout:
        print("Timeout waiting for response")
    except socket.error as e:
        print(f"Error receiving data: {e}")
    return None

def process_qc_eve(sock, content):
    send(sock, "QC", content)
    return new_content if (new_content := receive(sock)) else content  


##***************************************** Message *************************************************
def decode_message(data):
    action, _, content = data.partition(b":")
    return action.decode(), content.decode()

def concatenate_data(data):
    result = ",".join(map(str, data[:]))
    return result

def deconcatenate_data(data):
    return list(map(int, data.split(",")))

def read_file2(path):  
    with open(path, 'r') as file:
        content = file.read()  

    return content

##********************************************** BB84 **************************************************
def initiate_bb84(sock, name, nb_bits, token):
    
    basis, bits = generate_bb84_data(nb_bits)
    qc = prepare_qubits(bits, basis, token)
    print(qc.draw())
    qc_str = qc.qasm()
    qasm_circuit = base64.b64encode(qc_str.encode()).decode('utf-8')
    
    #send(sock, "name", name)
    send(sock, "QC", qasm_circuit)
    print(f"{name} has sent a QASM circuit.")

    
    send(sock, "BASIS", concatenate_data(basis))
    print(f"{name} has initiated BB84 with basis {concatenate_data(basis)} and bits {concatenate_data(bits)}.")
    return basis, bits

def generate_bb84_data(nb_bits=8):
    basis = np.random.randint(2, size=nb_bits).tolist()
    bits  = np.random.randint(2, size=nb_bits).tolist()
    return basis, bits

def decision(response):
    if response:
        return "The key is secure. We can continue the conversation."
    else:
        return "Interception detected, give up the key !!!"
    
def received(data, name, action, data_lock):
    while True: 
        time.sleep(2)
        with data_lock:
            if data[name][action] is not None and data[name]['other'] is not None:
                return data[name][action]
    

running = True
def received_msg(data, name, action, data_lock):
    global running
    while running: 
        with data_lock:
            if data[name][action] is not None and data[name]['other'] is not None:
                message = data[name][action]
                print(f"(ack:{data[name]['other']}): {message}")
                data[name][action] = None


       
def send_msg(sock, name):
    global running
    while running:
        msg_content = input(f"{name}:> ")
        if msg_content.lower() == "quit":
            send(sock, "DISCONNECT", name)
            running = False
        else:      
            send(sock, "MESSAGE", msg_content)

def print_info(name, O_name, basis, O_basis):
    print(f"{name} Basis is: {basis}")
    print(f"{O_name} Basis is: {O_basis}")




def generate_sha256_key(raw_key):
    binary_string = ''.join(str(bit) for bit in raw_key)
    hasher = hashlib.sha256()
    hasher.update(binary_string.encode('utf-8'))
    sha256_key = hasher.hexdigest()
    return sha256_key

def test(sock, client_data, name, data_lock, attempt):                   
    
    send(sock, "RESP", f"{attempt}")
    O_response = received(client_data, name, 'resp', data_lock)
    attempt = attempt == "y"
    O_response = O_response == "y"
    decision_final = O_response if O_response == attempt else not O_response
    
    return decision_final



def cipher_RSA(qc_key, data):  # sourcery skip: remove-unreachable-code
# Générez une clé RSA
    key = RSA.generate(2048)
    public_key = key.publickey()
    encryptor = PKCS1_OAEP.new(public_key)

    sha256_key = generate_sha256_key(qc_key)

    # Chiffrez la clé AES avec RSA
    encrypted_aes_key = encryptor.encrypt(sha256_key.encode('utf-8'))

    # Maintenant, vous pouvez utiliser aes_key pour chiffrer vos données avec AES
    aes_cipher = AES.new(sha256_key, AES.MODE_GCM)
    ciphertext, tag = aes_cipher.encrypt_and_digest(data)
    return ciphertext, tag





## Pour déchiffrer et vérifier les données
#try:
#    decryptor = AES.new(key, AES.MODE_GCM, nonce=cipher.nonce)
#    plaintext = decryptor.decrypt_and_verify(ciphertext, tag)
#    print("Le message est:", plaintext)
#except ValueError:
#    print("Clé incorrecte ou message corrompu.")




# Simuler la création d'un état de Bell
def create_bell_state(token):
    IBMProvider.save_account(token, overwrite=True)
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    return qc


# Mesurer l'état de Bell
def measure_bell_state(qc, alice_basis, bob_basis):
    provider = IBMProvider()
    simulator = provider.get_backend('simulator_mps')
    
    # Alice mesure dans sa base
    if alice_basis == 'X':
        qc.h(0)  
    qc.measure(0, 0)
    
    # Bob mesure dans sa base
    if bob_basis == 'X':
        qc.h(1)  
    qc.measure(1, 1)
    
    
    job = simulator.run(transpile(qc, simulator), shots=1, memory=True)
    job_id = job.job_id()
    retrieved_job = provider.retrieve_job(job_id)
    result = retrieved_job.result()
    measurements = result.get_memory()[0]
    bits = [int(measurements[i]) for i in range(len(measurements))]
    bits.reverse()
    print(f"Le Resultat Alice et Bob: {bits}")
    return bits

def send_bell_state(sock, token):
    qc = create_bell_state(token)

    client_bits = measure_bell_state(qc, measure_first=True)
    other_bits = measure_bell_state(qc, measure_first=False)
    send(sock, "BELL", client_bits)
    send(sock, "BELL", other_bits)
    

def eve_interception(qc, qubit_index):
    provider = IBMProvider()
    simulator = provider.get_backend('simulator_mps')
    
    # Eve essaie d'intercepter le qubit en mesurant dans une base aléatoire
    eve_basis = 'X' if np.random.random() < 0.5 else 'Z'
    
    
    if eve_basis == 'X':
        qc.h(qubit_index)
    qc.measure(qubit_index, qubit_index)
   
    job = simulator.run(transpile(qc, simulator), shots=1, memory=True)
    job_id = job.job_id()
    retrieved_job = provider.retrieve_job(job_id)
    result = retrieved_job.result()
    measurements = result.get_memory()[0]
    bits = [int(measurements[i]) for i in range(len(measurements))]
    bits.reverse()
    return bits
   





    
    

# Chiffrer un message en utilisant one-time pad
def encrypt_message(message, key):
    return ''.join(str(int(message_bit) ^ int(key_bit)) for message_bit, key_bit in zip(message, key))

# Déchiffrer un message
def decrypt_message(encrypted_message, key):
    return encrypt_message(encrypted_message, key)  # La même fonction peut être utilisée pour chiffrer et déchiffrer

