import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in ["true", "1"]
    SECRET_KEY = os.getenv("SECRET_KEY", "default_dev_key")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
