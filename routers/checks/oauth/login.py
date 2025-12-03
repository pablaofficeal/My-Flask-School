from models import *
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

oauth_bpp = Blueprint('oauth_bpp', __name__)

@oauth_bpp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if user.is_active:
                session['user_id'] = user.id
                user.last_login = datetime.utcnow()
                db.session.commit()
                flash('Успешный вход в систему!', 'success')
                return redirect(url_for('home_bpp.index'))
            else:
                flash('Ваш аккаунт деактивирован. Пожалуйста, свяжитесь с администратором.', 'danger')
        else:
            flash('Неверное имя пользователя или пароль.', 'danger')
    return render_template('login.html')