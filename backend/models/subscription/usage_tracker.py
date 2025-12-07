from models.imp import db
from datetime import datetime
import enum


class UsageType(enum.Enum):
    """Типы использования"""
    MESSAGE = "message"
    BOT_CREATION = "bot_creation"
    BOT_UPDATE = "bot_update"
    BOT_DELETION = "bot_deletion"
    API_CALL = "api_call"
    WEBHOOK_CALL = "webhook_call"
    STORAGE_UPLOAD = "storage_upload"
    STORAGE_DOWNLOAD = "storage_download"
    TEMPLATE_CREATION = "template_creation"
    TEMPLATE_USAGE = "template_usage"
    ANALYTICS_QUERY = "analytics_query"
    BACKUP_CREATION = "backup_creation"
    TEAM_MEMBER_ADDED = "team_member_added"
    TEAM_MEMBER_REMOVED = "team_member_removed"
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"


class UsageTracker(db.Model):
    """Модель отслеживания использования"""
    __tablename__ = 'usage_trackers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('user_subscriptions.id'), nullable=True)
    limit_id = db.Column(db.Integer, db.ForeignKey('usage_limits.id'), nullable=True)
    
    # Тип использования
    usage_type = db.Column(db.Enum(UsageType), nullable=False)
    
    # Детали использования
    resource_id = db.Column(db.String(100))  # ID ресурса (бота, шаблона и т.д.)
    resource_type = db.Column(db.String(50))  # Тип ресурса
    action = db.Column(db.String(100))  # Действие (create, update, delete и т.д.)
    
    # Количественные показатели
    quantity = db.Column(db.Integer, default=1)  # Количество использований
    cost = db.Column(db.Decimal(10, 4), default=0)  # "Стоимость" в единицах лимита
    size_bytes = db.Column(db.BigInteger, default=0)  # Размер в байтах (для хранилища)
    
    # Метаданные
    metadata = db.Column(db.JSON)  # Дополнительные данные
    tags = db.Column(db.String(500))  # Теги для фильтрации
    
    # Геолокация и клиент
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    country = db.Column(db.String(2))  # ISO код страны
    city = db.Column(db.String(100))
    
    # Производительность
    execution_time_ms = db.Column(db.Integer)  # Время выполнения в миллисекундах
    memory_usage_mb = db.Column(db.Integer)  # Использование памяти в МБ
    
    # Статус
    status = db.Column(db.String(50), default='success')  # success, failed, pending
    error_message = db.Column(db.Text)  # Сообщение об ошибке
    
    # Системные поля
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)  # Время обработки
    
    # Связи
    user = db.relationship('User', backref='usage_trackers', lazy=True)
    
    def __repr__(self):
        return f'<UsageTracker user_id={self.user_id} type={self.usage_type.value} quantity={self.quantity}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subscription_id': self.subscription_id,
            'limit_id': self.limit_id,
            'usage_type': self.usage_type.value,
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'action': self.action,
            'quantity': self.quantity,
            'cost': float(self.cost) if self.cost else 0,
            'size_bytes': self.size_bytes,
            'metadata': self.metadata,
            'tags': self.tags.split(',') if self.tags else [],
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'country': self.country,
            'city': self.city,
            'execution_time_ms': self.execution_time_ms,
            'memory_usage_mb': self.memory_usage_mb,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
    
    def mark_as_processed(self):
        """Отметить использование как обработанное"""
        self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_failed(self, error_message=None):
        """Отметить использование как неудачное"""
        self.status = 'failed'
        if error_message:
            self.error_message = error_message
        self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def add_tags(self, tags):
        """Добавить теги"""
        if isinstance(tags, list):
            tags_str = ','.join(tags)
        else:
            tags_str = str(tags)
        
        if self.tags:
            self.tags += f',{tags_str}'
        else:
            self.tags = tags_str
        
        db.session.commit()
    
    @staticmethod
    def track_usage(user_id, usage_type, quantity=1, cost=0, resource_id=None, 
                   resource_type=None, action=None, metadata=None, subscription_id=None,
                   limit_id=None, ip_address=None, user_agent=None, execution_time_ms=None,
                   status='success', error_message=None):
        """Статический метод для отслеживания использования"""
        
        tracker = UsageTracker(
            user_id=user_id,
            subscription_id=subscription_id,
            limit_id=limit_id,
            usage_type=usage_type,
            quantity=quantity,
            cost=cost,
            resource_id=resource_id,
            resource_type=resource_type,
            action=action,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            execution_time_ms=execution_time_ms,
            status=status,
            error_message=error_message
        )
        
        # Извлечь геолокацию из IP (если доступно)
        if ip_address:
            try:
                # Здесь можно подключить сервис геолокации
                # Пока используем заглушку
                tracker.country = 'US'  # Заглушка
                tracker.city = 'Unknown'
            except:
                pass
        
        db.session.add(tracker)
        db.session.commit()
        
        return tracker
    
    @staticmethod
    def get_user_usage_stats(user_id, start_date=None, end_date=None, usage_type=None):
        """Получить статистику использования пользователя"""
        query = UsageTracker.query.filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(UsageTracker.created_at >= start_date)
        
        if end_date:
            query = query.filter(UsageTracker.created_at <= end_date)
        
        if usage_type:
            query = query.filter_by(usage_type=usage_type)
        
        # Агрегированная статистика
        stats = {
            'total_usage': query.count(),
            'successful_usage': query.filter_by(status='success').count(),
            'failed_usage': query.filter_by(status='failed').count(),
            'total_cost': 0,
            'total_size_bytes': 0,
            'average_execution_time': 0,
            'usage_by_type': {},
            'daily_usage': []
        }
        
        # Суммарные значения
        results = query.all()
        if results:
            stats['total_cost'] = sum(float(r.cost or 0) for r in results)
            stats['total_size_bytes'] = sum(r.size_bytes or 0 for r in results)
            
            execution_times = [r.execution_time_ms for r in results if r.execution_time_ms]
            if execution_times:
                stats['average_execution_time'] = sum(execution_times) / len(execution_times)
        
        # Использование по типам
        usage_by_type_query = db.session.query(
            UsageTracker.usage_type,
            db.func.count(UsageTracker.id).label('count'),
            db.func.sum(UsageTracker.quantity).label('total_quantity'),
            db.func.sum(UsageTracker.cost).label('total_cost')
        ).filter_by(user_id=user_id)
        
        if start_date:
            usage_by_type_query = usage_by_type_query.filter(UsageTracker.created_at >= start_date)
        
        if end_date:
            usage_by_type_query = usage_by_type_query.filter(UsageTracker.created_at <= end_date)
        
        usage_by_type = usage_by_type_query.group_by(UsageTracker.usage_type).all()
        
        for usage_type, count, total_quantity, total_cost in usage_by_type:
            stats['usage_by_type'][usage_type.value] = {
                'count': count,
                'total_quantity': int(total_quantity or 0),
                'total_cost': float(total_cost or 0)
            }
        
        return stats
    
    @staticmethod
    def get_resource_usage(resource_id, resource_type=None, start_date=None, end_date=None):
        """Получить использование конкретного ресурса"""
        query = UsageTracker.query.filter_by(resource_id=resource_id)
        
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        
        if start_date:
            query = query.filter(UsageTracker.created_at >= start_date)
        
        if end_date:
            query = query.filter(UsageTracker.created_at <= end_date)
        
        return query.order_by(UsageTracker.created_at.desc()).all()
    
    @staticmethod
    def cleanup_old_records(days_to_keep=90):
        """Очистить старые записи"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = UsageTracker.query.filter(
            UsageTracker.created_at < cutoff_date,
            UsageTracker.status == 'success'  # Удаляем только успешные записи
        ).delete()
        
        db.session.commit()
        return deleted_count