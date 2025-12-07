from flask import Blueprint, request, jsonify, session, flash, redirect, url_for
from models.imp import db
from models.models_all_rout_imp import *

change_password_bpp = Blueprint('change_password_bpp', __name__)

@change_password_bpp.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        flash("Пожалуйста, войдите в систему", "error")
        return redirect(url_for("oauth_bpp.login"))
    
    user_id = session['user_id']
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')

    # Валидация входных данных
    if not old_password or not new_password:
        flash("Пожалуйста, заполните все поля", "error")
        return redirect(url_for("profile_bpp.profile"))

    # Проверка длины нового пароля
    if len(new_password) < 6:
        flash("Новый пароль должен быть не менее 6 символов", "error")
        return redirect(url_for("profile_bpp.profile"))

    user = User.query.get(user_id)

    if not user:
        flash("Пользователь не найден", "error")
        return redirect(url_for("oauth_bpp.login"))

    if not user.check_password(old_password):
        flash("Неверный текущий пароль", "error")
        return redirect(url_for("profile_bpp.profile"))

    # Устанавливаем новый пароль
    user.set_password(new_password)
    
    try:
        db.session.commit()
        flash("Пароль успешно обновлен", "success")
    except Exception as e:
        db.session.rollback()
        flash("Ошибка при обновлении пароля", "error")
    
    return redirect(url_for("profile_bpp.profile"))