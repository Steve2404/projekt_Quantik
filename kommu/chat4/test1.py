from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
import os

def key_from_bits(bit_list):
    """ Convertir une liste de bits en clé utilisable pour AES """
    bit_string = ''.join(str(bit) for bit in bit_list)
    key_raw = int(bit_string, 2).to_bytes((len(bit_string) + 7) // 8, byteorder='big')
    hash = SHA256.new()
    hash.update(key_raw)
    return hash.digest()[:16]  # Retourner les 16 premiers bytes pour AES-128

def encrypt(message, key):
    """ Chiffrer un message en utilisant AES """
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    return iv + ciphertext

def decrypt(ciphertext, key):
    """ Déchiffrer un message en utilisant AES """
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext[AES.block_size:]), AES.block_size)
    return plaintext.decode()

# Exemple d'utilisation
bit_list = [0, 1, 1, 1]  # Exemple de clé générée par BB84
key = key_from_bits(bit_list)
print(f"La cle est: {key}")

message = "Hello, Quantum World!"
ciphertext = encrypt(message, key)
print("Ciphertext:", ciphertext)

decrypted_message = decrypt(ciphertext, key)
print("Decrypted message:", decrypted_message)
