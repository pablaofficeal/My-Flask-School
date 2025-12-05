from flask import Blueprint, render_template

unsupported_media_type_error_bpp = Blueprint('unsupported_media_type_error_bpp', __name__)

@unsupported_media_type_error_bpp.route('/unsupported_media_type', methods=['GET'])
def unsupported_media_type_error():
    return render_template('errors/415.html'), 415