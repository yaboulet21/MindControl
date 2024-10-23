# -*- coding: utf-8 -*-
import os
import logging

# Configurer les logs pour afficher les informations sur la console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def remove_null_bytes(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
    
    # Vérifier s'il y a des bytes nulls
    if b'\x00' in data:
        logging.info(f"Bytes nulls détectés dans le fichier : {file_path}")
        # Supprimer les bytes nulls
        cleaned_data = data.replace(b'\x00', b'')
        with open(file_path, 'wb') as file:
            file.write(cleaned_data)
        logging.info(f"Bytes nulls supprimés du fichier : {file_path}")
    else:
        logging.info(f"Aucun byte null trouvé dans le fichier : {file_path}")

# Chemin vers le dossier où se trouvent tes fichiers
project_dir = "D:/tech/mindcontrol"

# Parcours récursif des fichiers dans le dossier
for root, dirs, files in os.walk(project_dir):
    for file in files:
        if file.endswith(".py"):  # On ne nettoie que les fichiers Python
            file_path = os.path.join(root, file)
            logging.info(f"Nettoyage du fichier : {file_path}")
            remove_null_bytes(file_path)
