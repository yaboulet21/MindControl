from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
import subprocess
from pynput.keyboard import Key, Controller
import logging

keyboard = Controller()

def control_media(command, value=None, ip=None, port=None):
    try:
        # Ajout de logs pour voir la commande et la valeur reçues
        logging.info(f"Commande reçue : {command} avec la valeur : {value}")
        
        if command == "playpause":
            keyboard.press(Key.media_play_pause)
            keyboard.release(Key.media_play_pause)
            logging.info("Commande playpause exécutée.")
        
        elif command == "next":
            keyboard.press(Key.media_next)
            keyboard.release(Key.media_next)
            logging.info("Commande next exécutée.")
        
        elif command == "previous":
            keyboard.press(Key.media_previous)
            keyboard.release(Key.media_previous)
            logging.info("Commande previous exécutée.")
        
        elif command == "set_volume" and value is not None:
            # Initialiser COM
            CoInitialize()

            try:
                # Utilisation de pycaw pour régler directement le volume via l'API Windows
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = interface.QueryInterface(IAudioEndpointVolume)

                # Conversion de la valeur du slider en une valeur entre 0.0 et 1.0 pour pycaw
                volume_level_normalized = value / 100
                volume.SetMasterVolumeLevelScalar(volume_level_normalized, None)

                logging.info(f"Volume réglé à {value}%")
            finally:
                # Libérer COM
                CoUninitialize()
        
        elif command == "set_brightness" and value is not None:
            logging.info(f"Réglage de la luminosité à {value}")
            # Commande PowerShell pour ajuster la luminosité
            subprocess.run(["powershell", "-Command", f"(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {value})"])
        
        else:
            logging.error("Commande inconnue ou valeur manquante.")
            return {"status": "error", "message": "Commande inconnue ou valeur manquante."}
        
        logging.info(f"Commande {command} exécutée avec succès.")
        return {"status": "success", "message": f"Commande {command} exécutée avec succès."}
    
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution de la commande : {e}")
        return {"status": "error", "message": f"Erreur lors de l'exécution de la commande : {e}"}
