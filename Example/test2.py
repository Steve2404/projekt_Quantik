import random

def generate_key(length):
    return [random.choice([0, 1]) for _ in range(length)]

def choose_bases(length):
    return [random.choice(["Z", "X"]) for _ in range(length)]

def encode_bits(bits, bases):
    return [bit if base == "Z" else (bit + 1) % 2 for bit, base in zip(bits, bases)]

def measure_qubits(encoded_bits, bases):
    return [bit if base == "Z" else (bit + 1) % 2 for bit, base in zip(encoded_bits, bases)]

def compare_bases(bases1, bases2):
    return [i for i, (b1, b2) in enumerate(zip(bases1, bases2)) if b1 == b2]

def generate_shared_key(bits, indices):
    return [bits[i] for i in indices]

# Simulate BB84
message_length = 20

alice_bits = generate_key(message_length)
alice_bases = choose_bases(message_length)

bob_bases = choose_bases(message_length)
bob_bits = measure_qubits(alice_bits, bob_bases)

matching_bases_indices = compare_bases(alice_bases, bob_bases)
shared_key = generate_shared_key(alice_bits, matching_bases_indices)

print("Alice's bits:", alice_bits)
print("Bob's bits:", bob_bits)
print("Shared key:", shared_key)
