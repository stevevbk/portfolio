from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import EmailStr, ValidationError
import aiosmtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import logging

# Chargement des variables d'environnement (fichier config.env)
load_dotenv("config.env")

# Configuration basique du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Monture du dossier static pour servir CSS, JS, images, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration des templates Jinja2
templates = Jinja2Templates(directory="templates")


@app.get("/logo.svg")
def logo():
    """
    Sert le fichier SVG du logo.
    """
    return FileResponse("static/logo.svg", media_type="image/svg+xml")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Page d'accueil (template index.html).
    """
    return templates.TemplateResponse("index.html", {"request": request})


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
    Bonnes pratiques appliquées :
    - Validation du format d'email avec pydantic.EmailStr
    - Gestion des exceptions d'envoi SMTP
    - Logging des erreurs
    - Renvoi d'une réponse JSON en cas d'erreur ou redirection vers la page d'accueil en cas de succès
    """

    # 1. Validation minimale du format d'email
    try:
        valid_email = EmailStr.validate(email)
    except ValidationError as e:
        # Si l'email n'est pas au bon format, on renvoie une réponse 400
        logger.error(f"Email invalide reçu : {email}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Adresse e-mail invalide."}
        )

    # 2. Préparation du message
    email_message = EmailMessage()
    email_message["From"] = os.getenv("EMAIL_USER")
    email_message["To"] = os.getenv("EMAIL_TO")
    email_message["Subject"] = f"Portfolio Contact: {subject}"
    email_message.set_content(
        f"Name: {fullname}\n"
        f"Email: {valid_email}\n"
        f"Phone: {phone or 'Non spécifié'}\n\n"
        f"Message:\n{message}"
    )

    # 3. Envoi via SMTP sécurisé
    try:
        await aiosmtplib.send(
            email_message,
            hostname=os.getenv("EMAIL_HOST"),
            port=int(os.getenv("EMAIL_PORT")),
            username=os.getenv("EMAIL_USER"),
            password=os.getenv("EMAIL_PASS"),
            start_tls=True,
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
