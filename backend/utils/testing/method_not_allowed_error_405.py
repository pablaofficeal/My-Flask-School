from flask import Blueprint, render_template

method_not_allowed_error_bpp = Blueprint('method_not_allowed_error_bpp', __name__)

@method_not_allowed_error_bpp.route('/method_not_allowed', methods=['GET'])
def method_not_allowed_error():
    return render_template('errors/405.html'), 405
