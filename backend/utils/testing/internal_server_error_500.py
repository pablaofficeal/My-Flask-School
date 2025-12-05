from flask import Blueprint, render_template
internal_server_error_bpp = Blueprint('internal_server_error_bpp', __name__)

@internal_server_error_bpp.route('/internal_server_error', methods=['GET'])
def internal_server_error():
    return render_template('errors/500.html'), 500
