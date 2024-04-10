def create_message(msg_type, content):
    return f"{msg_type}:{len(content)}:{content}".encode()

def decode_message(data):
    parts = data.decode().split(':', 2)  # Split en 3 parties : type, longueur, contenu
    msg_type, content = parts[0], parts[2]
    return msg_type, content