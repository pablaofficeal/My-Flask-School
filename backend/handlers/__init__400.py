from flask import render_template

def bad_request_error(error):
    return render_template('errors/400.html'), 400
