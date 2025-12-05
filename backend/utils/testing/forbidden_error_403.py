from flask import Blueprint, render_template

forbidden_error_bpp = Blueprint('forbidden_error_bpp', __name__)

@forbidden_error_bpp.route('/forbidden', methods=['GET'])
def forbidden_error():
    return render_template('errors/403.html')
