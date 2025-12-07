from models.imp import db
from datetime import datetime, timedelta
import enum


class LimitType(enum.Enum):
    """Типы лимитов"""
    MESSAGES_PER_MONTH = "messages_per_month"
    MESSAGES_PER_DAY = "messages_per_day"
    BOTS_COUNT = "bots_count"
    STORAGE_MB = "storage_mb"
    TEAM_MEMBERS = "team_members"
    API_CALLS_PER_MONTH = "api_calls_per_month"
    API_CALLS_PER_DAY = "api_calls_per_day"
    WEBHOOKS_COUNT = "webhooks_count"
    ANALYTICS_DAYS = "analytics_days"
    BACKUP_DAYS = "backup_days"
    CUSTOM_TEMPLATES = "custom_templates"


class LimitPeriod(enum.Enum):
    """Периоды лимитов"""
    DAILY = "daily"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"
    CUSTOM = "custom"


class UsageLimit(db.Model):
    """Модель лимитов использования"""
    __tablename__ = 'usage_limits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('user_subscriptions.id'), nullable=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=True)
    
    # Тип и период лимита
    limit_type = db.Column(db.Enum(LimitType), nullable=False)
    limit_period = db.Column(db.Enum(LimitPeriod), default=LimitPeriod.MONTHLY)
    
    # Значения лимита
    limit_value = db.Column(db.Integer, nullable=False)  # Максимальное значение (-1 = безлимит)
    current_usage = db.Column(db.Integer, default=0)  # Текущее использование
    warning_threshold = db.Column(db.Integer, default=80)  # Порог предупреждения в процентах
    
    # Период действия
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    # Настройки
    is_hard_limit = db.Column(db.Boolean, default=True)  # Жесткий лимит (true) или мягкий (false)
    auto_reset = db.Column(db.Boolean, default=True)  # Автоматический сброс
    rollover_enabled = db.Column(db.Boolean, default=False)  # Перенос неиспользованного лимита
    rollover_percentage = db.Column(db.Integer, default=0)  # Процент переноса
    
    # Статус
    is_active = db.Column(db.Boolean, default=True)
    last_reset_at = db.Column(db.DateTime)
    
    # Описание и примечания
    description = db.Column(db.String(500))
    notes = db.Column(db.Text)
    
    # Системные поля
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    usage_trackers = db.relationship('UsageTracker', backref='usage_limit', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<UsageLimit user_id={self.user_id} type={self.limit_type.value} limit={self.limit_value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subscription_id': self.subscription_id,
            'plan_id': self.plan_id,
            'limit_type': self.limit_type.value,
            'limit_period': self.limit_period.value,
            'limit_value': self.limit_value,
            'current_usage': self.current_usage,
            'warning_threshold': self.warning_threshold,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'is_hard_limit': self.is_hard_limit,
            'auto_reset': self.auto_reset,
            'rollover_enabled': self.rollover_enabled,
            'rollover_percentage': self.rollover_percentage,
            'is_active': self.is_active,
            'last_reset_at': self.last_reset_at.isoformat() if self.last_reset_at else None,
            'description': self.description,
            'usage_percentage': self.get_usage_percentage(),
            'remaining': self.get_remaining(),
            'is_unlimited': self.is_unlimited()
        }
    
    def get_usage_percentage(self):
        """Получить процент использования"""
        if self.is_unlimited():
            return 0
        
        if self.limit_value == 0:
            return 100 if self.current_usage > 0 else 0
        
        return min(100, (self.current_usage / self.limit_value) * 100)
    
    def get_remaining(self):
        """Получить оставшееся количество"""
        if self.is_unlimited():
            return -1
        
        return max(0, self.limit_value - self.current_usage)
    
    def is_unlimited(self):
        """Проверить, безлимитный ли лимит"""
        return self.limit_value == -1
    
    def is_limit_reached(self):
        """Проверить, достигнут ли лимит"""
        if self.is_unlimited():
            return False
        
        if self.is_hard_limit:
            return self.current_usage >= self.limit_value
        else:
            # Для мягкого лимита можно превышать на 10%
            return self.current_usage >= (self.limit_value * 1.1)
    
    def is_warning_threshold_reached(self):
        """Проверить, достигнут ли порог предупреждения"""
        if self.is_unlimited():
            return False
        
        return self.get_usage_percentage() >= self.warning_threshold
    
    def increment_usage(self, amount=1):
        """Увеличить использование"""
        if amount <= 0:
            return False
        
        if self.is_limit_reached() and self.is_hard_limit:
            return False
        
        self.current_usage += amount
        self.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    def decrement_usage(self, amount=1):
        """Уменьшить использование"""
        if amount <= 0:
            return False
        
        self.current_usage = max(0, self.current_usage - amount)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    def reset_usage(self):
        """Сбросить использование"""
        # Рассчитать rollover если включен
        rollover_amount = 0
        if self.rollover_enabled and self.rollover_percentage > 0:
            remaining = self.get_remaining()
            if remaining > 0:
                rollover_amount = int(remaining * (self.rollover_percentage / 100))
        
        self.current_usage = rollover_amount
        self.last_reset_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.session.commit()
        
        return rollover_amount
    
    def extend_period(self, days=0, months=0):
        """Продлить период действия лимита"""
        if days > 0:
            self.period_end += timedelta(days=days)
        
        if months > 0:
            self.period_end += timedelta(days=months * 30)  # Приблизительно
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_limit(self, new_limit_value, description=None):
        """Обновить значение лимита"""
        old_value = self.limit_value
        self.limit_value = new_limit_value
        
        if description:
            self.description = description
        
        # Если новый лимит меньше текущего использования, сбросить использование
        if not self.is_unlimited() and self.current_usage > new_limit_value:
            self.current_usage = new_limit_value
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
        
        return old_value
    
    def is_period_active(self):
        """Проверить, активен ли текущий период"""
        now = datetime.utcnow()
        return self.period_start <= now <= self.period_end
    
    def get_days_until_reset(self):
        """Получить количество дней до сброса"""
        if not self.period_end:
            return None
        
        delta = self.period_end - datetime.utcnow()
        return max(0, delta.days)
    
    @staticmethod
    def create_limit(user_id, limit_type, limit_value, period='monthly', subscription_id=None, 
                     plan_id=None, description=None, is_hard_limit=True, warning_threshold=80):
        """Создать новый лимит"""
        now = datetime.utcnow()
        
        # Определить период
        if period == 'daily':
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif period == 'monthly':
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = period_start.replace(day=28) + timedelta(days=4)  # Надежный способ получить следующий месяц
            period_end = next_month.replace(day=1)
        elif period == 'yearly':
            period_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start.replace(year=period_start.year + 1)
        else:  # lifetime or custom
            period_start = now
            period_end = now.replace(year=now.year + 10)  # 10 лет по умолчанию
        
        usage_limit = UsageLimit(
            user_id=user_id,
            subscription_id=subscription_id,
            plan_id=plan_id,
            limit_type=limit_type,
            limit_period=period,
            limit_value=limit_value,
            period_start=period_start,
            period_end=period_end,
            description=description,
            is_hard_limit=is_hard_limit,
            warning_threshold=warning_threshold
        )
        
        db.session.add(usage_limit)
        db.session.commit()
        
        return usage_limit
    
    @staticmethod
    def get_user_limits(user_id, limit_type=None, active_only=True):
        """Получить лимиты пользователя"""
        query = UsageLimit.query.filter_by(user_id=user_id)
        
        if limit_type:
            query = query.filter_by(limit_type=limit_type)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.order_by(UsageLimit.created_at.desc()).all()
    
    @staticmethod
    def get_user_limit_for_subscription(user_id, subscription_id, limit_type):
        """Получить лимит для конкретной подписки"""
        return UsageLimit.query.filter_by(
            user_id=user_id,
            subscription_id=subscription_id,
            limit_type=limit_type,
            is_active=True
        ).first()
    
    @staticmethod
    def reset_user_limits(user_id, limit_type=None):
        """Сбросить лимиты пользователя"""
        limits = UsageLimit.get_user_limits(user_id, limit_type)
        
        for limit in limits:
            if limit.auto_reset:
                limit.reset_usage()
        
        return len(limits)