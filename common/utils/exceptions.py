from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_payload = {
            'error': True,
            'message': _extract_message(response.data),
            'details': response.data,
            'status_code': response.status_code,
        }
        response.data = error_payload

    return response


def _extract_message(data):
    if isinstance(data, dict):
        first_key = next(iter(data))
        first_value = data[first_key]
        if isinstance(first_value, list):
            return f"{first_key}: {first_value[0]}"
        return str(first_value)
    if isinstance(data, list):
        return str(data[0])
    return str(data)