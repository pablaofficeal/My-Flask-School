from flask import render_template

def method_not_allowed_error(error):
    return render_template('errors/405.html'), 405