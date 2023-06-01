from flask import Flask
from .blueprints.google_auth import google_auth
from .blueprints.spotify_auth import spotify_auth
from .blueprints.owner_bp import owner_bp
from .blueprints.guest_bp import guest_bp
from dotenv import load_dotenv
import os


def create_app():

    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Carga de variables de configuración segun el ambiente:
    load_dotenv()
    ENV = os.getenv("ENV")
    if ENV == "PROD":
        app.config.from_object("app.config.ProductionConfig")
    if ENV == "DEV":
        app.config.from_object("app.config.DevelopmentConfig")
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"     # Para permitir usar oauthlib localmente sin https
    else:
        app.config.from_object("app.config.DevelopmentConfig")

    # Registro de Blueprints:
    app.register_blueprint(google_auth)
    app.register_blueprint(spotify_auth)
    app.register_blueprint(owner_bp)
    app.register_blueprint(guest_bp)

    return app