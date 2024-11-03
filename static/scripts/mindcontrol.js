// Variables globales pour l'IP et le port sélectionnés
let selectedIP = null;
let selectedPort = null;

// Fonction pour scanner les adresses IP actives via Ping
function pingScan() {
    console.log("Début du scan des adresses IP...");

    fetch('/api/ping-scan')  // Mise à jour de l'URL de l'API
        .then(response => response.json())
        .then(data => {
            console.log("Données reçues du scan réseau :", data);
            displayIPList(data);
        })
        .catch(error => console.error('Erreur lors du scan réseau :', error));
}

// Fonction pour afficher la liste des IPs et des ports dans le HTML
function displayIPList(data) {
    const ipListDiv = document.getElementById('ip-list');
    ipListDiv.innerHTML = '';  // Vide la liste précédente

    if (data.length === 0) {
        ipListDiv.innerHTML = '<p>Aucune adresse IP détectée</p>';
        return;
    }

    document.getElementById('debug-log').innerHTML = `Nombre d'IP détectées : ${data.length}`;

    data.forEach(device => {
        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.value = device.ip;
        radio.name = 'ip';
        radio.onclick = () => selectIP(device.ip, device.open_ports);

        const label = document.createElement('label');
        label.textContent = `${device.ip} - ${device.device_name}`;

        ipListDiv.appendChild(radio);
        ipListDiv.appendChild(label);
        ipListDiv.appendChild(document.createElement('br'));
    });
}

// Fonction pour sélectionner une IP et afficher les ports ouverts associés
function selectIP(ip, open_ports) {
    selectedIP = ip;
    selectedPort = null;  // Reset du port sélectionné
    console.log(`IP sélectionnée : ${selectedIP}, Ports disponibles : ${open_ports}`);

    const portListDiv = document.getElementById('port-list');
    portListDiv.innerHTML = '';  // Effacer la liste précédente

    open_ports.forEach(port => {
        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.value = port;
        radio.name = 'port';
        radio.onclick = () => selectedPort = port;
        
        const label = document.createElement('label');
        label.textContent = `Port : ${port}`;
        portListDiv.appendChild(radio);
        portListDiv.appendChild(label);
        portListDiv.appendChild(document.createElement('br'));
    });
    document.getElementById('port-selection').style.display = 'block';
}

// Fonction pour valider la sélection d'IP et de port
function validatePortSelection() {
    if (selectedIP && selectedPort) {
        console.log(`Validation de l'IP ${selectedIP} avec le port ${selectedPort}`);

        fetch('/validate-ip-port', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ip: selectedIP, port: selectedPort })
        })
        .then(response => response.json())
        .then(data => {
            alert(`Connexion établie avec l'appareil ${selectedIP}:${selectedPort}`);
        })
        .catch(error => console.error('Erreur lors de la validation de l\'IP et du port:', error));
    } else {
        alert("Veuillez sélectionner un port.");
    }
}

// Fonction pour envoyer une commande de contrôle multimédia
function sendMediaCommand(command) {
    if (!selectedIP || !selectedPort) {
        alert("Veuillez sélectionner un appareil et un port avant d'envoyer une commande.");
        return;
    }

    fetch('/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            command: command,
            ip: selectedIP,
            port: selectedPort
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'error') {
            console.error(data.message);
        } else {
            console.log(data.message);
        }
    })
    .catch(error => console.error('Erreur lors de l\'envoi de la commande multimédia:', error));
}

// Fonction pour régler la luminosité en temps réel
document.getElementById('brightness-slider').addEventListener('input', function() {
    const value = this.value;
    fetch('/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'set_brightness', value: value })  // Correction ici
    })
    .then(response => response.json())
    .then(data => console.log('Réglage de la luminosité appliqué:', data))
    .catch(error => console.error('Erreur lors du réglage de la luminosité:', error));
});

// Fonction pour régler le volume en temps réel
document.getElementById('volume-slider').addEventListener('input', function() {
    const value = this.value;
    fetch('/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'set_volume', value: value })  // Correction ici
    })
    .then(response => response.json())
    .then(data => console.log('Réglage du volume appliqué:', data))
    .catch(error => console.error('Erreur lors du réglage du volume:', error));
});

// Ajout d'événements sur les boutons
document.getElementById('ping-scan-btn').addEventListener('click', pingScan);
document.getElementById('validate-btn').addEventListener('click', validatePortSelection);
