import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad



def send(sock, msg_type, msg_content):
    message = f"{msg_type}:{msg_content}<END>"
    sock.sendall(message.encode())
    
    
##******************************************* EVE ********************************************************** 
def send_to_eve(data, msg_type, message):
    # Check if Eve is connected
    if 'Eve' in data and data['Eve']['conn']:
        eve_sock = data['Eve']['conn']
        try:
            send(eve_sock, msg_type, message)
        except Exception as e:
            print("Could not send message to Eve:", e)


##***************************************** Message *************************************************
def decode_message(data):
    action,_ , content = data.partition(b':')
    return action.decode(), content.decode()

def concatenate_data(data):
    return ",".join(map(str, data[:]))

def deconcatenate_data(data):
    return list(map(int, data.split(",")))


##********************************************** BB84 **************************************************
def decision(response):
    if response:
        return "The key is secure. We can continue the conversation."
    else:
        return "Interception detected, give up the key !!!"
    

def key_from_bits(bit_list):  
    """ Convertir une liste de bits en clé utilisable pour AES """
    bit_string = ''.join(str(bit) for bit in bit_list)
    key_raw = int(bit_string, 2).to_bytes((len(bit_string) + 7) // 8, byteorder='big')
    hash = SHA256.new()
    hash.update(key_raw)
    return hash.digest()[:16]  # Return the first 16 bytes for AES-128

##******************************** AES Protocol ******************************************
def encrypt_aes(plaintext, key):
    """ Chiffrer un message en utilisant AES """
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return base64.b64encode(iv + ciphertext).decode('utf-8')



def decrypt_aes(ciphertext_b64, key):
    """ Déchiffrer un message en utilisant AES """
    ciphertext = base64.b64decode(ciphertext_b64)
    
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext[AES.block_size:])
    plaintext = unpad(decrypted, AES.block_size)
    return plaintext.decode()


   

    



