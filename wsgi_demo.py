import os
import sys
import socket
import datetime
import time


from labwsgi.server_side import run_with_cgi
from labwsgi.app_side import simple_app

line_break = os.linesep
output = sys.stdout.buffer
time_now = datetime.datetime.now


def console_log(text):
    """
    output request information in terminal


    :type test: bytes

    Example

        >>> text = bytes("hello world", encoding='utf-8')
        >>> console_log(text)
        'hello world'
    """
    output.write(text)
    output.flush()


def wsgi_server():
    host, port = '127.0.0.1', 8090
    if len(sys.argv) >= 3:
        host, port = sys.argv[1], int(sys.argv[2])
    max_connections_queue = 1024
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(max_connections_queue)
    console_log(
        bytes(
            'LabWSGI serving HTTP service on http://%s:%d' % (
                host, port) + line_break,
            encoding='utf-8'
        )
    )
    console_log(
        bytes(
            time_now().strftime("%c ") + time.tzname[0] + line_break,
            encoding='utf-8'
        )
    )

    while True:
        sock, addr = s.accept()
        request = sock.recv(1024)
        response = run_with_cgi(simple_app)
        sock.sendall(response)
        console_log(
            bytes(
                time_now().strftime('[%Y-%m-%d %H:%M:%S] ') +
                repr(request.decode('utf-8').splitlines()[0]) + ' ' +
                response.decode('utf-8').split('\r\n')[0].split(' ', maxsplit=1)[-1] +
                line_break,
                encoding='utf-8'
            )
        )
        sock.close()


if __name__ == "__main__":
    wsgi_server()
