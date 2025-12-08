import os
import json

# Configuration
ILLUSTRATIONS_FOLDER = 'image/illustrations'
ILLUSTRATIONS_JSON = 'illustrations.json'

PORTFOLIO_FOLDER = 'image/portfolio'
PORTFOLIO_JSON = 'portfolio.json'

EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def scan_folder(folder_path, json_path):
    # Vérifier si le dossier existe
    if not os.path.exists(folder_path):
        print(f"Le dossier '{folder_path}' n'existe pas. Création en cours...")
        os.makedirs(folder_path)
        print(f"Dossier '{folder_path}' créé.")
        return

    # Lister les fichiers
    images = []
    # On trie la liste des fichiers par ordre alphabétique
    for filename in sorted(os.listdir(folder_path)):
        ext = os.path.splitext(filename)[1].lower()
        if ext in EXTENSIONS:
            # On construit le chemin relatif pour le site web
            path = f"{folder_path}/{filename}"
            images.append(path)

    # Sauvegarder dans le JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(images, f, indent=4)

    print(f"Succès ! {len(images)} images trouvées dans '{folder_path}' et enregistrées dans '{json_path}'.")

def main():
    print("--- Scan des Illustrations ---")
    scan_folder(ILLUSTRATIONS_FOLDER, ILLUSTRATIONS_JSON)
    
    print("\n--- Scan du Portfolio ---")
    scan_folder(PORTFOLIO_FOLDER, PORTFOLIO_JSON)

if __name__ == "__main__":
    main()
