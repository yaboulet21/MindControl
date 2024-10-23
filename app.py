from flask import Flask, jsonify, request
from network_utils.ping_scan import scan_network  # Garde ton module réseau en place
from media_controls.multimedia_controls import control_media  # Importer la fonction de contrôle multimédia
import socket
import logging
import concurrent.futures  # Pour le multi-threading
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Ports les plus courants à scanner
common_ports = [80, 443, 22, 21, 8080, 139, 445, 3389, 25, 110]

# Variable globale pour stocker l'IP et le port sélectionnés
selected_ip = None
selected_port = None

# Scan limité des ports avec multi-threading
def scan_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((ip, port))
        sock.close()
        return port if result == 0 else None
    except Exception as e:
        logging.error(f"Erreur lors du scan du port {port} pour {ip}: {e}")
        return None

def scan_ports(ip, ports_to_scan=common_ports, limit=3):
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scan_port, ip, port): port for port in ports_to_scan}
        for future in concurrent.futures.as_completed(futures):
            port = futures[future]
            try:
                result = future.result()
                if result:
                    open_ports.append(result)
                if len(open_ports) >= limit:
                    break
            except Exception as e:
                logging.error(f"Erreur lors du traitement des résultats du port {port} : {e}")
    return open_ports

@app.route('/ping-scan', methods=['GET'])
def ping_scan():
    logging.info("Début du scan réseau.")
    try:
        active_ips = scan_network()  # Utilise ton module réseau
        results = []

        for device in active_ips:
            logging.info(f"Scan des ports pour l'IP : {device['ip']}")
            open_ports = scan_ports(device['ip'])
            logging.info(f"Ports ouverts pour {device['ip']} : {open_ports}")

            device_info = {
                "ip": device['ip'],
                "device_name": device.get('device_name', "Nom inconnu"),
                "open_ports": open_ports
            }
            results.append(device_info)

        return jsonify(results)
    except Exception as e:
        logging.error(f"Erreur lors du scan des adresses : {e}")
        return jsonify({"error": str(e)}), 500

# Route pour valider l'IP sélectionnée
@app.route('/validate-ip-port', methods=['POST'])
def validate_ip_port():
    global selected_ip, selected_port
    data = request.json
    selected_ip = data.get('ip')
    selected_port = data.get('port')

    # Log pour vérifier l'IP et le port reçus
    logging.info(f"IP reçue : {selected_ip}, Port reçu : {selected_port}")

    if selected_ip and selected_port:
        logging.info(f"Appareil cible : {selected_ip}:{selected_port}")
        return jsonify({"status": "success", "message": f"Connexion établie avec {selected_ip}:{selected_port}"})
    else:
        return jsonify({"status": "error", "message": "IP ou port non spécifiés."}), 400

# Nouvelle route pour exécuter les commandes multimédia
@app.route('/control', methods=['POST'])
def control():
    data = request.get_json()  # Récupère les données JSON envoyées
    command = data.get('command')  # Récupère la commande envoyée
    value = data.get('value')  # Récupère la valeur envoyée

    # Log pour vérifier les données reçues
    logging.info(f"Commande reçue : {command} avec la valeur : {value}")
    
    # Appelle la fonction control_media avec les paramètres reçus
    return control_media(command, value)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
