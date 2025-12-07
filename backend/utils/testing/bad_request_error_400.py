from flask import Blueprint, render_template

bad_request_error_bpp = Blueprint('bad_request_error_bpp', __name__)

@bad_request_error_bpp.route('/bad_request', methods=['GET'])
def bad_request_error():
    return render_template('errors/400.html'), 400
