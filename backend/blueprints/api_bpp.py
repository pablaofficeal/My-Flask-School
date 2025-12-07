from api.change_password import change_password_bpp
from api.delete_account import delete_my_account_bpp
from api.user_status import user_status_bpp
from api.subscriptions import subscriptions_bp



def register_api_blueprints(app):
    app.register_blueprint(change_password_bpp)
    app.register_blueprint(delete_my_account_bpp)
    app.register_blueprint(user_status_bpp)
    app.register_blueprint(subscriptions_bp, url_prefix='/api/subscriptions')