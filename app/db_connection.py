from pymongo import MongoClient
import os
from dotenv import load_dotenv


def connect_to_db():

    load_dotenv()
    ENV = os.getenv("ENV")
    USERNAME = os.getenv("DB_USERNAME")
    PASSWORD = os.getenv("DB_PASSWORD")
    DB_URI = f"mongodb+srv://{USERNAME}:{PASSWORD}@cluster0.ebshqnh.mongodb.net/?retryWrites=true&w=majority"

    client = MongoClient(DB_URI)

    # Acceso a la base de datos del ambiente:
    if ENV == "PROD":
        db = client["rokolify_prod"]
    else:
        db = client["rokolify_dev"]

    return db
