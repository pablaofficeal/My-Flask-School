from models.models_all_rout_imp import Transaction, TransactionStatus, TransactionType, PaymentMethod
from models.users.main_user_db import User
from utils.logs_service import init_logger
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
import uuid
from models.imp import db


class TransactionService:
    """Сервис для управления транзакциями"""
    
    def __init__(self):
        self.logger = init_logger('transaction_service')
    
    def create_transaction(self, user_id, subscription_plan_id, amount, currency='USD', 
                          billing_cycle='monthly', payment_method=PaymentMethod.CREDIT_CARD,
                          metadata=None):
        """Создать транзакцию"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Создать уникальный внешний ID
            external_id = str(uuid.uuid4())
            
            transaction = Transaction(
                user_id=user_id,
                subscription_plan_id=subscription_plan_id,
                amount=amount,
                currency=currency,
                billing_cycle=billing_cycle,
                payment_method=payment_method,
                status=TransactionStatus.PENDING,
                external_id=external_id,
                metadata=metadata or {}
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            self.logger.info(f"Created transaction {transaction.id} for user {user_id}")
            return transaction
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating transaction: {str(e)}")
            raise
    
    def process_transaction(self, transaction_id, payment_data=None):
        """Обработать транзакцию"""
        try:
            transaction = Transaction.query.get(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")
            
            # Проверить, можно ли обработать транзакцию
            if transaction.status not in [TransactionStatus.PENDING, TransactionStatus.PROCESSING]:
                raise ValueError(f"Cannot process transaction in status {transaction.status.value}")
            
            # Обновить статус на обработку
            transaction.set_processing()
            
            # Здесь должна быть интеграция с платежной системой
            # Для примера просто симулируем успешную обработку
            
            # Симуляция обработки платежа
            payment_successful = self._simulate_payment_processing(transaction, payment_data)
            
            if payment_successful:
                transaction.set_completed()
                
                # Активировать подписку для пользователя
                from services.subscription_service import subscription_service
                subscription_service.assign_subscription_to_user(
                    user_id=transaction.user_id,
                    plan_id=transaction.subscription_plan_id,
                    billing_cycle=transaction.billing_cycle,
                    start_trial=False
                )
                
                self.logger.info(f"Transaction {transaction_id} completed successfully")
                
            else:
                transaction.set_failed("Payment processing failed")
                self.logger.warning(f"Transaction {transaction_id} failed")
            
            return transaction
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error processing transaction: {str(e)}")
            raise
    
    def refund_transaction(self, transaction_id, amount=None, reason=None):
        """Вернуть транзакцию"""
        try:
            transaction = Transaction.query.get(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")
            
            # Проверить, можно ли вернуть транзакцию
            if not transaction.can_be_refunded():
                raise ValueError("Transaction cannot be refunded")
            
            # Определить сумму возврата
            refund_amount = amount or transaction.amount
            
            if refund_amount > transaction.amount:
                raise ValueError("Refund amount cannot exceed transaction amount")
            
            # Создать транзакцию возврата
            refund_transaction = Transaction(
                user_id=transaction.user_id,
                subscription_plan_id=transaction.subscription_plan_id,
                amount=-refund_amount,  # Отрицательная сумма для возврата
                currency=transaction.currency,
                billing_cycle=transaction.billing_cycle,
                payment_method=transaction.payment_method,
                status=TransactionStatus.PENDING,
                type=TransactionType.REFUND,
                parent_transaction_id=transaction_id,
                external_id=str(uuid.uuid4()),
                metadata={
                    'refund_reason': reason,
                    'original_transaction_id': transaction_id,
                    'refund_amount': refund_amount
                }
            )
            
            # Обновить оригинальную транзакцию
            transaction.refund_amount = refund_amount
            transaction.refunded_at = datetime.utcnow()
            
            db.session.add(refund_transaction)
            db.session.commit()
            
            # Обработать возврат (симуляция)
            self._process_refund(refund_transaction, reason)
            
            self.logger.info(f"Created refund transaction {refund_transaction.id} for original transaction {transaction_id}")
            return refund_transaction
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error refunding transaction: {str(e)}")
            raise
    
    def get_transaction(self, transaction_id):
        """Получить транзакцию по ID"""
        return Transaction.query.get(transaction_id)
    
    def get_transaction_by_external_id(self, external_id):
        """Получить транзакцию по внешнему ID"""
        return Transaction.query.filter_by(external_id=external_id).first()
    
    def get_user_transactions(self, user_id, limit=50, offset=0):
        """Получить транзакции пользователя"""
        return Transaction.query.filter_by(user_id=user_id).order_by(
            Transaction.created_at.desc()
        ).limit(limit).offset(offset).all()
    
    def get_user_transaction_stats(self, user_id):
        """Получить статистику транзакций пользователя"""
        from sqlalchemy import func, case
        
        stats = db.session.query(
            func.count(Transaction.id).label('total_transactions'),
            func.sum(case([(Transaction.status == TransactionStatus.COMPLETED, Transaction.amount)], else_=0)).label('total_spent'),
            func.sum(case([(Transaction.status == TransactionStatus.REFUNDED, Transaction.refund_amount)], else_=0)).label('total_refunded'),
            func.count(case([(Transaction.status == TransactionStatus.COMPLETED, 1)])).label('successful_transactions'),
            func.count(case([(Transaction.status == TransactionStatus.FAILED, 1)])).label('failed_transactions'),
            func.count(case([(Transaction.status == TransactionStatus.REFUNDED, 1)])).label('refunded_transactions')
        ).filter_by(user_id=user_id).first()
        
        return {
            'total_transactions': stats.total_transactions or 0,
            'total_spent': float(stats.total_spent or 0),
            'total_refunded': float(stats.total_refunded or 0),
            'successful_transactions': stats.successful_transactions or 0,
            'failed_transactions': stats.failed_transactions or 0,
            'refunded_transactions': stats.refunded_transactions or 0,
            'success_rate': (stats.successful_transactions or 0) / max(stats.total_transactions or 1, 1) * 100
        }
    
    def get_transactions_by_date_range(self, start_date, end_date, status=None, limit=100):
        """Получить транзакции за период"""
        query = Transaction.query.filter(
            and_(
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            )
        )
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Transaction.created_at.desc()).limit(limit).all()
    
    def get_revenue_stats(self, start_date, end_date):
        """Получить статистику доходов"""
        from sqlalchemy import func
        
        stats = db.session.query(
            func.sum(Transaction.amount).label('total_revenue'),
            func.count(Transaction.id).label('total_transactions'),
            func.avg(Transaction.amount).label('avg_transaction_amount')
        ).filter(
            and_(
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date,
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.amount > 0  # Исключить возвраты
            )
        ).first()
        
        return {
            'total_revenue': float(stats.total_revenue or 0),
            'total_transactions': stats.total_transactions or 0,
            'avg_transaction_amount': float(stats.avg_transaction_amount or 0)
        }
    
    def update_transaction_status(self, transaction_id, status, error_message=None):
        """Обновить статус транзакции"""
        try:
            transaction = Transaction.query.get(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")
            
            if status == TransactionStatus.COMPLETED:
                transaction.set_completed()
            elif status == TransactionStatus.FAILED:
                transaction.set_failed(error_message)
            elif status == TransactionStatus.PROCESSING:
                transaction.set_processing()
            else:
                transaction.status = status
            
            db.session.commit()
            
            self.logger.info(f"Updated transaction {transaction_id} status to {status.value}")
            return transaction
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating transaction status: {str(e)}")
            raise
    
    def _simulate_payment_processing(self, transaction, payment_data):
        """Симуляция обработки платежа"""
        # В реальном приложении здесь будет интеграция с платежной системой
        # Например: Stripe, PayPal, etc.
        
        # Для демонстрации просто возвращаем успех
        return True
    
    def _process_refund(self, refund_transaction, reason):
        """Обработать возврат"""
        # В реальном приложении здесь будет интеграция с платежной системой
        # Для демонстрации просто помечаем как завершенный
        
        refund_transaction.set_completed()
        self.logger.info(f"Processed refund transaction {refund_transaction.id}")


# Создать глобальный экземпляр сервиса
transaction_service = TransactionService()