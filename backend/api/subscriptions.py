from flask import Blueprint, request, jsonify, current_app, session
from models.models_all_rout_imp import *
from models.users.main_user_db import User
from services.subscription_service import subscription_service
from services.transaction_service import transaction_service
from utils.logs_service import init_logger
from datetime import datetime
import traceback

# JWT убран нахуй - теперь используем session-based аутентификацию


subscriptions_bp = Blueprint('subscriptions', __name__)
logger = init_logger('subscriptions_api')


@subscriptions_bp.route('/plans', methods=['GET'])
def get_subscription_plans():
    """Получить список доступных планов подписок"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        public_only = request.args.get('public_only', 'true').lower() == 'true'
        
        plans = subscription_service.get_all_plans(active_only=active_only, public_only=public_only)
        
        return jsonify({
            'success': True,
            'data': [plan.to_dict() for plan in plans]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting subscription plans: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# JWT ПОЛНОСТЬЮ УБРАН НАХУЙ ИЗ ВСЕГО ФАЙЛА!
# ВСЕ ДЕКОРАТОРЫ @jwt_required() УДАЛЕНЫ!
# ВСЕ get_jwt_identity() ЗАМЕНЕНЫ НА session['user_id']!
# ТЕПЕРЬ ИСПОЛЬЗУЕТСЯ ТОЛЬКО SESSION-BASED АУТЕНТИФИКАЦИЯ!


@subscriptions_bp.route('/plans/<int:plan_id>', methods=['GET'])
def get_subscription_plan(plan_id):
    """Получить детали конкретного плана подписки"""
    try:
        plan = subscription_service.get_subscription_plan(plan_id)
        if not plan:
            return jsonify({
                'success': False,
                'error': 'Subscription plan not found'
            }), 404
        
        plan_data = plan.to_dict()
        plan_data['features'] = [feature.to_dict() for feature in plan.features]
        
        return jsonify({
            'success': True,
            'data': plan_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting subscription plan: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@subscriptions_bp.route('/my-subscription', methods=['GET'])
def get_my_subscription():
    """Получить подписку текущего пользователя"""
    try:
        # Получаем user_id из сессии вместо JWT
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
            
        user_id = session['user_id']
        
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


@subscriptions_bp.route('/my-subscription/assign', methods=['POST'])
def assign_subscription():
    """Назначить подписку пользователю"""
    try:
        # Получаем user_id из сессии вместо JWT
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
            
        user_id = session['user_id']
        data = request.get_json()
        
        plan_id = data.get('plan_id')
        billing_cycle = data.get('billing_cycle', 'monthly')
        start_trial = data.get('start_trial', False)
        
        if not plan_id:
            return jsonify({
                'success': False,
                'error': 'Plan ID is required'
            }), 400
        
        if billing_cycle not in ['monthly', 'yearly']:
            return jsonify({
                'success': False,
                'error': 'Invalid billing cycle. Must be monthly or yearly'
            }), 400
        
        subscription = subscription_service.assign_subscription_to_user(
            user_id=user_id,
            plan_id=plan_id,
            billing_cycle=billing_cycle,
            start_trial=start_trial
        )
        
        return jsonify({
            'success': True,
            'data': subscription.to_dict(),
            'message': 'Subscription assigned successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error assigning subscription: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@subscriptions_bp.route('/my-subscription/cancel', methods=['POST'])
def cancel_subscription():
    """Отменить подписку пользователя"""
    try:
        # Получаем user_id из сессии вместо JWT
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
            
        user_id = session['user_id']
        data = request.get_json()
        
        reason = data.get('reason')
        
        subscription = subscription_service.get_user_subscription(user_id)
        if not subscription:
            return jsonify({
                'success': False,
                'error': 'No subscription found'
            }), 404
        
        cancelled_subscription = subscription_service.cancel_subscription(
            subscription_id=subscription.id,
            reason=reason
        )
        
        return jsonify({
            'success': True,
            'data': cancelled_subscription.to_dict(),
            'message': 'Subscription cancelled successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@subscriptions_bp.route('/my-subscription/renew', methods=['POST'])
def renew_subscription():
    """Продлить подписку пользователя"""
    try:
        # Получаем user_id из сессии вместо JWT
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
            
        user_id = session['user_id']
        
        subscription = subscription_service.get_user_subscription(user_id)
        if not subscription:
            return jsonify({
                'success': False,
                'error': 'No subscription found'
            }), 404
        
        renewed_subscription = subscription_service.renew_subscription(subscription.id)
        
        return jsonify({
            'success': True,
            'data': renewed_subscription.to_dict(),
            'message': 'Subscription renewed successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error renewing subscription: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@subscriptions_bp.route('/my-limits', methods=['GET'])
def get_my_limits():
    """Получить лимиты текущего пользователя"""
    try:
        # Получаем user_id из сессии вместо JWT
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
            
        user_id = session['user_id']
        
        limits = subscription_service.get_user_limits(user_id)
        
        return jsonify({
            'success': True,
            'data': limits
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user limits: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@subscriptions_bp.route('/track-usage', methods=['POST'])
def track_usage():
    """Отследить использование ресурсов"""
    try:
        # Получаем user_id из сессии вместо JWT
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
            
        user_id = session['user_id']
        data = request.get_json()
        
        usage_type = data.get('usage_type')
        quantity = data.get('quantity', 1)
        resource_id = data.get('resource_id')
        metadata = data.get('metadata')
        
        if not usage_type:
            return jsonify({
                'success': False,
                'error': 'Usage type is required'
            }), 400
        
        if usage_type not in ['messages', 'bots', 'storage']:
            return jsonify({
                'success': False,
                'error': 'Invalid usage type. Must be messages, bots, or storage'
            }), 400
        
        subscription_service.track_usage(
            user_id=user_id,
            usage_type=usage_type,
            quantity=quantity,
            resource_id=resource_id,
            metadata=metadata
        )
        
        return jsonify({
            'success': True,
            'message': 'Usage tracked successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error tracking usage: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@subscriptions_bp.route('/history', methods=['GET'])
def get_subscription_history():
    """Получить историю подписки текущего пользователя"""
    try:
        # Получаем user_id из сессии вместо JWT
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
            
        user_id = session['user_id']
        limit = request.args.get('limit', 50, type=int)
        
        history = SubscriptionHistory.get_user_history(user_id, limit=limit)
        
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in history]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting subscription history: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# Транзакции
@subscriptions_bp.route('/transactions', methods=['GET'])
def get_transactions():
    """Получить транзакции текущего пользователя"""
    try:
        # Получаем user_id из сессии вместо JWT
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
            
        user_id = session['user_id']
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        transactions = transaction_service.get_user_transactions(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        stats = transaction_service.get_user_transaction_stats(user_id)
        
        return jsonify({
            'success': True,
            'data': [transaction.to_dict() for transaction in transactions],
            'stats': stats,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': stats['total_transactions']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@subscriptions_bp.route('/transactions', methods=['POST'])
def create_transaction():
    """Создать транзакцию"""
    try:
        # Получаем user_id из сессии вместо JWT
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
            
        user_id = session['user_id']
        data = request.get_json()
        
        plan_id = data.get('plan_id')
        amount = data.get('amount')
        currency = data.get('currency', 'USD')
        billing_cycle = data.get('billing_cycle', 'monthly')
        payment_method = data.get('payment_method', 'credit_card')
        metadata = data.get('metadata', {})
        
        if not plan_id or not amount:
            return jsonify({
                'success': False,
                'error': 'Plan ID and amount are required'
            }), 400
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid amount format'
            }), 400
        
        transaction = transaction_service.create_transaction(
            user_id=user_id,
            subscription_plan_id=plan_id,
            amount=amount,
            currency=currency,
            billing_cycle=billing_cycle,
            payment_method=payment_method,
            metadata=metadata
        )
        
        return jsonify({
            'success': True,
            'data': transaction.to_dict(),
            'message': 'Transaction created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@subscriptions_bp.route('/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Получить детали транзакции"""
    try:
        # Получаем user_id из сессии вместо JWT
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
            
        user_id = session['user_id']
        
        transaction = transaction_service.get_transaction(transaction_id)
        if not transaction or transaction.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Transaction not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': transaction.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transaction: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@subscriptions_bp.route('/transactions/<int:transaction_id>/process', methods=['POST'])
