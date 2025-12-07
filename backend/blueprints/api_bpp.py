from api.change_password import change_password_bpp

def register_api_blueprints(app):
    app.register_blueprint(change_password_bpp)