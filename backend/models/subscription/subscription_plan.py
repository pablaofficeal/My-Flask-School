from models.imp import db
from datetime import datetime
from sqlalchemy import Numeric


class SubscriptionPlan(db.Model):
    """Модель плана подписки"""
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # free, basic, premium, business
    display_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(Numeric(10, 2), nullable=False)  # Цена в валюте
    currency = db.Column(db.String(3), default='USD')
    billing_cycle = db.Column(db.String(20), nullable=False)  # monthly, yearly, lifetime
    
    # Статус плана
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=True)  # Показывать ли план публично
    sort_order = db.Column(db.Integer, default=0)  # Порядок сортировки
    
    # Лимиты использования
    max_bots = db.Column(db.Integer, default=1)
    max_messages_per_month = db.Column(db.Integer, default=100)
    max_storage_mb = db.Column(db.Integer, default=100)  # Максимальный объем хранилища в МБ
    max_team_members = db.Column(db.Integer, default=1)
    
    # Функции
    has_api_access = db.Column(db.Boolean, default=False)
    has_webhook_access = db.Column(db.Boolean, default=False)
    has_advanced_analytics = db.Column(db.Boolean, default=False)
    has_priority_support = db.Column(db.Boolean, default=False)
    has_custom_branding = db.Column(db.Boolean, default=False)
    has_white_label = db.Column(db.Boolean, default=False)
    
    # Сроки и условия
    trial_days = db.Column(db.Integer, default=0)  # Количество дней пробного периода
    grace_period_days = db.Column(db.Integer, default=3)  # Льготный период после окончания
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    user_subscriptions = db.relationship('UserSubscription', backref='plan', lazy='dynamic')
    features = db.relationship('SubscriptionFeature', backref='plan', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SubscriptionPlan {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'price': float(self.price),
            'currency': self.currency,
            'billing_cycle': self.billing_cycle,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'max_bots': self.max_bots,
            'max_messages_per_month': self.max_messages_per_month,
            'max_storage_mb': self.max_storage_mb,
            'max_team_members': self.max_team_members,
            'has_api_access': self.has_api_access,
            'has_webhook_access': self.has_webhook_access,
            'has_advanced_analytics': self.has_advanced_analytics,
            'has_priority_support': self.has_priority_support,
            'has_custom_branding': self.has_custom_branding,
            'has_white_label': self.has_white_label,
            'trial_days': self.trial_days,
            'grace_period_days': self.grace_period_days,
            'features': [feature.to_dict() for feature in self.features]
        }
    
    def get_price_for_cycle(self, cycle=None):
        """Получить цену для указанного цикла биллинга"""
        if cycle is None:
            cycle = self.billing_cycle
        
        # Если запрашиваемый цикл совпадает с базовым
        if cycle == self.billing_cycle:
            return self.price
        
        # Пересчет для других циклов
        if cycle == 'yearly' and self.billing_cycle == 'monthly':
            # Годовая подписка со скидкой 20%
            return self.price * 12 * 0.8
        elif cycle == 'monthly' and self.billing_cycle == 'yearly':
            # Месячная подписка без скидки
            return self.price / 12
        
        return self.price
    
    def is_available_for_user(self, user):
        """Проверить, доступен ли план для пользователя"""
        if not self.is_active or not self.is_public:
            return False
        
        # Проверка специальных условий
        if self.name == 'free':
            return True
        
        return True