import socket

# Exemple de ports communs à scanner (80, 443, 22)
ports_to_scan = [80, 443, 22, 8080, 21]

# Liste des IPs à scanner
ips_to_scan = ["192.168.1.1", "192.168.1.10"]

# Scan limité des ports
def scan_ports(ip):
    open_ports = []
    print(f"Début du scan des ports pour l'IP {ip}")
    for port in ports_to_scan:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Timeout réduit à 0.5 seconde
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except Exception as e:
            print(f"Erreur lors du scan du port {port} sur {ip}: {e}")
    return open_ports

# Test du scan sur plusieurs IPs
if __name__ == "__main__":
    for ip_to_scan in ips_to_scan:
        print(f"Scan des ports pour l'IP : {ip_to_scan}")
        open_ports = scan_ports(ip_to_scan)
        if open_ports:
            print(f"Ports ouverts sur {ip_to_scan} : {open_ports}")
        else:
            print(f"Aucun port ouvert trouvé sur {ip_to_scan}.")
