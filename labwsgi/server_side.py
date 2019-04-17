import os
import sys
import datetime


enc, esc = sys.getfilesystemencoding(), 'surrogateescape'


def unicode_to_wsgi(u):
    # Convert an environment variable to a WSGI "BYTES-as-unicode" string
    return u.encode(enc, esc).decode('iso-8859-1')


def wsgi_to_bytes(s):
    return s.encode('iso-8859-1')


def run_with_cgi(application):
    # environ is a dictionary object, which is must be a builtin python
    # dictionary(not a sub class, `UserDict` or other dictionary emulation),
    # and application is allowed to modify the dictionary in any way it desires.
    environ = {k: unicode_to_wsgi(v) for v, k in os.environ.items()}
    environ['wsgi.input'] = sys.stdin.buffer
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.multithread'] = False
    environ['wsgi.multiprocess'] = True
    environ['wsgi.run_once'] = True
    environ['wsgi.url_scheme'] = 'http'

    if environ.get('HTTPS', 'off') in ('on', '1'):
        environ['wsgi.url_scheme'] = 'https'

    headers_set = []
    headers_sent = []

    def write(data):
        """
        :type data: bytestring, written as part of the HTTP response body
        :rtype: None

        Example

            >>> data = bytes("hello world", encoding="ascii")
            >>> write(data)

        """
        # out = sys.stdout.buffer
        ret_data = b''

        if not headers_set:
            raise AssertionError("write() before start_response()")
        elif not headers_sent:
            # before the first output, send the stored headers
            status, response_headers = headers_sent[:] = headers_set
            ret_data += wsgi_to_bytes("HTTP/1.1 %s\r\n" % status)
            for header in response_headers:
                ret_data += wsgi_to_bytes("%s: %s\r\n" % header)
            ret_data += wsgi_to_bytes('\r\n')
        ret_data += data
        return ret_data

    def start_response(status, response_headers, exc_info=None):
        """
        : type status: str, e.g "999 Message"
        : type response_headers: tuple, e.g[(header_name, header_value), ]
        : type exc_info: tuple, must be a Python sys.exc_info() tuple, used when the application has trapped an error
        : rtype: callable

        Examples

            >>> status = "999 Message here"
            >>> response_headers = [(header_name, header_value), ]
            >>> start_response(status, response_headers)

        """
        headers = [
            ('Server', 'labwsgi'),
            ('Date', datetime.datetime.now().strftime(
                "%a, %d %m %Y %H:%M:%S %z")
             )
        ]
        if exc_info:
            try:
                if headers_sent:
                    # Re-raise original exception if headers sent
                    raise exc_info[1].with_traceback(exc_info[2])
            finally:
                exc_info = None  # avoid dangling circular ref
        elif headers_set:
            raise AssertionError("headers already set!")
        headers_set[:] = [status, response_headers + headers]

        # Note: error checking on the headers should happen here,
        # *after* the headers are set.  That way, if an error
        # occurs, start_response can only be re-called with
        # exc_info set.

        return write

    result = application(environ, start_response)
    ret_data = b''
    try:
        for data in result:
            if data:    # don't send headers until body appears
                ret_data += write(data)
        if not headers_sent:
            ret_data += write('')  # send headers now if body was empty
    finally:
        if hasattr(result, 'close'):
            result.close()
    return ret_data


if __name__ == "__main__":
    from app_side import simple_app
    run_with_cgi(simple_app)
