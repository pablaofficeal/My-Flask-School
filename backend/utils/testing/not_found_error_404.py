from flask import Blueprint, render_template

not_found_error_bpp = Blueprint('not_found_error_bpp', __name__)

@not_found_error_bpp.route('/not_found', methods=['GET'])
def not_found_error():
    return render_template('errors/404.html'), 404