import os
import pyautogui
import socket
import platform
import time
import logging
from flask import Flask, jsonify, send_from_directory
from xml.etree import ElementTree as ET
import requests

app = Flask(__name__)

# Configurer le niveau de log pour faciliter le débogage
logging.basicConfig(level=logging.DEBUG)

# Fonction pour détecter l'adresse IP locale de la machine
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connexion à une adresse externe sans envoyer de données réelles pour déterminer l'IP locale
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception as e:
        logging.error(f"Erreur lors de la récupération de l'IP locale : {e}")
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# Fonction pour extraire le sous-réseau à partir de l'IP locale
def get_subnet():
    ip = get_local_ip()
    subnet = '.'.join(ip.split('.')[:-1]) + '.'
    logging.info(f"Sous-réseau détecté : {subnet}")
    return subnet

# Fonction pour envoyer une requête SSDP et détecter les appareils compatibles UPnP
def discover_ssdp():
    ssdp_request = \
        "M-SEARCH * HTTP/1.1\r\n" \
        "HOST:239.255.255.250:1900\r\n" \
        "MAN:\"ssdp:discover\"\r\n" \
        "MX:2\r\n" \
        "ST:upnp:rootdevice\r\n" \
        "\r\n"

    # Créer une socket UDP pour envoyer les requêtes SSDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(20)
    sock.sendto(ssdp_request.encode('utf-8'), ('239.255.255.250', 1900))

    logging.info("Requête SSDP envoyée.")

    # Liste pour stocker les appareils trouvés
    devices = []

    try:
        while True:
            response, addr = sock.recvfrom(1024)
            logging.info(f"Réponse SSDP reçue de {addr}")
            devices.append(parse_ssdp_response(response.decode('utf-8')))
    except socket.timeout:
        logging.info("Fin de la réception des réponses SSDP (timeout atteint).")

    return devices

# Fonction pour analyser la réponse SSDP
def parse_ssdp_response(response):
    headers = {}
    lines = response.splitlines()
    for line in lines[1:]:
        parts = line.split(":", 1)
        if len(parts) == 2:
            headers[parts[0].strip()] = parts[1].strip()

    location = headers.get("LOCATION")
    logging.info(f"Appareil trouvé à {location}") if location else logging.info("Aucune localisation trouvée.")
    if location:
        device_info = fetch_device_info(location)
        return {
            "ip": location.split("/")[2].split(":")[0],
            "location": location,
            "info": device_info
        }
    return {"ip": "Unknown", "location": "Unknown", "info": "Unknown"}

# Fonction pour récupérer les informations de l'appareil à partir de son XML UPnP
def fetch_device_info(location):
    try:
        response = requests.get(location, timeout=5)
        tree = ET.fromstring(response.content)
        device = tree.find(".//{urn:schemas-upnp-org:device-1-0}device")
        if device is not None:
            return {
                "deviceType": device.findtext("{urn:schemas-upnp-org:device-1-0}deviceType"),
                "friendlyName": device.findtext("{urn:schemas-upnp-org:device-1-0}friendlyName"),
                "manufacturer": device.findtext("{urn:schemas-upnp-org:device-1-0}manufacturer"),
                "modelName": device.findtext("{urn:schemas-upnp-org:device-1-0}modelName")
            }
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des informations de l'appareil : {e}")
    return "Unknown device"

# Fonction pour pinger une IP
def ping_ip(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip]
    response = os.system(" ".join(command))
    return response == 0  # Retourne True si le ping est réussi

# Fonction pour scanner le réseau local avec un Ping Scan
def scan_network():
    active_ips = []
    subnet = get_subnet()  # Utilisation du sous-réseau dynamique
    for i in range(1, 255):  # Scanner les adresses de 1 à 254
        ip = f"{subnet}{i}"
        if ping_ip(ip):
            active_ips.append(ip)
            logging.info(f"Adresse IP active trouvée : {ip}")
        time.sleep(0.1)  # Pause légère pour éviter la saturation du réseau
    return active_ips

# Route pour découvrir les appareils via SSDP
@app.route('/ssdp', methods=['GET'])
def ssdp_discovery():
    devices = discover_ssdp()
    if devices:
        logging.info(f"{len(devices)} appareil(s) détecté(s).")
    else:
        logging.info("Aucun appareil détecté.")
    return jsonify(devices)

# Route pour découvrir les appareils via Ping Scan
@app.route('/ping-scan', methods=['GET'])
def ping_scan():
    active_ips = scan_network()
    return jsonify(active_ips)

# Route pour servir l'interface HTML
@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')

# Contrôle des commandes multimédia
@app.route('/control', methods=['POST'])
def control_media():
    command = request.json.get('command')
    if command == "playpause":
        pyautogui.press('playpause')
    elif command == "next":
        pyautogui.press('nexttrack')
    elif command == "previous":
        pyautogui.press('prevtrack')
    elif command == "brightness":
        value = request.json.get('value')
        os.system(f"powershell (Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {value})")
    elif command == "volume":
        value = request.json.get('value')
        os.system(f"D:\\Tech\\MindControl\\NirCmd\\nircmd.exe setsysvolume {int(value) * 65535 // 100}")
    else:
        return jsonify({"error": "Commande inconnue"}), 400

    return jsonify({"status": "Commande exécutée"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
