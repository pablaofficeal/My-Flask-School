from datetime import timedelta
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = 'your_secret_key'
    #SQLALCHEMY_DATABASE_URI = 'postgresql://your_db_user:your_db_password@db:5432/your_db_name'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Установите в True в продакшене
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
    GITHUB_REDIRECT_URI = os.getenv('GITHUB_REDIRECT_URI')
    GITHUB_AUTHORIZE_URL = os.getenv('GITHUB_AUTHORIZE_URL')
    GITHUB_TOKEN_URL = os.getenv('GITHUB_TOKEN_URL')
    GITHUB_USER_URL = os.getenv('GITHUB_USER_URL')
    GITHUB_EMAILS_URL = os.getenv('GITHUB_EMAILS_URL')

    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
