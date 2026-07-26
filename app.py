import os
import re
import sqlite3
import smtplib
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")
DATABASE = BASE_DIR / "database" / "portfolio.db"

PROFILE = {"initials": "BM", "name": "Bilal Ahmat Mahamat", "role": "Développeur web full-stack", "headline": "Développeur web full-stack", "intro": "Je transforme les idées ambitieuses en produits web rapides, clairs et agréables à utiliser.", "bio": "Je m'appelle Bilal Ahmat Mahamat, étudiant en deuxième année en génie logiciel et systèmes d'information à la Faculté des sciences de Gabès, en Tunisie. Je suis un développeur full-stack passionné par les technologies modernes. J'aime créer des interfaces utilisateur intuitives et des expériences web exceptionnelles.", "email": "ourbo100.com@gmail.com", "phone": "+216 50182778 / +235 60802857", "location": "Gabès, Tunisie"}
STATS = [("4+", "ans d'expérience"), ("32", "projets livrés"), ("98%", "clients satisfaits"), ("3", "langues parlées")]
SKILLS = [("Frontend", "Interfaces accessibles, rapides et mémorables.", [("HTML & CSS", 94), ("JavaScript", 88), ("Responsive design", 92)]), ("Backend & outils", "Une base robuste pour faire grandir votre produit.", [("Python / Flask", 86), ("SQL / SQLite", 84), ("Linux & Git", 80)]), ("Langues", "Une communication fluide, du brief au suivi.", [("Français", 100), ("Anglais", 86), ("Arabe", 92)])]
PROJECTS = [{"title": "restaurant delicieux", "category": "Site vitrine", "description": "Restaurant Délicieux est un site vitrine dédié à un restaurant gastronomique. Il présente les plats, les services, les horaires et les informations de réservation dans une interface conviviale et attrayante.", "tags": ["HTML", "CSS", "UX"]}, {"title": "frite express", "category": "Application web", "description": "Frite Express est un site web de restauration rapide permettant de découvrir le menu, consulter les spécialités et passer des commandes en ligne. Son design moderne offre une expérience utilisateur simple et rapide.", "tags": ["JavaScript", "Flask", "SQLite"]}, {"title": "parfumerie halou", "category": "site vitrine", "description": "Parfumerie Halou est une boutique en ligne de parfums proposant une sélection de fragrances pour hommes et femmes. Le site met l'accent sur une interface élégante, une navigation intuitive et une présentation soignée des produits.", "tags": ["HTML", "CSS", "Python"]}]
PROCESS = [("01", "Découverte", "Nous clarifions vos objectifs, vos utilisateurs et la meilleure direction."), ("02", "Conception", "Je dessine une expérience simple avant de construire chaque écran."), ("03", "Développement", "Le produit prend vie par petites étapes visibles et testables."), ("04", "Livraison", "Mise en ligne, transmission et suivi pour démarrer sereinement.")]
BENEFITS = [("✦", "Un partenaire impliqué", "Des échanges directs, des décisions expliquées et un vrai sens du détail."), ("↗", "Pensé pour vos objectifs", "Chaque choix de design ou de code sert vos utilisateurs et votre activité."), ("✓", "Une base durable", "Un code clair, performant et maintenable pour évoluer sans repartir de zéro.")]
FAQ = [("Combien de temps prend un projet ?", "Selon le périmètre, un site vitrine prend généralement 2 à 4 semaines. Nous définissons un planning précis au démarrage."), ("Pouvez-vous reprendre un site existant ?", "Oui. Je commence par un audit rapide pour identifier les améliorations prioritaires et proposer un plan réaliste."), ("Travaillez-vous à distance ?", "Absolument. Les rendez-vous se font en visio et le suivi reste fluide grâce à des points réguliers."), ("Le site sera-t-il facile à faire évoluer ?", "Oui. Je privilégie une structure lisible et je fournis les indications nécessaires pour les évolutions futures.")]

def init_db():
    DATABASE.parent.mkdir(exist_ok=True)
    if not DATABASE.exists():
        with sqlite3.connect(DATABASE) as connection:
            connection.executescript((BASE_DIR / "schema.sql").read_text(encoding="utf-8"))

def send_notification(data):
    host, username, password, recipient = os.getenv("SMTP_HOST"), os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"), os.getenv("CONTACT_RECIPIENT")
    if not all((host, username, password, recipient)): return False
    email = EmailMessage(); email["Subject"] = f"[Portfolio] {data['sujet']}"; email["From"] = os.getenv("MAIL_FROM", username); email["To"] = recipient; email["Reply-To"] = data["email"]
    email.set_content(f"Nom : {data['nom']}\nEmail : {data['email']}\n\n{data['message']}")
    try:
        with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=10) as server:
            server.starttls(); server.login(username, password); server.send_message(email)
        return True
    except (OSError, ValueError, smtplib.SMTPException): return False

@app.get("/")
def home():
    return render_template("index.html", profile=PROFILE, stats=STATS, skills=SKILLS, projects=PROJECTS, process=PROCESS, benefits=BENEFITS, faq=FAQ)

@app.post("/contact")
def contact():
    data = request.get_json(silent=True) or {}
    values = {key: str(data.get(key, "")).strip() for key in ("nom", "email", "sujet", "message")}
    errors = {}
    if len(values["nom"]) < 2: errors["nom"] = "Indiquez votre nom."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", values["email"]): errors["email"] = "Indiquez une adresse email valide."
    if len(values["sujet"]) < 3: errors["sujet"] = "Précisez le sujet de votre demande."
    if len(values["message"]) < 20: errors["message"] = "Votre message doit contenir au moins 20 caractères."
    if errors: return jsonify(success=False, message="Veuillez corriger les champs indiqués.", errors=errors), 400
    sent = send_notification(values)
    try:
        with sqlite3.connect(DATABASE) as connection:
            connection.execute("INSERT INTO messages (nom,email,sujet,message,email_envoye) VALUES (?,?,?,?,?)", (*values.values(), int(sent)))
    except sqlite3.Error: return jsonify(success=False, message="Une erreur est survenue lors de l'enregistrement."), 500
    if not sent:
        return jsonify(success=False, message="Le message a été enregistré, mais l’envoi de l’email a échoué. Réessayez dans quelques instants."), 502
    return jsonify(success=True, message="Message bien reçu ! Je vous répondrai très vite.")

init_db()
if __name__ == "__main__": app.run(debug=True)
