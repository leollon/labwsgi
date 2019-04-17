import socket
import sys
from labwsgi.server_side import run_with_cgi
from labwsgi.app_side import simple_app


def wsgi_server():
    host, port = '127.0.0.1', 8090
    max_connections = 1024
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(max_connections)

    while True:
        sock, addr = s.accept()
        sock.recv(1024)
        sock.sendall(run_with_cgi(simple_app))
        sock.close()
        print(addr)


if __name__ == "__main__":
    wsgi_server()
