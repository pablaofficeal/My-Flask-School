from flask import render_template, request
from utils.logs_service import init_logger

logger = init_logger('error_handler')

def not_found_error(error):
    logger.warning(f"404 ERROR: {request.url} - IP: {request.remote_addr}")
    return render_template('errors/404.html'), 404