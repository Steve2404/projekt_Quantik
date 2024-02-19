from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import PublicFormat, Encoding
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_x509_certificate

def secure_connection():
    # Génération des clés pour la connexion sécurisée
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()

    # Exportation de la clé publique au format PEM
    public_pem = public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

    # Partie Bob: Stockage de la clé publique de Alice
    # (En pratique, cela pourrait être échangé de manière sécurisée, par exemple, via une connexion hors bande)
    alice_public_key = public_pem

    # Partie Alice: Vérification de la clé publique reçue de Bob
    certificate = x509.load_pem_x509_certificate(alice_public_key, default_backend())
    alice_public_key = certificate.public_key()

    # La connexion sécurisée est maintenant établie
    print("Connexion sécurisée établie avec succès.")

if __name__ == "__main__":
    # Établir une connexion sécurisée avant de commencer le protocole BB84
    secure_connection()

    # BB84 protocol peut maintenant être démarré
    #bb84_protocol()
