from models.imp import db
from datetime import datetime, timedelta
import enum


class SubscriptionStatus(enum.Enum):
    """Статусы подписки"""
    ACTIVE = "active"
    TRIAL = "trial"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    PENDING = "pending"
    GRACE_PERIOD = "grace_period"


class UserSubscription(db.Model):
    """Модель подписки пользователя"""
    __tablename__ = 'user_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    
    # Статус подписки
    status = db.Column(db.Enum(SubscriptionStatus), default=SubscriptionStatus.PENDING)
    
    # Даты
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)  # Дата окончания подписки
    trial_end_date = db.Column(db.DateTime)  # Дата окончания пробного периода
    grace_period_end = db.Column(db.DateTime)  # Дата окончания льготного периода
    
    # Даты управления
    cancelled_at = db.Column(db.DateTime)  # Дата отмены
    suspended_at = db.Column(db.DateTime)  # Дата приостановки
    reactivated_at = db.Column(db.DateTime)  # Дата повторной активации
    
    # Параметры подписки
    auto_renew = db.Column(db.Boolean, default=True)  # Автоматическое продление
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, yearly
    currency = db.Column(db.String(3), default='USD')
    price_paid = db.Column(db.Decimal(10, 2))  # Фактическая цена оплаты
    
    # Использование
    bots_created = db.Column(db.Integer, default=0)  # Количество созданных ботов
    messages_used_this_cycle = db.Column(db.Integer, default=0)  # Использовано сообщений в текущем цикле
    storage_used_mb = db.Column(db.Integer, default=0)  # Использовано хранилища в МБ
    
    # Метаданные
    notes = db.Column(db.Text)  # Примечания
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    transactions = db.relationship('Transaction', backref='user_subscription', lazy='dynamic')
    usage_trackers = db.relationship('UsageTracker', backref='user_subscription', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<UserSubscription user_id={self.user_id} plan_id={self.plan_id} status={self.status.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'status': self.status.value,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'trial_end_date': self.trial_end_date.isoformat() if self.trial_end_date else None,
            'grace_period_end': self.grace_period_end.isoformat() if self.grace_period_end else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'auto_renew': self.auto_renew,
            'billing_cycle': self.billing_cycle,
            'currency': self.currency,
            'price_paid': float(self.price_paid) if self.price_paid else None,
            'bots_created': self.bots_created,
            'messages_used_this_cycle': self.messages_used_this_cycle,
            'storage_used_mb': self.storage_used_mb,
            'plan': self.plan.to_dict() if self.plan else None
        }
    
    def is_active(self):
        """Проверить, активна ли подписка"""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]
    
    def is_expired(self):
        """Проверить, истекла ли подписка"""
        if self.end_date and datetime.utcnow() > self.end_date:
            return True
        if self.trial_end_date and self.status == SubscriptionStatus.TRIAL and datetime.utcnow() > self.trial_end_date:
            return True
        return False
    
    def is_in_grace_period(self):
        """Проверить, находится ли подписка в льготном периоде"""
        if self.grace_period_end:
            return datetime.utcnow() <= self.grace_period_end
        return False
    
    def can_renew(self):
        """Можно ли продлить подписку"""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.EXPIRED, SubscriptionStatus.GRACE_PERIOD]
    
    def get_days_until_expiry(self):
        """Получить количество дней до окончания подписки"""
        if not self.end_date:
            return None
        
        delta = self.end_date - datetime.utcnow()
        return max(0, delta.days)
    
    def get_usage_percentage(self, limit_type='messages'):
        """Получить процент использования лимитов"""
        if not self.plan:
            return 0
        
        if limit_type == 'messages':
            limit = self.plan.max_messages_per_month
            used = self.messages_used_this_cycle
        elif limit_type == 'bots':
            limit = self.plan.max_bots
            used = self.bots_created
        elif limit_type == 'storage':
            limit = self.plan.max_storage_mb
            used = self.storage_used_mb
        else:
            return 0
        
        if limit == 0:
            return 100 if used > 0 else 0
        
        return min(100, (used / limit) * 100)
    
    def update_usage(self, usage_type, amount=1):
        """Обновить использование"""
        if usage_type == 'messages':
            self.messages_used_this_cycle += amount
        elif usage_type == 'bots':
            self.bots_created += amount
        elif usage_type == 'storage':
            self.storage_used_mb += amount
        
        db.session.commit()
    
    def reset_monthly_usage(self):
        """Сбросить ежемесячное использование"""
        self.messages_used_this_cycle = 0
        db.session.commit()
    
    def activate(self):
        """Активировать подписку"""
        self.status = SubscriptionStatus.ACTIVE
        self.reactivated_at = datetime.utcnow()
        db.session.commit()
    
    def cancel(self):
        """Отменить подписку"""
        self.status = SubscriptionStatus.CANCELLED
        self.cancelled_at = datetime.utcnow()
        self.auto_renew = False
        db.session.commit()
    
    def suspend(self, reason=None):
        """Приостановить подписку"""
        self.status = SubscriptionStatus.SUSPENDED
        self.suspended_at = datetime.utcnow()
        if reason:
            self.notes = f"Приостановлено: {reason}"
        db.session.commit()
    
    def reactivate(self):
        """Повторно активировать подписку"""
        if self.status == SubscriptionStatus.SUSPENDED:
            self.status = SubscriptionStatus.ACTIVE
            self.reactivated_at = datetime.utcnow()
            db.session.commit()
    
    def check_and_update_status(self):
        """Проверить и обновить статус подписки"""
        now = datetime.utcnow()
        
        # Проверка пробного периода
        if self.status == SubscriptionStatus.TRIAL and self.trial_end_date and now > self.trial_end_date:
            self.status = SubscriptionStatus.EXPIRED
            db.session.commit()
            return
        
        # Проверка льготного периода
        if self.status == SubscriptionStatus.GRACE_PERIOD and self.grace_period_end and now > self.grace_period_end:
            self.status = SubscriptionStatus.EXPIRED
            db.session.commit()
            return
        
        # Проверка окончания подписки
        if self.status == SubscriptionStatus.ACTIVE and self.end_date and now > self.end_date:
            if self.grace_period_end and now <= self.grace_period_end:
                self.status = SubscriptionStatus.GRACE_PERIOD
            else:
                self.status = SubscriptionStatus.EXPIRED
            db.session.commit()
            return