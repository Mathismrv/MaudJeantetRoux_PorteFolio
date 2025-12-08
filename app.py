from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import cloudinary
import cloudinary.uploader
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

app = Flask(__name__, template_folder='.', static_folder='.')

# Configuration de la durée de la session (ex: 1 heure)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# Configuration Base de données
# Utilise SQLite par défaut, ou la variable DATABASE_URL si elle existe (pour Render)
database_url = os.getenv('DATABASE_URL', 'sqlite:///site.db')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'votre_cle_secrete_a_changer')

db = SQLAlchemy(app)

# Configuration Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configuration Cloudinary
cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key = os.getenv('CLOUDINARY_API_KEY'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
)

# --- Modèles Base de données ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(300), nullable=False) # Image de couverture
    order = db.Column(db.Integer, default=0)
    medias = db.relationship('ProjectMedia', backref='project', lazy=True, cascade="all, delete-orphan", order_by="ProjectMedia.order")

class ProjectMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    url = db.Column(db.String(300), nullable=False)
    media_type = db.Column(db.String(20), nullable=False) # 'image' or 'video'
    order = db.Column(db.Integer, default=0)

class Illustration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(300), nullable=False)
    order = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes Publiques ---

@app.route('/')
@app.route('/home.html')
def home():
    return render_template('home.html')

@app.route('/projets.html')
def projets():
    # Récupérer tous les projets de la base de données, triés par ordre
    projects = Project.query.order_by(Project.order.asc()).all()
    return render_template('projets.html', projects=projects)

@app.route('/illustrations.html')
def illustrations():
    # Récupérer toutes les illustrations, triées par ordre
    illustrations = Illustration.query.order_by(Illustration.order.asc()).all()
    return render_template('illustrations.html', illustrations=illustrations)

@app.route('/<path:filename>')
def serve_static(filename):
    # Servir les fichiers statiques (css, images locales, pdf)
    if filename in ['home.html', 'projets.html', 'illustrations.html']:
        # Ces pages sont maintenant gérées par des routes spécifiques
        return redirect(url_for(filename.replace('.html', '')))
    
    if os.path.exists(filename):
        return send_from_directory('.', filename)
    return "Fichier non trouvé", 404

# --- Routes Admin ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # remember=True garde la session active même après fermeture du navigateur
            # La durée est définie par PERMANENT_SESSION_LIFETIME (ici 1h)
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants invalides')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    projects = Project.query.order_by(Project.order.asc()).all()
    illustrations = Illustration.query.order_by(Illustration.order.asc()).all()
    return render_template('dashboard.html', projects=projects, illustrations=illustrations)

@app.route('/add_project', methods=['POST'])
@login_required
def add_project():
    title = request.form.get('title')
    description = request.form.get('description')
    files = request.files.getlist('image') # Récupérer plusieurs fichiers

    if files:
        # Créer le projet d'abord
        new_project = Project(title=title, description=description, image_url="")
        db.session.add(new_project)
        db.session.commit()

        first_image_set = False

        for i, file in enumerate(files):
            if file and file.filename != '':
                try:
                    # resource_type="auto" permet à Cloudinary de détecter si c'est une image ou une vidéo
                    # Pour les vidéos > 10Mo, il vaut mieux spécifier resource_type='video' si on est sûr
                    # Mais 'auto' est le plus flexible.
                    upload_result = cloudinary.uploader.upload(file, resource_type="auto")
                    url = upload_result['secure_url']
                    media_type = 'video' if 'video' in upload_result['resource_type'] else 'image'
                    
                    # La première image devient l'image de couverture du projet
                    if not first_image_set:
                        new_project.image_url = url
                        first_image_set = True
                    
                    # Ajouter au modèle ProjectMedia
                    media = ProjectMedia(project_id=new_project.id, url=url, media_type=media_type, order=i)
                    db.session.add(media)
                except cloudinary.exceptions.Error as e:
                    print(f"Erreur upload Cloudinary: {e}")
                    flash(f"Erreur lors de l'upload de {file.filename} : {str(e)}. (Limite: 10Mo images, 100Mo vidéos)")
                    # On continue avec les autres fichiers ou on arrête ? 
                    # Pour l'instant on continue mais ce fichier ne sera pas ajouté.
        
        db.session.commit()
    
    return redirect(url_for('dashboard'))

@app.route('/update_project_order', methods=['POST'])
@login_required
def update_project_order():
    # Met à jour l'ordre des projets
    for key, value in request.form.items():
        if key.startswith('order_'):
            project_id = int(key.split('_')[1])
            project = Project.query.get(project_id)
            if project:
                project.order = int(value)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/update_illustration_order', methods=['POST'])
