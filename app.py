from flask import Flask, render_template
from config import Config
from models import *
from routers.home.main_home import home_bpp
from routers.checks.oauth.login import oauth_bpp
from routers.checks.oauth.register import oauth_register_bpp
from routers.checks.oauth.logout import oauth_logout_bpp
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
app.register_blueprint(home_bpp)
app.register_blueprint(oauth_bpp)
app.register_blueprint(oauth_register_bpp)
app.register_blueprint(oauth_logout_bpp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)