# -*- coding: utf-8 -*-
import socket
import logging
from xml.etree import ElementTree as ET
import requests

def discover_ssdp():
    ssdp_request = (
        "M-SEARCH * HTTP/1.1\r\n"
        "HOST:239.255.255.250:1900\r\n"
        "MAN:\"ssdp:discover\"\r\n"
        "MX:2\r\n"
        "ST:upnp:rootdevice\r\n\r\n"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(20)
    sock.sendto(ssdp_request.encode('utf-8'), ('239.255.255.250', 1900))

    devices = []
    try:
        while True:
            response, addr = sock.recvfrom(1024)
            devices.append(parse_ssdp_response(response.decode('utf-8')))
    except socket.timeout:
        logging.info("Fin de la réception des réponses SSDP (timeout atteint).")
    return devices

def parse_ssdp_response(response):
    headers = {}
    lines = response.splitlines()
    for line in lines[1:]:
        parts = line.split(":", 1)
        if len(parts) == 2:
            headers[parts[0].strip()] = parts[1].strip()

    location = headers.get("LOCATION")
    if location:
        device_info = fetch_device_info(location)
        return {
            "ip": location.split("/")[2].split(":")[0],
            "location": location,
            "info": device_info
        }
    return {"ip": "Unknown", "location": "Unknown", "info": "Unknown"}

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
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur lors de la récupération des informations de l'appareil : {e}")
    except ET.ParseError as e:
        logging.error(f"Erreur de parsing XML : {e}")
    return "Unknown device"
