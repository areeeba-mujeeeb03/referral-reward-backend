# import json
# from main_app.utils.user.errors import error_messages
#
#
# def handle_error(e: Exception):
#     error_type = type(e).__name__
#     error_data = error_messages.get(error_type, error_messages["Exception"])
#
#     print(f"[ERROR {error_data['code']}] {error_data['message']}")
#     print(f"Details: {str(e)}")

from flask import jsonify
from main_app.utils.user.errors import error_messages
import logging

logger = logging.getLogger(__name__)

def handle_error(error_code, status_code=400, extra_info=None):

    message = error_messages.get(error_code, "Unknown error occurred")
    logger.error(f"Error occurred: {message}")

    response = {"error": message}
    if extra_info:
        response["details"] = extra_info

    return jsonify(response), status_code