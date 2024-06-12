import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
import sqlite3



def send(sock, msg_type, msg_content):
    message = f"{msg_type}:{msg_content}<END>"
    sock.sendall(message.encode())
    
    
##***************************** EVE ******************************************
def send_to_eve(data, msg_type, message):
    # Check if Eve is connected
    if 'Eve' in data and data['Eve']['conn']:
        eve_sock = data['Eve']['conn']
        try:
            send(eve_sock, msg_type, message)
        except Exception as e:
            print("Could not send message to Eve:", e)


##**************************** Message ***************************************
def decode_message(data):
    action,_ , content = data.partition(b':')
    return action.decode(), content.decode()

def concatenate_data(data):
    return ",".join(map(str, data[:]))

def deconcatenate_data(data):
    return list(map(int, data.split(",")))


##*************************** BB84 *******************************************
def decision(response):
    if response:
        return "The key is secure. We can continue the conversation."
    else:
        return "Interception detected, give up the key !!!"
    

def key_from_bits(bit_list):  
    """Convert a list of bits into a key usable for AES"""
    bit_string = ''.join(str(bit) for bit in bit_list)
    key_raw = int(bit_string, 2).to_bytes(
        (len(bit_string) + 7) // 8, byteorder='big')
    hash = SHA256.new()
    hash.update(key_raw)
    return hash.digest()[:16]  # Return the first 16 bytes for AES-128

##********************** AES Protocol ****************************************
def encrypt_aes(plaintext, key):
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return base64.b64encode(iv + ciphertext).decode('utf-8')



def decrypt_aes(ciphertext_b64, key):
    ciphertext = base64.b64decode(ciphertext_b64)
    
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext[AES.block_size:])
    plaintext = unpad(decrypted, AES.block_size)
    return plaintext.decode()

# ****************************** DB ******************************************
def init_db():
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            key TEXT NOT NULL,
            UNIQUE(sender, receiver)
        )
    ''')
    conn.commit()
    conn.close()

def store_key(sender, receiver, key):
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO keys (sender, receiver, key) 
            VALUES (?, ?, ?)
        ''', (sender, receiver, key))
        conn.commit()
    except sqlite3.IntegrityError:
        cursor.execute('''
            UPDATE keys 
            SET key = ? 
            WHERE sender = ? AND receiver = ?
        ''', (key, sender, receiver))
        conn.commit()
    finally:
        conn.close()
        
def get_key(sender, receiver):
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT key FROM keys 
        WHERE sender = ? AND receiver = ?
    ''', (sender, receiver))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None



   

    