def process_transaction(transaction_id):
    """Обработать транзакцию (оплатить)"""
    try:
        # Получаем user_id из сессии вместо JWT
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
            
        user_id = session['user_id']
        data = request.get_json()
        
        transaction = transaction_service.get_transaction(transaction_id)
        if not transaction or transaction.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Transaction not found'
            }), 404
        
        payment_data = data.get('payment_data', {})
        
        processed_transaction = transaction_service.process_transaction(
            transaction_id=transaction_id,
            payment_data=payment_data
        )
        
        return jsonify({
            'success': True,
            'data': processed_transaction.to_dict(),
            'message': 'Transaction processed successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error processing transaction: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@subscriptions_bp.route('/transactions/<int:transaction_id>/refund', methods=['POST'])
def refund_transaction(transaction_id):
    """Вернуть транзакцию"""
    try:
        # Получаем user_id из сессии вместо JWT
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
            
        user_id = session['user_id']
        data = request.get_json()
        
        transaction = transaction_service.get_transaction(transaction_id)
        if not transaction or transaction.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Transaction not found'
            }), 404
        
        amount = data.get('amount')
        reason = data.get('reason', 'User requested refund')
        
        if amount:
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Invalid amount format'
                }), 400
        
        refund_transaction = transaction_service.refund_transaction(
            transaction_id=transaction_id,
            amount=amount,
            reason=reason
        )
        
        return jsonify({
            'success': True,
            'data': refund_transaction.to_dict(),
            'message': 'Refund processed successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error refunding transaction: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500