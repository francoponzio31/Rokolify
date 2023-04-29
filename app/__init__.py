from flask import Flask
from .blueprints.spotify_auth import spotify_auth
from .blueprints.owner_bp import owner_bp
from .blueprints.guest_bp import guest_bp
from dotenv import load_dotenv
import os


def create_app():

    load_dotenv()
    ENV = os.getenv("ENV")

    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Carga de variables de configuración segun el ambiente:
    if ENV == "PROD":
        app.config.from_object("app.config.TestingConfig")
    else:
        app.config.from_object("app.config.DevelopmentConfig")

    app.register_blueprint(spotify_auth)
    app.register_blueprint(owner_bp)
    app.register_blueprint(guest_bp)
    

    return app