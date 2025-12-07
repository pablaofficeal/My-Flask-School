from models.imp import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    role = db.Column(db.String(20), default='user')  # user, moderator, admin, super_admin

    subscription_type = db.Column(db.String(20), default='free')  # free, premium, business
    subscription_expires = db.Column(db.DateTime)

    # Связь с транзакциями
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    # Связь с лимитами
    limits = db.relationship('Limit', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def activate(self):
        self.is_active = True
        self.last_login = datetime.utcnow()
        db.session.commit()

    def deactivate(self):
        self.is_active = False
        db.session.commit()
    def promote_to_admin(self):
        self.is_admin = True
        db.session.commit()
    
    def is_admin(self):
        """Проверить, является ли пользователь администратором"""
        return self.role in ['admin', 'super_admin', 'creater']
    
    def is_moderator(self):
        """Проверить, является ли пользователь модератором"""
        return self.role in ['moderator', 'admin', 'super_admin', 'creater']
    
    def is_super_admin(self):
        """Проверить, является ли пользователь супер-администратором"""
        return self.role == 'super_admin'
    
    def can_manage_users(self):
        """Проверить, может ли пользователь управлять другими пользователями (изменять роли и т.д.)"""
        return self.role in ['admin', 'super_admin', 'creater']
    
    def can_ban_users(self):
        """Проверить, может ли пользователь банить других пользователей"""
        return self.role in ['moderator', 'admin', 'super_admin', 'creater']
    
    def can_manage_templates(self):
        """Проверить, может ли пользователь управлять шаблонами"""
        return self.role in ['moderator', 'admin', 'super_admin', 'creater']
    
    def can_view_admin_panel(self):
        """Проверить, может ли пользователь видеть админ-панель"""
        return self.role in ['moderator', 'admin', 'super_admin', 'creater']
