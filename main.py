import socket
import threading
import time
from http_server import handle_client


def run_server(port=8080) -> None:
    server_socket = create_server_socket(port)
    cid = 0

    while True:
        client_socket = accept_client_connection(server_socket, cid)
        thread = threading.Thread(target=serve_client, args=(client_socket, cid))
        thread.start()
        cid += 1


def serve_client(client_socket, cid):
    try:
        class LoggingSocket:
            def __init__(self, sock):
                self.sock = sock
                self.response_data = b""

            def recv(self, *args):
                data = self.sock.recv(*args)
                if data:
                    print(f"\n[Client #{cid}] REQUEST:\n{data.decode()}\n")
                return data

            def sendall(self, data):
                self.response_data += data
                print(f"[Client #{cid}] RESPONSE:\n{data.decode()}\n")
                return self.sock.sendall(data)

            def close(self):
                return self.sock.close()

            def __getattr__(self, name):
                return getattr(self.sock, name)

        logging_socket = LoggingSocket(client_socket)

        handle_client(logging_socket)

        print(f"Client #{cid} has been served")
    except Exception as e:
        print(f"Error serving client #{cid}: {e}")
    finally:
        client_socket.close()


def read_request(client_socket: socket, delimiter=b"!") -> bytearray:
    request = bytearray()
    try:
        while True:
            chunk = client_socket.recv(1024)
            print(chunk)
            if not chunk:
                return None
            request += chunk
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