from handlers.__init__400 import bad_request_error
from handlers.__init__403 import forbidden_error
from handlers.__init__404 import not_found_error
from handlers.__init__405 import method_not_allowed_error
from handlers.__init__415 import unsupported_media_type_error
from handlers.__init__500 import internal_server_error

def register_error_handlers(app):
    app.register_error_handler(400, bad_request_error)
    app.register_error_handler(403, forbidden_error)
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(405, method_not_allowed_error)
    app.register_error_handler(415, unsupported_media_type_error)
    app.register_error_handler(500, internal_server_error)
