from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from models.models_all_rout_imp import *
from models.imp import db
import traceback

delete_my_account_bpp = Blueprint('delete_my_account_bpp', __name__)

@delete_my_account_bpp.route('/delete-account', methods=['POST', 'DELETE'])
def delete_my_account():
    user_id = session.get('user_id')
    if not user_id:
        if request.is_json:
            return jsonify({'error': 'You need to be logged in to delete your account'}), 401
        flash('You need to be logged in to delete your account', 'error')
        return redirect(url_for('oauth_bpp.login'))
    
    user = User.query.get(user_id)
    if not user:
        if request.is_json:
            return jsonify({'error': 'User not found'}), 404
        flash('User not found', 'error')
        return redirect(url_for('oauth_bpp.login'))
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    if not data:
        if request.is_json:
            return jsonify({'error': 'No data provided'}), 400
        flash('No data provided', 'error')
        return redirect(url_for('oauth_bpp.login'))
    
    password = data.get('password')
    
    if not password:
        if request.is_json:
            return jsonify({'error': 'Password is required'}), 400
        flash('Password is required', 'error')
        return redirect(url_for('oauth_bpp.login'))
    
    if not user.check_password(password):
        if request.is_json:
            return jsonify({'error': 'Password is incorrect'}), 400
        flash('Password is incorrect', 'error')
        return redirect(url_for('oauth_bpp.login'))
    
    try:
        db.session.delete(user)
        db.session.commit()        
        check_user = User.query.get(user_id)
        if check_user:
            if request.is_json:
                return jsonify({'error': 'Error deleting account. Please try again.'}), 500
            else:
                flash('Error deleting account. Please try again.', 'error')
                return redirect(url_for('oauth_bpp.login'))

        session.clear()

        if request.is_json:
            return jsonify({
                'message': 'Your account has been successfully deleted',
                'status': 'success'
            })
        else:
            flash('Your account has been successfully deleted', 'success')
            return redirect(url_for('oauth_bpp.login'))
            
    except Exception as e:
        db.session.rollback()
        
        if request.is_json:
            return jsonify({
                'error': 'Error deleting account. Please try again.',
                'status': 'error',
                'details': str(e)
            }), 500
        else:
            flash('Error deleting account. Please try again.', 'error')
            return redirect(url_for('oauth_bpp.login'))
