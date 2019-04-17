"""The Application/Framework Side

"""

HELLO_WORLD = b"Hello world!"


def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/plain')
    ]
    start_response(status, response_headers)
    return [HELLO_WORLD]
