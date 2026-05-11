from dotenv import load_dotenv
import os

class Config:
    load_dotenv()
    PROVIDER_NAME = 'google'
    SECRET_KEY = "never-guess tget tr373 324 not#just a number 0383-but=stuff"
    SQLALCHEMY_DATABASE_URI = "sqlite:///nature_plus_database"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    SERVER_METADATA_URI = 'https://accounts.google.com/.well-known/openid-configuration'
    DATA = {'scope': 'openid email profile'}