@login_required
def update_illustration_order():
    # Met à jour l'ordre des illustrations
    for key, value in request.form.items():
        if key.startswith('order_'):
            ill_id = int(key.split('_')[1])
            illustration = Illustration.query.get(ill_id)
            if illustration:
                illustration.order = int(value)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/reset_db_schema')
@login_required
def reset_db_schema():
    # Route pour mettre à jour la structure de la base de données si nécessaire
    db.drop_all()
    db.create_all()
    
    # Recréer l'admin
    if not User.query.filter_by(username='Mjr444').first():
        admin = User(username='Mjr444')
        admin.set_password('Gatam!04')
        db.session.add(admin)
        db.session.commit()
        
    return "Base de données réinitialisée (Tables recréées avec succès)."

@app.route('/edit_project/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        
        # Update existing media orders and handle deletions
        for key, value in request.form.items():
            if key.startswith('media_order_'):
                media_id = int(key.split('_')[2])
                media = ProjectMedia.query.get(media_id)
                if media and media.project_id == project.id:
                    media.order = int(value)
            
            if key.startswith('delete_media_'):
                media_id = int(key.split('_')[2])
                media = ProjectMedia.query.get(media_id)
                if media and media.project_id == project.id:
                    db.session.delete(media)
        
        # Add new medias
        files = request.files.getlist('new_images')
        if files:
            # Find current max order to append new items at the end
            current_max_order = 0
            if project.medias:
                current_max_order = max(m.order for m in project.medias)
            
            for i, file in enumerate(files):
                if file and file.filename != '':
                    try:
                        upload_result = cloudinary.uploader.upload(file, resource_type="auto")
                        url = upload_result['secure_url']
                        media_type = 'video' if 'video' in upload_result['resource_type'] else 'image'
                        
                        media = ProjectMedia(project_id=project.id, url=url, media_type=media_type, order=current_max_order + 1 + i)
                        db.session.add(media)
                    except cloudinary.exceptions.Error as e:
                        print(f"Erreur upload Cloudinary: {e}")
                        flash(f"Erreur lors de l'upload de {file.filename} : {str(e)}")
        
        db.session.commit()
        
        # Update project cover image to be the first media in order
        # Refresh project medias
        db.session.refresh(project)
        if project.medias:
            # Sort by order
            sorted_medias = sorted(project.medias, key=lambda x: x.order)
            project.image_url = sorted_medias[0].url
        elif not project.medias:
             # If no media left, maybe set a placeholder or leave empty?
             pass
             
        db.session.commit()
            
        return redirect(url_for('dashboard'))
        
    return render_template('edit_project.html', project=project)

@app.route('/delete_project/<int:id>')
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_illustration', methods=['POST'])
@login_required
def add_illustration():
    try:
        images = request.files.getlist('images')
        
        if not images or not images[0].filename:
            flash('Aucune image sélectionnée')
            return redirect(url_for('dashboard'))

        # Trouver l'ordre maximum actuel pour ajouter les nouvelles à la suite
        max_order = db.session.query(db.func.max(Illustration.order)).scalar() or 0

        count = 0
        for i, image in enumerate(images):
            if image and image.filename:
                upload_result = cloudinary.uploader.upload(image)
                image_url = upload_result['secure_url']
                
                # Assigner un ordre incrémental
                new_illustration = Illustration(image_url=image_url, order=max_order + 1 + i)
                db.session.add(new_illustration)
                count += 1
        
        db.session.commit()
        flash(f'{count} illustration(s) ajoutée(s) avec succès !')
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur upload: {e}")
        flash(f"Erreur lors de l'upload : {str(e)}")
    
    return redirect(url_for('dashboard'))

@app.route('/delete_illustration/<int:id>')
@login_required
def delete_illustration(id):
    illustration = Illustration.query.get_or_404(id)
    db.session.delete(illustration)
    db.session.commit()
    return redirect(url_for('dashboard'))

# --- Initialisation ---

def init_db():
    with app.app_context():
        db.create_all()
        
        # Supprimer l'ancien compte 'admin' s'il existe encore
        old_admin = User.query.filter_by(username='admin').first()
        if old_admin:
            db.session.delete(old_admin)
            db.session.commit()
            print("Ancien compte 'admin' supprimé.")

        # Créer un admin par défaut si aucun n'existe
        if not User.query.filter_by(username='Mjr444').first():
            admin = User(username='Mjr444')
            admin.set_password('Gatam!04') # Mot de passe par défaut à changer !
            db.session.add(admin)
            db.session.commit()
            print("Admin user created (Mjr444/Gatam!04)")

# Initialisation de la base de données au démarrage (pour Gunicorn/Render)
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)