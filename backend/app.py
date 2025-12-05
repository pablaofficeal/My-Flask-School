from flask import Flask
from config import Config
from models.imp import db
from models.models_all_rout_imp import *
from flask_wtf import CSRFProtect
from blueprints.all_bpp import register_all_blueprints
from blueprints.testing_errors_handlers import register_testing_error_handlers
from blueprints.errors_handlers import register_error_handlers

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config.from_object(Config)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,      # Нельзя читать через JS
    SESSION_COOKIE_SECURE=False,        # Только по HTTPS (в проде!)
    SESSION_COOKIE_SAMESITE='Lax',     # Защита от CSRF
    WTF_CSRF_ENABLED=True,
    WTF_CSRF_TIME_LIMIT=None
)
csrf = CSRFProtect(app)
db.init_app(app)

register_all_blueprints(app)
register_testing_error_handlers(app)
register_error_handlers(app)



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # В проде debug=False!