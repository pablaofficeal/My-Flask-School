from flask import Blueprint, render_template, request, redirect, url_for, session, flash 
from models import * 
from werkzeug.security import generate_password_hash, check_password_hash 
from datetime import datetime 
from flask_wtf.csrf import generate_csrf 
profile_bpp = Blueprint('profile_bpp', __name__) 
@profile_bpp.route('/profile', methods=['GET', 'POST']) 
def profile(): 
    if 'user_id' not in session: 
        flash('Пожалуйста, войдите в систему.', 'danger') 
        return redirect(url_for('oauth_bpp.login')) 
    user = User.query.get(session['user_id']) 
    email = user.email 
    csrf_token = generate_csrf() 
    if request.method == 'POST': 
        if 'delete_account' in request.form: 
            db.session.delete(user) 
            db.session.commit() 
            session.clear() 
            flash('Ваш аккаунт был успешно удален.', 'success') 
            return redirect(url_for('home_bpp.index')) 
        return render_template('profile.html', user=user, email=email)
