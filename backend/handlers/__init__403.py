from flask import render_template

def forbidden_error(error):
    return render_template('errors/403.html'), 403
