import socket
import threading
import time
from src.http_server import handle_client
import os
import select


def run_server(port=8080) -> None:
    server_socket = create_server_socket(port)
    cid = 0

    while True:
        client_socket = accept_client_connection(server_socket, cid)
        thread = threading.Thread(target=serve_client, args=(client_socket, cid))
        thread.start()
        cid += 1

# статика в класическом виде jpg|jpeg|gif|png|ico|css|zip|tgz|gz|rar|bz2
# |doc|xls|exe|pdf|ppt|txt|tar|mid|midi|wav|bmp|rtf|js|swf|flv|mp3

def serve_static_file(path):
    content_type = None
    if path.endswith('.html'):
        content_type = 'text/html'
    elif path.endswith('.css'):
        content_type = 'text/css'
    elif path.endswith('.js'):
        content_type = 'application/javascript'
    elif path.endswith('.png'):
        content_type = 'image/png'
    elif path.endswith('.jpg') or path.endswith('.jpeg'):
        content_type = 'image/jpeg'

    with open(path, 'rb') as f:
        content = f.read()

    return (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(content)}\r\n"
            f"\r\n".encode() + content
    )


def serve_client(client_socket: socket, cid: int):
    try:
      while True:
        request = read_request(client_socket, cid)
        if request is None:
            print(f"Client #{cid} disconnected")
            client_socket.close()
            break
        else:
            handle_client(client_socket)



    except ConnectionResetError:
        return None
    except:
        raise   
        

def read_request(client_socket: socket, cid: int, delimiter=b"!") -> bytearray:
    request = bytearray()
    try:
        while True:
            request_data = client_socket.recv(1024)
            print(f"\n[Client #{cid}] REQUEST:\n{request_data.decode()}\n")
            if not request_data:
                return None
            request += request_data
            if delimiter in request:
                return request
    except ConnectionResetError:
        return None
    except:
        raise


def create_server_socket(server_port) -> socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    server_socket.bind(("", server_port))
    server_socket.listen()
    return server_socket


def accept_client_connection(server_socket: socket, cid: int) -> socket:
    client_socket, client_addres = server_socket.accept()
    print(f"Client #{cid} conected\n {client_addres[0]}:{client_addres[1]}")
    return client_socket


if __name__ == "__main__":
    run_server()