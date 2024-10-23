import os
import platform
import socket
import logging
import concurrent.futures
import subprocess
from network_utils.ip_utils import get_subnet

# Fonction pour obtenir le nom du périphérique via DNS inversé
def get_device_name(ip):
    try:
        # Essaye de faire un reverse DNS lookup pour obtenir le nom de l'appareil
        name, _, _ = socket.gethostbyaddr(ip)
        return name
    except socket.herror:
        # Si le lookup échoue, retourne simplement l'IP
        return ip

# Fonction pour scanner les ports d'une IP donnée
def scan_ports(ip, start_port=1, end_port=1024):
    open_ports = []
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return open_ports

# Fonction pour pinger une IP et vérifier si elle répond
def ping_ip(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip]
    
    try:
        # Capture la sortie de la commande ping
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Vérifie la présence de la réponse dans la sortie
        if "TTL=" in result.stdout:  # Rechercher TTL pour déterminer une réponse réussie
            device_name = get_device_name(ip)  # Ajoute le reverse DNS lookup
            logging.info(f"Adresse IP active trouvée : {ip}, Nom de l'appareil : {device_name}")
            return {"ip": ip, "device_name": device_name}  # Retourne un dictionnaire avec l'IP et le nom de l'appareil
        else:
            logging.info(f"Aucune réponse de l'adresse IP : {ip}")
            return None
    except Exception as e:
        logging.error(f"Erreur lors du ping de l'adresse {ip}: {e}")
        return None

# Fonction pour scanner le réseau local avec un Ping Scan en parallèle
def scan_network():
    subnet = get_subnet()  # Utilisation du sous-réseau dynamique
    ips = [f"{subnet}{i}" for i in range(1, 255)]  # Crée une liste d'IPs à pinger

    # Utilisation d'un ThreadPoolExecutor pour paralléliser les appels de ping
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(ping_ip, ips)

    # Filtrer les résultats pour n'inclure que les adresses IP actives
    active_devices = [res for res in results if res]

    return active_devices
