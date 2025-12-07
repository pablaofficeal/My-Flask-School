import logging
import time
from datetime import datetime
import os

# Создаем директорию для логов если не существует
os.makedirs('logs', exist_ok=True)

# Настраиваем формат с миллисекундами
class MillisecondFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            s = ct.strftime('%Y-%m-%d %H:%M:%S')
            s = f"{s}.{int(record.msecs):03d}"
        return s

# Создаем единый обработчик для всех логов
def setup_logging():
    """Настраиваем логирование один раз для всего приложения"""
    # Очищаем все существующие обработчики
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Создаем файл handler
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setLevel(logging.DEBUG)
    
    # Форматтер с миллисекундами
    formatter = MillisecondFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Добавляем handler к root logger
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.DEBUG)
    
    return logging.getLogger(__name__)

# Инициализируем логирование один раз
logger = setup_logging()

def log_info(message: str):
    logger.info(message)

def log_error(message: str):
    logger.error(message)

def log_debug(message: str):
    logger.debug(message)

def log_warning(message: str):
    logger.warning(message)

def log_critical(message: str):
    logger.critical(message)

def log_exception(message: str):
    logger.exception(message)

def log_function_entry(func_name: str, **kwargs):
    """Логирование входа в функцию с параметрами"""
    params = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"ENTER: {func_name}({params})")

def log_function_exit(func_name: str, result=None):
    """Логирование выхода из функции с результатом"""
    if result is not None:
        logger.debug(f"EXIT: {func_name} -> {result}")
    else:
        logger.debug(f"EXIT: {func_name}")

def log_time_execution(func_name: str, start_time: float):
    """Логирование времени выполнения функции"""
    execution_time = (time.time() - start_time) * 1000  # в миллисекундах
    logger.debug(f"EXECUTION TIME: {func_name} took {execution_time:.3f}ms")

def log_request_details(request, response=None):
    """Детальное логирование HTTP запросов"""
    logger.info(f"REQUEST: {request.method} {request.url} from {request.remote_addr}")
    if response:
        logger.info(f"RESPONSE: {response.status_code} for {request.url}")

def log_database_operation(operation: str, table: str, details: str = ""):
    """Логирование операций с базой данных"""
    logger.debug(f"DB OPERATION: {operation} on {table} - {details}")

def log_performance_metric(metric_name: str, value: float, unit: str = "ms"):
    """Логирование метрик производительности"""
    logger.info(f"PERFORMANCE: {metric_name} = {value:.3f}{unit}")

def init_logger(name: str):
    """Создает новый логгер для конкретного модуля"""
    module_logger = logging.getLogger(name)
    module_logger.setLevel(logging.DEBUG)
    return module_logger