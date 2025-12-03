from flask import Blueprint, request, redirect, url_for, session, flash

oauth_logout_bpp = Blueprint('oauth_logout_bpp', __name__)

@oauth_logout_bpp.route('/', methods=['GET'])
def logout():
    session.clear()
    flash('Вы успешно вышли из системы.', 'success')
    return redirect(url_for('home_bpp.index'))