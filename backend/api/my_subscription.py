from flask import Blueprint, request, jsonify, session
from models.models_all_rout_imp import *
from models.imp import db

my_subscription_bpp = Blueprint('my_subscription_bpp', __name__)

@my_subscription_bpp.route('/my_subscription', methods=['GET'])
def get_my_subscription():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(user_id)
    return jsonify({'subscription': user.subscription})

@my_subscription_bpp.route('/my_subscription/create/test', methods=['POST'])
def create_test_subscription():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(user_id)
    user.subscription = 'test'
    db.session.commit()
    return jsonify({'subscription': user.subscription})
