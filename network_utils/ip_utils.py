# -*- coding: utf-8 -*-
import socket
import logging

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
