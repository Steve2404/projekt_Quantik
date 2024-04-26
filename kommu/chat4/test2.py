


def register_client(data, name, content):
    if name not in data:
        data[name] = {
            "basis": None,
            "bit": None,
            "QC": None,
            "index": None,
            "check_bits": None,
            "resp": None,
            "msg": None,
            "other": None,
            "error2": None,
            "error": None,
            "ack": content,
            "ack2": None,
            "role": None,
        }

def process_message(data, name, content):
    message = content.split(":>")[1]
    if name:
        data[name]["msg"] = message

def process_other(data, name, content):
    data[name]["other"] = content

def process_error2(data, name, content):
    data[name]["error2"] = content

def process_error(data, name, content):
    data[name]["error"] = content
    
def process_ack(data, name, content):
    data[name]["ack"] = content
    
def process_ack2(data, name, content):
    data[name]["ack2"] = content
    
def process_role(data, name, content):
    data[name]["role"] = content
    
def process_qc(data, name, content):
    data[name]["QC"] = content
    
def process_basis(data, name, content):
    data[name]["basis"] = content
    
def process_index(data, name, content):
    data[name]["index"] = content

def process_check_bits(data, name, content):
    data[name]["check_bits"] = content

def process_resp(data, name, content):
    data[name]["resp"] = content
 
def process_bit(data, name, content):
    data[name]["bit"] = content


actions = {
    "REGISTER": register_client,
    "MESSAGE": process_message,
    "OTHER": process_other,
    "ERROR2": process_error2,
    "ERROR": process_error,
    "ACK": process_ack,
    "ACK2": process_ack2,
    "ROLE": process_role,
    "QC": process_qc,
    "basis": process_basis,
    "index": process_index,
    "check_bits": process_check_bits,
    "resp": process_resp,
    "bit": process_bit
     
}








