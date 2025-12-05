from flask import render_template

def internal_server_error(error):
    return render_template('errors/500.html'), 500