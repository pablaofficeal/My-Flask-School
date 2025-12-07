from flask import Blueprint, jsonify, request
from models.models_all_rout_imp import *
from models.imp import db

user_status_bpp = Blueprint('user_status_bpp', __name__)

@user_status_bpp.route('/profile/status', methods=['GET'])
def profile_status():
    user = User.query.first()
    if not user:
        return jsonify({"is_active": False}), 200
    return jsonify({"is_active": user.is_active}), 200
