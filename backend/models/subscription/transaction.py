from models.imp import db
from datetime import datetime
import enum


class TransactionStatus(enum.Enum):
    """Статусы транзакций"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    CHARGEBACK = "chargeback"


class TransactionType(enum.Enum):
    """Типы транзакций"""
    SUBSCRIPTION_PAYMENT = "subscription_payment"
    SUBSCRIPTION_RENEWAL = "subscription_renewal"
    SUBSCRIPTION_UPGRADE = "subscription_upgrade"
    SUBSCRIPTION_DOWNGRADE = "subscription_downgrade"
    REFUND = "refund"
    TRIAL_TO_PAID = "trial_to_paid"
    MANUAL_PAYMENT = "manual_payment"


class PaymentMethod(enum.Enum):
    """Методы оплаты"""
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    MANUAL = "manual"


class Transaction(db.Model):
    """Расширенная модель транзакций"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('user_subscriptions.id'), nullable=True)
    
    # Тип и статус транзакции
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    status = db.Column(db.Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    # Финансовые детали
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # Сумма
    currency = db.Column(db.String(3), default='USD')  # Валюта
    tax_amount = db.Column(db.Numeric(10, 2), default=0)  # Налог
    discount_amount = db.Column(db.Numeric(10, 2), default=0)  # Скидка
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)  # Итоговая сумма
    
    # План подписки
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=True)
    billing_cycle = db.Column(db.String(20))  # monthly, yearly
    
    # Платежная информация
    payment_method = db.Column(db.Enum(PaymentMethod))
    payment_provider = db.Column(db.String(50))  # stripe, paypal и т.д.
    payment_provider_transaction_id = db.Column(db.String(100))  # ID транзакции в платежной системе
    
    # Внешние идентификаторы
    invoice_id = db.Column(db.String(100))  # ID инвойса
    receipt_id = db.Column(db.String(100))  # ID чека
    
    # Даты
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)  # Время обработки
    completed_at = db.Column(db.DateTime)  # Время завершения
    refunded_at = db.Column(db.DateTime)  # Время возврата
    
    # Описание и примечания
    description = db.Column(db.Text)  # Описание транзакции
    failure_reason = db.Column(db.Text)  # Причина отказа
    notes = db.Column(db.Text)  # Внутренние примечания
    
    # Метаданные
    metadata = db.Column(db.JSON)  # Дополнительные данные
    
    # Связи
    plan = db.relationship('SubscriptionPlan', backref='transactions', lazy=True)
    
    def __init__(self, user_id, transaction_type, amount, currency='USD', total_amount=None,
                 subscription_id=None, plan_id=None, billing_cycle=None, payment_method=None,
                 description=None, tax_amount=0, discount_amount=0):
        self.user_id = user_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.currency = currency
        self.tax_amount = tax_amount
        self.discount_amount = discount_amount
        
        # Рассчитать итоговую сумму если не указана
        if total_amount is None:
            self.total_amount = float(amount) + float(tax_amount) - float(discount_amount)
        else:
            self.total_amount = total_amount
        
        self.subscription_id = subscription_id
        self.plan_id = plan_id
        self.billing_cycle = billing_cycle
        self.payment_method = payment_method
        self.description = description
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.transaction_type.value} - {self.amount} {self.currency} ({self.status.value})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subscription_id': self.subscription_id,
            'transaction_type': self.transaction_type.value,
            'status': self.status.value,
            'amount': float(self.amount),
            'currency': self.currency,
            'tax_amount': float(self.tax_amount),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'plan_id': self.plan_id,
            'billing_cycle': self.billing_cycle,
            'payment_method': self.payment_method.value if self.payment_method else None,
            'payment_provider': self.payment_provider,
            'payment_provider_transaction_id': self.payment_provider_transaction_id,
            'invoice_id': self.invoice_id,
            'receipt_id': self.receipt_id,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None,
            'description': self.description,
            'failure_reason': self.failure_reason,
            'metadata': self.metadata,
            'plan': self.plan.to_dict() if self.plan else None
        }
    
    def mark_as_processing(self):
        """Отметить как обрабатываемую"""
        self.status = TransactionStatus.PROCESSING
        self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_completed(self, provider_transaction_id=None, invoice_id=None, receipt_id=None):
        """Отметить как завершенную"""
        self.status = TransactionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        
        if provider_transaction_id:
            self.payment_provider_transaction_id = provider_transaction_id
        if invoice_id:
            self.invoice_id = invoice_id
        if receipt_id:
            self.receipt_id = receipt_id
        
        db.session.commit()
    
    def mark_as_failed(self, failure_reason=None):
        """Отметить как неудачную"""
        self.status = TransactionStatus.FAILED
        if failure_reason:
            self.failure_reason = failure_reason
        db.session.commit()
    
    def mark_as_refunded(self, refund_amount=None, reason=None):
        """Отметить как возвращенную"""
        self.status = TransactionStatus.REFUNDED
        self.refunded_at = datetime.utcnow()
        
        if reason:
            self.notes = f"Refund: {reason}"
        
        db.session.commit()
    
    def is_completed(self):
        """Проверить, завершена ли транзакция"""
        return self.status == TransactionStatus.COMPLETED
    
    def is_refundable(self):
        """Проверить, можно ли вернуть транзакцию"""
        return self.status == TransactionStatus.COMPLETED and not self.refunded_at
    
    def get_refund_amount(self):
        """Получить сумму доступную для возврата"""
        if not self.is_refundable():
            return 0
        
        # Здесь можно добавить логику расчета доступной суммы для возврата
        # Например, учитывать использованное время подписки
        return float(self.total_amount)
    
    @staticmethod
    def get_user_transactions(user_id, limit=50, offset=0, status=None, transaction_type=None):
        """Получить транзакции пользователя"""
        query = Transaction.query.filter_by(user_id=user_id)
        
        if status:
            if isinstance(status, str):
                status = TransactionStatus(status)
            query = query.filter_by(status=status)
        
        if transaction_type:
            if isinstance(transaction_type, str):
                transaction_type = TransactionType(transaction_type)
            query = query.filter_by(transaction_type=transaction_type)
        
        return query.order_by(Transaction.created_at.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_subscription_transactions(subscription_id, limit=50, offset=0):
        """Получить транзакции подписки"""
        return Transaction.query.filter_by(subscription_id=subscription_id)\
            .order_by(Transaction.created_at.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_total_revenue(start_date=None, end_date=None, status=None):
        """Получить общую выручку"""
        query = db.session.query(db.func.sum(Transaction.total_amount)).filter(
            Transaction.status == TransactionStatus.COMPLETED
        )
        
        if start_date:
            query = query.filter(Transaction.completed_at >= start_date)
        
        if end_date:
            query = query.filter(Transaction.completed_at <= end_date)
        
        if status:
            if isinstance(status, str):
                status = TransactionStatus(status)
            query = query.filter_by(status=status)
        
        result = query.scalar()
        return float(result) if result else 0.0