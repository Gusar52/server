import socket
import threading
import json
from src.http_server import handle_client
from functools import lru_cache


def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Файл конфигурации не найден, используются значения по умолчанию")
        return {
            "server": {
                "port": 8080,
                "host": "0.0.0.0"
            }
        }


def run_server() -> None:
    config = load_config()
    server_config = config['server']
    server_socket = create_server_socket(server_config['host'], server_config['port'])
    cid = 0

    print(f"Сервер запущен на {server_config['host']}:{server_config['port']}")

    while True:
        client_socket = accept_client_connection(server_socket, cid)
        thread = threading.Thread(target=serve_client, args=(client_socket, cid))
        thread.start()
        cid += 1

# статика в класическом виде jpg|jpeg|gif|png|ico|css|zip|tgz|gz|rar|bz2
# |doc|xls|exe|pdf|ppt|txt|tar|mid|midi|wav|bmp|rtf|js|swf|flv|mp3

@lru_cache(maxsize=52)
def get_content(path):
    with open(path, "rb") as f:
        return f.read()

def serve_static_file(path):
    content = get_content(path)
    if not content:
        return "HTTP/1.1 404"
    
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
    except Exception as e:
        print(f"Ошибка при чтении запроса от клиента #{cid}: {e}")
        raise


def create_server_socket(host: str, port: int) -> socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((host, port))
        server_socket.listen()
        return server_socket
    except OSError as e:
        print(f"Ошибка при создании сервера: {e}")
        print("Попытка использовать другой порт...")
        server_socket.close()
        return create_server_socket(host, port + 1)


def accept_client_connection(server_socket: socket, cid: int) -> socket:
    client_socket, client_addres = server_socket.accept()
    print(f"Client #{cid} conected\n {client_addres[0]}:{client_addres[1]}")
    return client_socket


if __name__ == "__main__":
    run_server()