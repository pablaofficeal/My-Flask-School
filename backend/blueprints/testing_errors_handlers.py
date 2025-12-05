from utils.testing.forbidden_error_403 import forbidden_error_bpp
from utils.testing.not_found_error_404 import not_found_error_bpp
from utils.testing.method_not_allowed_error_405 import method_not_allowed_error_bpp
from utils.testing.unsupported_media_type_error_415 import unsupported_media_type_error_bpp
from utils.testing.internal_server_error_500 import internal_server_error_bpp

def register_testing_error_handlers(app):
    app.register_blueprint(forbidden_error_bpp)
    app.register_blueprint(not_found_error_bpp)
    app.register_blueprint(method_not_allowed_error_bpp)
    app.register_blueprint(unsupported_media_type_error_bpp)
    app.register_blueprint(internal_server_error_bpp)
