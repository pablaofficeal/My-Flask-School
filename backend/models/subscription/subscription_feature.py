from models.imp import db
from datetime import datetime


class SubscriptionFeature(db.Model):
    """Модель функций подписки"""
    __tablename__ = 'subscription_features'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    
    # Название и описание функции
    feature_key = db.Column(db.String(100), nullable=False)  # Уникальный ключ функции
    display_name = db.Column(db.String(200), nullable=False)  # Отображаемое название
    description = db.Column(db.Text)  # Описание функции
    
    # Параметры функции
    is_enabled = db.Column(db.Boolean, default=True)  # Включена ли функция
    value = db.Column(db.String(500))  # Значение функции (если есть)
    limit_value = db.Column(db.Integer)  # Лимит (если применимо)
    unit = db.Column(db.String(50))  # Единица измерения (messages, GB, etc.)
    
    # Категория и приоритет
    category = db.Column(db.String(50), default='general')  # Категория функции
    priority = db.Column(db.Integer, default=0)  # Приоритет отображения
    
    # Иконка и визуальные элементы
    icon_class = db.Column(db.String(100))  # CSS класс иконки
    color = db.Column(db.String(20))  # Цвет для визуального выделения
    
    # Системные поля
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SubscriptionFeature {self.feature_key} for plan {self.plan_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'feature_key': self.feature_key,
            'display_name': self.display_name,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'value': self.value,
            'limit_value': self.limit_value,
            'unit': self.unit,
            'category': self.category,
            'priority': self.priority,
            'icon_class': self.icon_class,
            'color': self.color
        }
    
    @staticmethod
    def get_standard_features():
        """Получить стандартный набор функций для подписок"""
        return [
            # Базовые функции
            {
                'feature_key': 'bot_creation',
                'display_name': 'Создание ботов',
                'description': 'Возможность создавать чат-ботов',
                'category': 'core',
                'priority': 1
            },
            {
                'feature_key': 'basic_templates',
                'display_name': 'Базовые шаблоны',
                'description': 'Доступ к базовым шаблонам ботов',
                'category': 'templates',
                'priority': 2
            },
            {
                'feature_key': 'basic_analytics',
                'display_name': 'Базовая аналитика',
                'description': 'Базовая статистика использования ботов',
                'category': 'analytics',
                'priority': 3
            },
            
            # Продвинутые функции
            {
                'feature_key': 'advanced_templates',
                'display_name': 'Продвинутые шаблоны',
                'description': 'Доступ к продвинутым шаблонам и кастомизация',
                'category': 'templates',
                'priority': 4
            },
            {
                'feature_key': 'ai_training',
                'display_name': 'Обучение ИИ',
                'description': 'Возможность обучать ботов на своих данных',
                'category': 'ai',
                'priority': 5
            },
            {
                'feature_key': 'advanced_analytics',
                'display_name': 'Расширенная аналитика',
                'description': 'Детальная аналитика и отчеты',
                'category': 'analytics',
                'priority': 6
            },
            {
                'feature_key': 'api_access',
                'display_name': 'API доступ',
                'description': 'Доступ к API для интеграций',
                'category': 'integrations',
                'priority': 7
            },
            {
                'feature_key': 'webhook_access',
                'display_name': 'Вебхуки',
                'description': 'Возможность настройки вебхуков',
                'category': 'integrations',
                'priority': 8
            },
            
            # Командные функции
            {
                'feature_key': 'team_management',
                'display_name': 'Управление командой',
                'description': 'Возможность добавлять членов команды',
                'category': 'team',
                'priority': 9
            },
            {
                'feature_key': 'role_management',
                'display_name': 'Управление ролями',
                'description': 'Настройка ролей и прав доступа',
                'category': 'team',
                'priority': 10
            },
            
            # Поддержка и безопасность
            {
                'feature_key': 'priority_support',
                'display_name': 'Приоритетная поддержка',
                'description': 'Быстрая техническая поддержка',
                'category': 'support',
                'priority': 11
            },
            {
                'feature_key': 'security_audit',
                'display_name': 'Аудит безопасности',
                'description': 'Расширенные функции безопасности',
                'category': 'security',
                'priority': 12
            },
            
            # Кастомизация
            {
                'feature_key': 'custom_branding',
                'display_name': 'Кастомный брендинг',
                'description': 'Возможность настройки внешнего вида',
                'category': 'customization',
                'priority': 13
            },
            {
                'feature_key': 'white_label',
                'display_name': 'White Label',
                'description': 'Полная кастомизация под свой бренд',
                'category': 'customization',
                'priority': 14
            },
            
            # Резервное копирование
            {
                'feature_key': 'backup_restore',
                'display_name': 'Резервное копирование',
                'description': 'Автоматическое резервное копирование данных',
                'category': 'backup',
                'priority': 15
            },
            {
                'feature_key': 'export_data',
                'display_name': 'Экспорт данных',
                'description': 'Возможность экспорта всех данных',
                'category': 'backup',
                'priority': 16
            }
        ]
    
    @staticmethod
    def get_feature_icon(feature_key):
        """Получить иконку для функции"""
        icons = {
            'bot_creation': 'fas fa-robot',
            'basic_templates': 'fas fa-file-alt',
            'basic_analytics': 'fas fa-chart-bar',
            'advanced_templates': 'fas fa-layer-group',
            'ai_training': 'fas fa-brain',
            'advanced_analytics': 'fas fa-chart-line',
            'api_access': 'fas fa-plug',
            'webhook_access': 'fas fa-link',
            'team_management': 'fas fa-users',
            'role_management': 'fas fa-user-shield',
            'priority_support': 'fas fa-headset',
            'security_audit': 'fas fa-shield-alt',
            'custom_branding': 'fas fa-palette',
            'white_label': 'fas fa-tag',
            'backup_restore': 'fas fa-history',
            'export_data': 'fas fa-download'
        }
        return icons.get(feature_key, 'fas fa-check')
    
    @staticmethod
    def get_feature_color(feature_key):
        """Получить цвет для функции"""
        colors = {
            'bot_creation': 'primary',
            'basic_templates': 'info',
            'basic_analytics': 'success',
            'advanced_templates': 'warning',
            'ai_training': 'danger',
            'advanced_analytics': 'dark',
            'api_access': 'secondary',
            'webhook_access': 'info',
            'team_management': 'primary',
            'role_management': 'warning',
            'priority_support': 'success',
            'security_audit': 'danger',
            'custom_branding': 'purple',
            'white_label': 'orange',
            'backup_restore': 'info',
            'export_data': 'secondary'
        }
        return colors.get(feature_key, 'success')