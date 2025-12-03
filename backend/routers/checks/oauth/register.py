from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import *
from werkzeug.security import generate_password_hash, check_password_hash

oauth_register_bpp = Blueprint('oauth_register_bpp', __name__, url_prefix='/register')

@oauth_register_bpp.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Имя пользователя или email уже существуют.', 'danger')
            return redirect(url_for('oauth_register_bpp.register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('oauth_bpp.login'))
    
    return render_template('register.html')