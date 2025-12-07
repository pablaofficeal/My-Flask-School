from models.imp import db
from datetime import datetime
import enum


class HistoryAction(enum.Enum):
    """Типы действий в истории подписки"""
    CREATED = "created"
    ACTIVATED = "activated"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    REACTIVATED = "reactivated"
    EXPIRED = "expired"
    UPGRADED = "upgraded"
    DOWNGRADED = "downgraded"
    RENEWED = "renewed"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    TRIAL_STARTED = "trial_started"
    TRIAL_ENDED = "trial_ended"
    GRACE_PERIOD_STARTED = "grace_period_started"
    GRACE_PERIOD_ENDED = "grace_period_ended"


class SubscriptionHistory(db.Model):
    """Модель истории изменений подписки"""
    __tablename__ = 'subscription_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('user_subscriptions.id'), nullable=True)
    
    # Действие
    action = db.Column(db.Enum(HistoryAction), nullable=False)
    
    # Детали подписки до изменения
    old_plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=True)
    old_status = db.Column(db.String(50), nullable=True)
    old_end_date = db.Column(db.DateTime, nullable=True)
    
    # Детали подписки после изменения
    new_plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=True)
    new_status = db.Column(db.String(50), nullable=True)
    new_end_date = db.Column(db.DateTime, nullable=True)
    
    # Дополнительная информация
    description = db.Column(db.Text)  # Описание изменения
    metadata = db.Column(db.JSON)  # Дополнительные метаданные
    ip_address = db.Column(db.String(45))  # IP адрес пользователя
    user_agent = db.Column(db.String(500))  # User agent
    
    # Системные поля
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    user = db.relationship('User', backref='subscription_history', lazy=True)
    subscription = db.relationship('UserSubscription', backref='history', lazy=True)
    old_plan = db.relationship('SubscriptionPlan', foreign_keys=[old_plan_id], lazy=True)
    new_plan = db.relationship('SubscriptionPlan', foreign_keys=[new_plan_id], lazy=True)
    
    def __repr__(self):
        return f'<SubscriptionHistory user_id={self.user_id} action={self.action.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subscription_id': self.subscription_id,
            'action': self.action.value,
            'old_plan_id': self.old_plan_id,
            'old_status': self.old_status,
            'old_end_date': self.old_end_date.isoformat() if self.old_end_date else None,
            'new_plan_id': self.new_plan_id,
            'new_status': self.new_status,
            'new_end_date': self.new_end_date.isoformat() if self.new_end_date else None,
            'description': self.description,
            'metadata': self.metadata,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat(),
            'old_plan': self.old_plan.to_dict() if self.old_plan else None,
            'new_plan': self.new_plan.to_dict() if self.new_plan else None
        }
    
    @staticmethod
    def log_action(user_id, action, subscription_id=None, old_plan_id=None, new_plan_id=None, 
                   old_status=None, new_status=None, old_end_date=None, new_end_date=None,
                   description=None, metadata=None, ip_address=None, user_agent=None):
        """Статический метод для логирования действия"""
        
        history_entry = SubscriptionHistory(
            user_id=user_id,
            subscription_id=subscription_id,
            action=action,
            old_plan_id=old_plan_id,
            new_plan_id=new_plan_id,
            old_status=old_status,
            new_status=new_status,
            old_end_date=old_end_date,
            new_end_date=new_end_date,
            description=description,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(history_entry)
        db.session.commit()
        
        return history_entry
    
    @staticmethod
    def get_user_history(user_id, limit=50, offset=0):
        """Получить историю подписок пользователя"""
        return SubscriptionHistory.query.filter_by(user_id=user_id)\
            .order_by(SubscriptionHistory.created_at.desc())\
            .limit(limit).offset(offset).all()
    
    @staticmethod
    def get_subscription_history(subscription_id, limit=50, offset=0):
        """Получить историю конкретной подписки"""
        return SubscriptionHistory.query.filter_by(subscription_id=subscription_id)\
            .order_by(SubscriptionHistory.created_at.desc())\
            .limit(limit).offset(offset).all()
    
    def get_action_description(self):
        """Получить читаемое описание действия"""
        descriptions = {
            HistoryAction.CREATED: 'Подписка создана',
            HistoryAction.ACTIVATED: 'Подписка активирована',
            HistoryAction.CANCELLED: 'Подписка отменена',
            HistoryAction.SUSPENDED: 'Подписка приостановлена',
            HistoryAction.REACTIVATED: 'Подписка возобновлена',
            HistoryAction.EXPIRED: 'Подписка истекла',
            HistoryAction.UPGRADED: 'Подписка обновлена',
            HistoryAction.DOWNGRADED: 'Подписка понижена',
            HistoryAction.RENEWED: 'Подписка продлена',
            HistoryAction.PAYMENT_SUCCESS: 'Оплата прошла успешно',
            HistoryAction.PAYMENT_FAILED: 'Оплата не удалась',
            HistoryAction.TRIAL_STARTED: 'Начался пробный период',
            HistoryAction.TRIAL_ENDED: 'Пробный период закончился',
            HistoryAction.GRACE_PERIOD_STARTED: 'Начался льготный период',
            HistoryAction.GRACE_PERIOD_ENDED: 'Льготный период закончился'
        }
        
        return descriptions.get(self.action, f'Неизвестное действие: {self.action.value}')
    
    def get_detailed_description(self):
        """Получить детальное описание изменения"""
        if self.description:
            return self.description
        
        action_desc = self.get_action_description()
        
        if self.action in [HistoryAction.UPGRADED, HistoryAction.DOWNGRADED]:
            old_plan_name = self.old_plan.display_name if self.old_plan else 'Неизвестный план'
            new_plan_name = self.new_plan.display_name if self.new_plan else 'Неизвестный план'
            return f'{action_desc}: с "{old_plan_name}" на "{new_plan_name}"'
        
        if self.action in [HistoryAction.PAYMENT_SUCCESS, HistoryAction.PAYMENT_FAILED]:
            plan_name = self.new_plan.display_name if self.new_plan else 'Неизвестный план'
            return f'{action_desc} для плана "{plan_name}"'
        
        if self.old_status and self.new_status and self.old_status != self.new_status:
            return f'{action_desc}: статус изменен с "{self.old_status}" на "{self.new_status}"'
        
        return action_desc