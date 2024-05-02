import numpy as np
import time
import socket
import base64
from bb84 import prepare_qubits
import hashlib
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
from qiskit import QuantumCircuit
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
    return ",".join(map(str, data[:]))

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
def received_msg(data, name, action, data_lock, key):
    global running
    while running: 
        with data_lock:
            if data[name][action] is not None and data[name]['other'] is not None:
                message = data[name][action]
                plaintext = decrypt_aes(message, key)
                print(f"(ack:{data[name]['other']}): {plaintext}")
                data[name][action] = None


       
def send_msg(sock, name, key):
    global running
    while running:
        msg_content = input(f"{name}:> ")
        cipher_sms = encrypt_aes(msg_content, key)
        if msg_content.lower() == "quit":
            send(sock, "DISCONNECT", name)
            running = False
        else:      
            send(sock, "MESSAGE", cipher_sms)

def print_info(name, O_name, basis, O_basis):
    print(f"{name} Basis is: {basis}")
    print(f"{O_name} Basis is: {O_basis}")




def generate_sha256_key(raw_key):
    binary_string = ''.join(str(bit) for bit in raw_key)
    hasher = hashlib.sha256()
    hasher.update(binary_string.encode('utf-8'))
    return hasher.hexdigest()[:16]

def test(sock, client_data, name, data_lock, attempt):                   
    
    send(sock, "DECIS", f"{attempt}")
    O_response = received(client_data, name, 'decis', data_lock)
    attempt = attempt == "y"
    O_response = O_response == "y"
    return O_response if O_response == attempt else not O_response



def prepare_key(bbinary_key, key_size=256):
    
    # Assurer que bbinary_key est une chaîne de caractères
    bbinary_key = str(bbinary_key)
    
    # Extension ou troncature de la clé à 256 bits
    if len(bbinary_key) < 256:
        bbinary_key = (bbinary_key * (256 // len(bbinary_key) + 1))[:256]
    else:
        bbinary_key = bbinary_key[:256]
    
    # Conversion de la chaîne binaire en bytes
    binary_key_bytes = bytes((int(bbinary_key[i:i+8], 2) for i in range(0, 256, 8)))
    
    # Hashage SHA-256 pour obtenir la clé finale
    sha256_hasher = hashlib.sha256()
    sha256_hasher.update(binary_key_bytes)
    final_key = sha256_hasher.digest()
    return final_key

def key_from_bits(bit_list):  
    """ Convertir une liste de bits en clé utilisable pour AES """
    bit_string = ''.join(str(bit) for bit in bit_list)
    key_raw = int(bit_string, 2).to_bytes((len(bit_string) + 7) // 8, byteorder='big')
    hash = SHA256.new()
    hash.update(key_raw)
    return hash.digest()[:16]  # Retourner les 16 premiers bytes pour AES-128


def encrypt_aes(plaintext, key):
    """ Chiffrer un message en utilisant AES """
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return iv + ciphertext

def decrypt_aes1(ciphertext, key):
    """ Déchiffrer un message en utilisant AES """
     # Convertir en bytes si nécessaire (par exemple si en base64 ou hexadécimal)
    if isinstance(ciphertext, str):
        ciphertext = base64.b64decode(ciphertext)
        
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext[AES.block_size:]), AES.block_size)
    return plaintext.decode()



def decrypt_aes(ciphertext, key):
    """ Déchiffrer un message en utilisant AES """
    try:
        ciphertext = base64.b64decode(ciphertext)
    except base64.binascii.Error as e:
        if padding_error := len(ciphertext) % 4:
            ciphertext += b'=' * (4 - padding_error)
        ciphertext = base64.b64decode(ciphertext)  # Réessayer le décodage

    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext[AES.block_size:])
    plaintext = unpad(decrypted, AES.block_size)
    return plaintext.decode()


#******************************* Bell State ***************************************************


# Simulating the creation of a Bell state
def create_bell_state(token):
    IBMProvider.save_account(token, overwrite=True)
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    return qc


# Measuring Bell's condition
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
    
    # Eve tries to intercept the qubit by measuring in a random base
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
   

    



