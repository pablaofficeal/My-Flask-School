from flask import Blueprint, request, jsonify, session
from models.models_all_rout_imp import *
from models.imp import db
from services.subscription_service import subscription_service
from utils.logs_service import init_logger

my_subscription_bpp = Blueprint('my_subscription_bpp', __name__)
logger = init_logger('my_subscription_api')

@my_subscription_bpp.route('/my_subscription', methods=['GET'])
def get_my_subscription():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Проверить и обновить статус подписки
        subscription_service.check_and_update_subscription_status(user_id)
        
        subscription = subscription_service.get_user_subscription(user_id)
        
        if not subscription:
            return jsonify({
                'success': True,
                'data': None,
                'message': 'No active subscription found'
            }), 200
        
        subscription_data = subscription.to_dict()
        subscription_data['plan'] = subscription.plan.to_dict()
        subscription_data['limits'] = subscription_service.get_user_limits(user_id)
        
        return jsonify({
            'success': True,
            'data': subscription_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user subscription: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@my_subscription_bpp.route('/my_subscription/create/test', methods=['POST'])
def create_test_subscription():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Создать тестовую подписку с базовым планом (ID 1)
        subscription = subscription_service.assign_subscription_to_user(
            user_id=user_id,
            plan_id=1,  # Предполагаем, что есть базовый план с ID 1
            billing_cycle='monthly',
            start_trial=True
        )
        
        return jsonify({
            'success': True,
            'data': subscription.to_dict(),
            'message': 'Test subscription created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error creating test subscription: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500