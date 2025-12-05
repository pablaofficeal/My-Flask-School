from flask import Blueprint, render_template, session
from models import *

home_bpp = Blueprint('home_bpp', __name__)

@home_bpp.route('/')
def index():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)