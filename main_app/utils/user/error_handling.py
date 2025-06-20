import json
from functools import wraps


with open('errors.json') as f:
    error_dict = json.load(f)


def handle_error(e: Exception):
    error_type = type(e).__name__
    error_data = error_dict.get(error_type, error_dict["Exception"])

    print(f"[ERROR {error_data['code']}] {error_data['message']}")
    print(f"Details: {str(e)}")