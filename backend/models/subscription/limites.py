from models.imp import db
from datetime import datetime

class Limit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_type = db.Column(db.String(20), default='free')  # free, premium, business
    subscription_expires = db.Column(db.DateTime)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    status = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, subscription_type, amount, currency, status):
        self.user_id = user_id
        self.subscription_type = subscription_type
        self.amount = amount
        self.currency = currency
        self.status = status

        self.created_at = datetime.utcnow()

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<Limit {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subscription_type': self.subscription_type,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'created_at': self.created_at
        }
    
    def get_bot_limit(self):
        """Получить лимит ботов для пользователя"""
        limits = {
            'free': 20,
            'go': 500,
            'premium': 1000,
            'business': 5000,
        }
        return limits.get(self.subscription, 50)
    
    def can_create_bot(self):
        """Проверить, может ли пользователь создать нового бота"""
        return self.bots_created_this_month < self.get_bot_limit()
    
    def get_bot_limit(self):
        """Получить лимит ботов для пользователя"""
        limits = {
            'free': 20,
            'go': 500,
            'premium': 1000,
            'business': 5000,
        }
        return limits.get(self.subscription_type, 50)
