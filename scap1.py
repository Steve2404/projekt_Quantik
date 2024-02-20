from scapy.all import *

# Créer un paquet ICMP (ping) vers une adresse IP spécifique
packet = IP(dst="8.8.8.8")/ICMP()

# Envoyer le paquet et recevoir la réponse
response = sr1(packet, timeout=2)

# Afficher la réponse
if response:
    response.show()
else:
    print("Pas de réponse reçue.")
