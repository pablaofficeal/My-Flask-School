# app.py
from flask import Flask
from config import Config
from models import db
from flask_wtf import CSRFProtect

# Импорты с правильной структурой папок
from routers.home.main_home import home_bpp
from routers.checks.oauth.login import oauth_bpp
from routers.checks.oauth.register import oauth_register_bpp
from routers.checks.oauth.logout import oauth_logout_bpp
from routers.home.homes import homes_bpp
from routers.home.profile import profile_bpp

app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)

# ЖЁСТКАЯ БЕЗОПАСНОСТЬ СЕССИИ
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,      # Нельзя читать через JS
    SESSION_COOKIE_SECURE=False,        # Только по HTTPS (в проде!)
    SESSION_COOKIE_SAMESITE='Lax',     # Защита от CSRF
    WTF_CSRF_ENABLED=True,
    WTF_CSRF_TIME_LIMIT=None
)

csrf = CSRFProtect(app)
db.init_app(app)

app.register_blueprint(home_bpp)
app.register_blueprint(oauth_bpp)
app.register_blueprint(oauth_register_bpp, url_prefix='/register')
app.register_blueprint(oauth_logout_bpp, url_prefix='/logout')
app.register_blueprint(homes_bpp)
app.register_blueprint(profile_bpp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)  # В проде debug=False!