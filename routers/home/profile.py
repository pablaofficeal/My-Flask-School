# routers/home/profile.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from models import User, db

profile_bpp = Blueprint('profile_bpp', __name__)

@profile_bpp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему.', 'danger')
        return redirect(url_for('oauth_bpp.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        # ЗАЩИТА ОТ CSRF — ОБЯЗАТЕЛЬНО!
        if request.form.get('csrf_token') != session.get('csrf_token'):
            flash('Недействительный CSRF-токен.', 'danger')
            return redirect(url_for('profile_bpp.profile'))

        if request.form.get('confirm_delete') == 'yes':
            db.session.delete(user)
            db.session.commit()
            session.clear()
            flash('Аккаунт удалён навсегда.', 'success')
            return redirect(url_for('home_bpp.index'))

    return render_template('profile.html', user=user, csrf_token=session.get('csrf_token', ''))