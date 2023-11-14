import os
from dotenv import load_dotenv
from datetime import timedelta


class Config(object):

    load_dotenv()
    
    DEBUG = True
    TESTING = True
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)  # Duración de la cookie de sesión
    SECRET_KEY = os.getenv("SECRET_KEY")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing playlist-read-private user-read-email"
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300  # Tiempo de expiración predeterminado en segundos

class DevelopmentConfig(Config):
    BASE_URL = "http://localhost:8888"

class TestingConfig(Config):
    ...

class ProductionConfig(Config):
    BASE_URL = "https://rokolify.rj.r.appspot.com"
    DEBUG = False
    TESTING = False