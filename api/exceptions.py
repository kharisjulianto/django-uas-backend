from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework.
    Formats errors into a consistent structure.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Default DRF errors are dicts of {field: [messages]} or lists for non_field_errors
        # We want to flatten this into a simple list of strings.
        error_messages = []

        if isinstance(response.data, dict):
            for field, messages in response.data.items():
                if isinstance(messages, list):
                    for message in messages:
                        if field == 'non_field_errors' or field == 'detail':
                            error_messages.append(str(message))
                        else:
                            error_messages.append(f"{field}: {message}")
                else:
                    if field == 'non_field_errors' or field == 'detail':
                        error_messages.append(str(messages))
                    else:
                        error_messages.append(f"{field}: {messages}")
        elif isinstance(response.data, list):
            error_messages = [str(msg) for msg in response.data]
        else:
            error_messages.append(str(response.data))

        # The custom renderer will wrap this in the final structure
        response.data = {'error': error_messages}

    return response
