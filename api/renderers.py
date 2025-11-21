from rest_framework.renderers import JSONRenderer


class StandardizedResponseRenderer(JSONRenderer):
    """
    A custom renderer that wraps the API response in a standard format.
    {
        "code": <http_status_code>,
        "status": "<http_status_text>",
        "data": <original_response_data>
    }
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context is None:
            return super().render(data, accepted_media_type, renderer_context)

        response = renderer_context.get('response')
        if response is None:
            return super().render(data, accepted_media_type, renderer_context)

        status_code = response.status_code
        status_text = response.status_text.replace('_', ' ').upper()

        # For paginated responses, DRF uses the whole response as data
        response_payload = {
            'code': status_code,
            'status': status_text,
            'data': data
        }

        # Use the default JSONRenderer to render the final payload
        return super().render(response_payload, accepted_media_type, renderer_context)
