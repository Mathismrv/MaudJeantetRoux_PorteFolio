import os
import json

# Configuration
IMAGE_FOLDER = 'image/illustrations'
JSON_FILE = 'illustrations.json'
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def scan_illustrations():
    # Vérifier si le dossier existe
    if not os.path.exists(IMAGE_FOLDER):
        print(f"Le dossier '{IMAGE_FOLDER}' n'existe pas. Création en cours...")
        os.makedirs(IMAGE_FOLDER)
        print("Dossier créé. Mettez vos images dedans et relancez ce script.")
        return

    # Lister les fichiers
    images = []
    # On trie la liste des fichiers par ordre alphabétique pour contrôler l'ordre d'affichage
    for filename in sorted(os.listdir(IMAGE_FOLDER)):
        ext = os.path.splitext(filename)[1].lower()
        if ext in EXTENSIONS:
            # On construit le chemin relatif pour le site web (avec des slashs /)
            path = f"{IMAGE_FOLDER}/{filename}"
            images.append(path)

    # Sauvegarder dans le JSON
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(images, f, indent=4)

    print(f"Succès ! {len(images)} illustrations trouvées et enregistrées dans {JSON_FILE}.")

if __name__ == "__main__":
    scan_illustrations()
