from flask import Flask, request, g
from config import Config
from models.imp import db
from models.models_all_rout_imp import *
from flask_wtf import CSRFProtect
from __init__ import *
from utils.logs_service import init_logger
import os
import time

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config.from_object(Config)
csrf = CSRFProtect(app)
db.init_app(app)
logger = init_logger('app')

register_all_blueprints(app)
register_testing_error_handlers(app)
register_error_handlers(app)
register_admin_routes(app)
register_api_blueprints(app)

if not os.path.exists('logs'):
    os.makedirs('logs')

# Middleware для детального логирования всех запросов (без дублирования)
logger = init_logger('app')

@app.before_request
def before_request():
    g.start_time = time.time()
    # Логируем только основную информацию о запросе
    logger.info(f"REQUEST: {request.method} {request.url} from {request.remote_addr}")

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        execution_time = (time.time() - g.start_time) * 1000
        logger.info(f"RESPONSE: {response.status_code} for {request.url} ({execution_time:.3f}ms)")
    return response

# Удаляем универсальный обработчик - пусть работают кастомные

with app.app_context():
    db.create_all()
    logger.info("✅ Database initialized successfully")

if __name__ == '__main__':
    logger.info("🚀 Starting Flask application...")
    logger.info(f"🌐 Server will run on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)  # В проде debug=False!