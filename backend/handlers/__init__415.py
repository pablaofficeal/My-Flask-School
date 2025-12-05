from flask import render_template

def unsupported_media_type_error(error):
    return render_template('errors/415.html'), 415 