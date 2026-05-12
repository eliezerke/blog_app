from dotenv import load_dotenv
import os

class Config:
    load_dotenv()
    PROVIDER_NAME = 'google'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'temporary-secret-key-please-change-this-in-production-use-a-secure-random-value')
    SQLALCHEMY_DATABASE_URI = "sqlite:///nature_plus_database"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    SERVER_METADATA_URI = 'https://accounts.google.com/.well-known/openid-configuration'
    DATA = {'scope': 'openid email profile'}

    DATABASE_URL = os.getenv("DATABASE_URL_A")
    SERVICE_ACCOUNT_PATH = os.getenv("SERVICE_ACCOUNT_PATH_A")