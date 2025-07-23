from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import EmailStr, ValidationError, BaseModel
import aiosmtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import logging

# Modèle Pydantic pour valider l'email utilisateur
class EmailCheckModel(BaseModel):
    email: EmailStr

# Chargement des variables d'environnement (fichier config.env)
# Permet de stocker les informations sensibles (identifiants SMTP, destinataire, etc.) hors du code
load_dotenv("config.env")

# Configuration basique du logger pour afficher les informations et erreurs dans la console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI()

# Monture du dossier static pour servir CSS, JS, images, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration des templates Jinja2 pour le rendu HTML
templates = Jinja2Templates(directory="templates")

# Route pour servir le logo SVG (optionnel)
@app.get("/logo.svg")
def logo():
    """
    Sert le fichier SVG du logo.
    """
    return FileResponse("static/logo.svg", media_type="image/svg+xml")

# Route principale pour afficher la page d'accueil
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Page d'accueil (template index.html).
    """
    return templates.TemplateResponse("index.html", {"request": request})

# Route pour traiter le formulaire de contact (POST)
@app.post("/contact")
async def contact(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    subject: str = Form(...),
    message: str = Form(...)
):
    """
    Reçoit les données du formulaire de contact et envoie un e-mail via SMTP.
    Étapes détaillées :
    1. Validation du format d'email avec pydantic.EmailStr
    2. Préparation du message e-mail
    3. Envoi via SMTP sécurisé (aiosmtplib)
    4. Gestion des erreurs et réponses appropriées
    """

    # 1. Validation minimale du format d'email
    try:
        # Valide l'email via un modèle Pydantic
        valid_email = EmailCheckModel(email=email).email
    except ValidationError as e:
        # Si l'email n'est pas au bon format, on logue l'erreur et on renvoie une réponse 400
        logger.error(f"Email invalide reçu : {email}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Adresse e-mail invalide."}
        )

    # 2. Préparation du message e-mail
    email_message = EmailMessage()
    email_message["From"] = os.getenv("EMAIL_USER")  # Toujours ton adresse Gmail
    email_message["To"] = os.getenv("EMAIL_TO")      # Destinataire
    email_message["Subject"] = f"Portfolio Contact: {subject}"
    email_message["Reply-To"] = valid_email          # <-- Ajoute cette ligne

    email_message.set_content(
        f"Name: {fullname}\n"
        f"Email: {valid_email}\n"
        f"Phone: {phone or 'Non spécifié'}\n\n"
        f"Message:\n{message}"
    )

    # 3. Envoi via SMTP sécurisé
    try:
        # Utilise aiosmtplib pour envoyer l'e-mail de façon asynchrone et sécurisée
        await aiosmtplib.send(
            email_message,
            hostname=os.getenv("EMAIL_HOST"),
            port=int(os.getenv("EMAIL_PORT")),
            username=os.getenv("EMAIL_USER"),
            password=os.getenv("EMAIL_PASS"),
            start_tls=True,  # Active le chiffrement TLS
        )
        logger.info(f"E-mail de contact envoyé avec succès pour {valid_email}")
    except Exception as smtp_error:
        # Gestion d'erreur d'envoi : on logue et on renvoie une réponse d'erreur
        logger.error(f"Erreur lors de l'envoi de l'e-mail : {smtp_error}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Une erreur est survenue lors de l'envoi de votre message. Veuillez réessayer plus tard."}
        )

    # 4. En cas de succès, on redirige vers la page d'accueil (ou on pourrait renvoyer un template de confirmation)
    #    Code 303 pour éviter la resoumission du formulaire si l'utilisateur rafraîchit la page
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
