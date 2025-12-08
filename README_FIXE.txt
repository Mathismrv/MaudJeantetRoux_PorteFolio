INSTRUCTIONS POUR LE SITE FIXE

Le site est maintenant statique (sans base de données ni Flask).

POUR AJOUTER UN PROJET :
1. Créez un dossier dans "image/" avec le nom du projet (ex: "mon_projet").
2. Dans ce dossier, ajoutez :
   - Une image de couverture (ex: "cover.jpg").
   - Un fichier texte nommé "description.txt" contenant la description du projet.
   - Vos autres photos (ex: "photo1.jpg", "photo2.jpg").
3. Ouvrez le fichier "projects.json" à la racine du site.
4. Ajoutez un bloc pour le nouveau projet en suivant le modèle :
   {
       "id": "mon_projet",
       "title": "Titre du Projet",
       "folder": "mon_projet",
       "cover": "cover.jpg",
       "images": ["photo1.jpg", "photo2.jpg"],
       "youtube_id": "ID_VIDEO_YOUTUBE" 
   }
   (Laissez "youtube_id" vide "" s'il n'y a pas de vidéo).

POUR AJOUTER UNE ILLUSTRATION :
1. Ajoutez l'image dans le dossier "image/".
2. Ouvrez "illustrations.json".
3. Ajoutez le chemin de l'image dans la liste (ex: "image/nouvelle_illustration.jpg").

POUR LANCER LE SITE :
Il suffit d'ouvrir "index.html" dans votre navigateur.
Note : Pour que le chargement des fichiers JSON fonctionne correctement en local (CORS policy), il est préférable d'utiliser un petit serveur local (ex: extension "Live Server" sur VS Code) plutôt que d'ouvrir directement le fichier.
