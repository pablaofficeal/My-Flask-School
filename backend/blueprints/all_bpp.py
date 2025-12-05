from routers.home.main_home import home_bpp
from routers.checks.oauth.login import oauth_bpp
from routers.checks.oauth.register import oauth_register_bpp
from routers.checks.oauth.logout import oauth_logout_bpp
from routers.home.homes import homes_bpp
from routers.home.profile import profile_bpp

def register_all_blueprints(app):
    app.register_blueprint(home_bpp)
    app.register_blueprint(oauth_bpp)
    app.register_blueprint(oauth_register_bpp, url_prefix='/register')
    app.register_blueprint(oauth_logout_bpp, url_prefix='/logout')
    app.register_blueprint(homes_bpp)
    app.register_blueprint(profile_bpp)