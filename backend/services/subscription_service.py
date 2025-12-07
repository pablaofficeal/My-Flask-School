from models.subscription import *
from models.users.main_user_db import User
from utils.logs_service import init_logger
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
import traceback
from models.imp import db


class SubscriptionService:
    """Сервис для управления подписками"""
    
    def __init__(self):
        self.logger = init_logger('subscription_service')
    
    def create_subscription_plan(self, plan_data):
        """Создать план подписки"""
        try:
            plan = SubscriptionPlan(**plan_data)
            db.session.add(plan)
            db.session.commit()
            
            # Создать стандартные функции для плана
            self._create_standard_features(plan.id)
            
            self.logger.info(f"Created subscription plan: {plan.name}")
            return plan
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating subscription plan: {str(e)}")
            raise
    
    def get_subscription_plan(self, plan_id):
        """Получить план подписки по ID"""
        return SubscriptionPlan.query.get(plan_id)
    
    def get_all_plans(self, active_only=True, public_only=True):
        """Получить все планы подписок"""
        query = SubscriptionPlan.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        if public_only:
            query = query.filter_by(is_public=True)
        
        return query.order_by(SubscriptionPlan.sort_order, SubscriptionPlan.price).all()
    
    def assign_subscription_to_user(self, user_id, plan_id, billing_cycle='monthly', start_trial=False):
        """Назначить подписку пользователю"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            plan = SubscriptionPlan.query.get(plan_id)
            if not plan:
                raise ValueError("Subscription plan not found")
            
            # Проверить, есть ли у пользователя активная подписка
            active_subscription = self.get_user_active_subscription(user_id)
            if active_subscription:
                # Обновить существующую подписку
                return self._upgrade_subscription(active_subscription, plan, billing_cycle)
            
            # Создать новую подписку
            subscription = UserSubscription(
                user_id=user_id,
                plan_id=plan_id,
                billing_cycle=billing_cycle,
                currency=plan.currency
            )
            
            # Установить даты
            now = datetime.utcnow()
            subscription.start_date = now
            
            if start_trial and plan.trial_days > 0:
                subscription.status = SubscriptionStatus.TRIAL
                subscription.trial_end_date = now + timedelta(days=plan.trial_days)
                subscription.end_date = subscription.trial_end_date
            else:
                subscription.status = SubscriptionStatus.PENDING
                # Установить дату окончания в зависимости от цикла биллинга
                if billing_cycle == 'monthly':
                    subscription.end_date = now + timedelta(days=30)
                elif billing_cycle == 'yearly':
                    subscription.end_date = now + timedelta(days=365)
                else:
                    subscription.end_date = now + timedelta(days=30)
            
            # Установить льготный период
            subscription.grace_period_end = subscription.end_date + timedelta(days=plan.grace_period_days)
            
            db.session.add(subscription)
            db.session.commit()
            
            # Создать лимиты для подписки
            self._create_subscription_limits(subscription)
            
            # Залогировать в историю
            action = HistoryAction.TRIAL_STARTED if start_trial else HistoryAction.CREATED
            SubscriptionHistory.log_action(
                user_id=user_id,
                subscription_id=subscription.id,
                action=action,
                new_plan_id=plan_id,
                new_status=subscription.status.value,
                new_end_date=subscription.end_date,
                description=f"Assigned {plan.name} plan to user"
            )
            
            self.logger.info(f"Assigned subscription {plan.name} to user {user_id}")
            return subscription
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error assigning subscription: {str(e)}")
            raise
    
    def get_user_subscription(self, user_id):
        """Получить подписку пользователя"""
        return UserSubscription.query.filter_by(user_id=user_id).first()
    
    def get_user_active_subscription(self, user_id):
        """Получить активную подписку пользователя"""
        return UserSubscription.query.filter(
            and_(
                UserSubscription.user_id == user_id,
                UserSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
            )
        ).first()
    
    def cancel_subscription(self, subscription_id, reason=None):
        """Отменить подписку"""
        try:
            subscription = UserSubscription.query.get(subscription_id)
            if not subscription:
                raise ValueError("Subscription not found")
            
            old_status = subscription.status.value
            subscription.cancel()
            
            # Залогировать в историю
            SubscriptionHistory.log_action(
                user_id=subscription.user_id,
                subscription_id=subscription_id,
                action=HistoryAction.CANCELLED,
                old_status=old_status,
                new_status=subscription.status.value,
                description=reason or "User cancelled subscription"
            )
            
            self.logger.info(f"Cancelled subscription {subscription_id} for user {subscription.user_id}")
            return subscription
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error cancelling subscription: {str(e)}")
            raise
    
    def renew_subscription(self, subscription_id):
        """Продлить подписку"""
        try:
            subscription = UserSubscription.query.get(subscription_id)
            if not subscription:
                raise ValueError("Subscription not found")
            
            plan = subscription.plan
            
            # Продлить дату окончания
            if subscription.billing_cycle == 'monthly':
                subscription.end_date = datetime.utcnow() + timedelta(days=30)
            elif subscription.billing_cycle == 'yearly':
                subscription.end_date = datetime.utcnow() + timedelta(days=365)
            else:
                subscription.end_date = datetime.utcnow() + timedelta(days=30)
            
            # Обновить статус
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.grace_period_end = subscription.end_date + timedelta(days=plan.grace_period_days)
            
            # Сбросить использование
            subscription.reset_monthly_usage()
            
            db.session.commit()
            
            # Залогировать в историю
            SubscriptionHistory.log_action(
                user_id=subscription.user_id,
                subscription_id=subscription_id,
                action=HistoryAction.RENEWED,
                new_end_date=subscription.end_date,
                description="Subscription renewed"
            )
            
            self.logger.info(f"Renewed subscription {subscription_id} for user {subscription.user_id}")
            return subscription
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error renewing subscription: {str(e)}")
            raise
    
    def check_and_update_subscription_status(self, user_id):
        """Проверить и обновить статус подписки пользователя"""
        try:
            subscription = self.get_user_subscription(user_id)
            if not subscription:
                return None
            
            old_status = subscription.status.value
            subscription.check_and_update_status()
            
            # Если статус изменился, залогировать
            if old_status != subscription.status.value:
                action_map = {
                    SubscriptionStatus.EXPIRED: HistoryAction.EXPIRED,
                    SubscriptionStatus.GRACE_PERIOD: HistoryAction.GRACE_PERIOD_STARTED
                }
                
                action = action_map.get(subscription.status)
                if action:
                    SubscriptionHistory.log_action(
                        user_id=user_id,
                        subscription_id=subscription.id,
                        action=action,
                        old_status=old_status,
                        new_status=subscription.status.value,
                        description=f"Subscription status automatically updated"
                    )
            
            return subscription
            
        except Exception as e:
            self.logger.error(f"Error checking subscription status: {str(e)}")
            raise
    
    def track_usage(self, user_id, usage_type, quantity=1, resource_id=None, metadata=None):
        """Отследить использование ресурсов"""
        try:
            subscription = self.get_user_active_subscription(user_id)
            if not subscription:
                # Проверить лимиты для бесплатного пользователя
                return self._track_free_user_usage(user_id, usage_type, quantity, resource_id, metadata)
            
            # Проверить лимиты подписки
            plan = subscription.plan
            
            if usage_type == 'messages':
                if subscription.messages_used_this_cycle + quantity > plan.max_messages_per_month:
                    raise ValueError("Monthly message limit exceeded")
                subscription.update_usage('messages', quantity)
            
            elif usage_type == 'bots':
                if subscription.bots_created >= plan.max_bots:
                    raise ValueError("Bot creation limit exceeded")
                subscription.update_usage('bots', quantity)
            
            elif usage_type == 'storage':
                if subscription.storage_used_mb + quantity > plan.max_storage_mb:
                    raise ValueError("Storage limit exceeded")
                subscription.update_usage('storage', quantity)
            
            # Записать в трекер использования
            UsageTracker.track_usage(
                user_id=user_id,
                subscription_id=subscription.id,
                usage_type=UsageType.MESSAGE if usage_type == 'messages' else UsageType.BOT_CREATION,
                quantity=quantity,
                resource_id=resource_id,
                metadata=metadata
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking usage: {str(e)}")
            raise
    
    def get_user_limits(self, user_id):
        """Получить лимиты пользователя"""
        subscription = self.get_user_active_subscription(user_id)
        if not subscription:
            # Вернуть лимиты для бесплатного пользователя
            return self._get_free_user_limits()
        
        plan = subscription.plan
        return {
            'bots': {
                'limit': plan.max_bots,
                'used': subscription.bots_created,
                'percentage': (subscription.bots_created / plan.max_bots * 100) if plan.max_bots > 0 else 0
            },
            'messages': {
                'limit': plan.max_messages_per_month,
                'used': subscription.messages_used_this_cycle,
                'percentage': (subscription.messages_used_this_cycle / plan.max_messages_per_month * 100) if plan.max_messages_per_month > 0 else 0
            },
            'storage': {
                'limit': plan.max_storage_mb,
                'used': subscription.storage_used_mb,
                'percentage': (subscription.storage_used_mb / plan.max_storage_mb * 100) if plan.max_storage_mb > 0 else 0
            }
        }
    
    def _upgrade_subscription(self, current_subscription, new_plan, billing_cycle):
        """Обновить существующую подписку"""
        old_plan_id = current_subscription.plan_id
        old_status = current_subscription.status.value
        
        current_subscription.plan_id = new_plan.id
        current_subscription.billing_cycle = billing_cycle
        current_subscription.currency = new_plan.currency
        
        # Обновить дату окончания если подписка активна
        if current_subscription.is_active():
            if billing_cycle == 'monthly':
                current_subscription.end_date = datetime.utcnow() + timedelta(days=30)
            elif billing_cycle == 'yearly':
                current_subscription.end_date = datetime.utcnow() + timedelta(days=365)
        
        db.session.commit()
        
        # Залогировать в историю
        SubscriptionHistory.log_action(
            user_id=current_subscription.user_id,
            subscription_id=current_subscription.id,
            action=HistoryAction.UPGRADED,
            old_plan_id=old_plan_id,
            new_plan_id=new_plan.id,
            old_status=old_status,
            new_status=current_subscription.status.value,
            description=f"Upgraded from plan {old_plan_id} to {new_plan.id}"
        )
        
        return current_subscription
    
    def _create_subscription_limits(self, subscription):
        """Создать лимиты для подписки"""
        plan = subscription.plan
        
        # Лимит сообщений
        if plan.max_messages_per_month > 0:
            UsageLimit.create_limit(
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                plan_id=plan.id,
                limit_type=LimitType.MESSAGES_PER_MONTH,
                limit_value=plan.max_messages_per_month,
                period='monthly',
                description=f"Monthly message limit for {plan.name} plan"
            )
        
        # Лимит ботов
        if plan.max_bots > 0:
            UsageLimit.create_limit(
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                plan_id=plan.id,
                limit_type=LimitType.BOTS_COUNT,
                limit_value=plan.max_bots,
                period='lifetime',
                description=f"Bot creation limit for {plan.name} plan"
            )
        
        # Лимит хранилища
        if plan.max_storage_mb > 0:
            UsageLimit.create_limit(
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                plan_id=plan.id,
                limit_type=LimitType.STORAGE_MB,
                limit_value=plan.max_storage_mb,
                period='lifetime',
                description=f"Storage limit for {plan.name} plan"
            )
    
    def _create_standard_features(self, plan_id):
        """Создать стандартные функции для плана"""
        standard_features = SubscriptionFeature.get_standard_features()
        
        for feature_data in standard_features:
            feature = SubscriptionFeature(
                plan_id=plan_id,
                **feature_data,
                icon_class=SubscriptionFeature.get_feature_icon(feature_data['feature_key']),
                color=SubscriptionFeature.get_feature_color(feature_data['feature_key'])
            )
            db.session.add(feature)
        
        db.session.commit()
    
    def _track_free_user_usage(self, user_id, usage_type, quantity, resource_id, metadata):
        """Отследить использование для бесплатного пользователя"""
        free_limits = self._get_free_user_limits()
        
        if usage_type == 'messages':
            limit = free_limits['messages']['limit']
            used = UsageTracker.query.filter_by(
                user_id=user_id,
                usage_type=UsageType.MESSAGE
            ).filter(
                UsageTracker.created_at >= datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
            ).count()
            
            if used + quantity > limit:
                raise ValueError("Free user monthly message limit exceeded")
        
        elif usage_type == 'bots':
            limit = free_limits['bots']['limit']
            used = UsageTracker.query.filter_by(
                user_id=user_id,
                usage_type=UsageType.BOT_CREATION
            ).count()
            
            if used + quantity >= limit:
                raise ValueError("Free user bot creation limit exceeded")
        
        # Записать использование
        UsageTracker.track_usage(
            user_id=user_id,
            usage_type=UsageType.MESSAGE if usage_type == 'messages' else UsageType.BOT_CREATION,
            quantity=quantity,
            resource_id=resource_id,
            metadata=metadata
        )
        
        return True
    
    def _get_free_user_limits(self):
        """Получить лимиты для бесплатного пользователя"""
        return {
            'bots': {'limit': 1, 'used': 0, 'percentage': 0},
            'messages': {'limit': 100, 'used': 0, 'percentage': 0},
            'storage': {'limit': 100, 'used': 0, 'percentage': 0}
        }


# Создать глобальный экземпляр сервиса
subscription_service = SubscriptionService()