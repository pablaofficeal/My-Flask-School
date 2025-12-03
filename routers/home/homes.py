from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import *

homes_bpp = Blueprint('homes_bpp', __name__)

@homes_bpp.route('/home')
def home():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему, чтобы получить доступ к этой странице.')
        return redirect(url_for('oauth_bpp.login'))
    
    user = User.query.get(session['user_id'])
    
    return render_template('home.html', user=user)