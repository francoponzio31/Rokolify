import os
from dotenv import load_dotenv


class Config(object):

    load_dotenv()
    
    DEBUG = True
    TESTING = True
    SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing playlist-read-private user-read-email user-read-recently-played"
    SECRET_KEY = os.getenv("SECRET_KEY")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")


class DevelopmentConfig(Config):
    BASE_URL = "http://localhost:8888"

class TestingConfig(Config):
    BASE_URL = "https://test-spotify-api.rj.r.appspot.com"


class ProductionConfig(Config):
    ...