import json
import socket
import threading
from select import select

from src.http_server import handle_client
from src.virtual_server_manager import VirtualServerManager


def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ("Файл конфигурации не найден")


def run_server() -> None:
    config = load_config()
    server_manager = VirtualServerManager(config)

    server_sockets = []
    for server_config in config["server"]:
        port = server_config["port"]
        if port not in server_sockets:
            server_sockets.append(create_server_socket(server_config["host"], port))
            print(
                f"Сервер {server_config['server_name']} запущен на {server_config['host']}:{server_config['port']}"
            )

    cid = 0

    while True:
        read_sockets, _, _ = select(list(server_sockets), [], [])
        for server_socket in read_sockets:
            client_socket = accept_client_connection(server_socket, cid)
            thread = threading.Thread(
                target=serve_client, args=(client_socket, cid, server_manager)
            )
        thread.start()
        cid += 1


def serve_client(client_socket: socket, cid: int, server_manager: VirtualServerManager):
    try:
        while True:
            request = read_request(client_socket, cid)
            if not request :
                print("Client #{cid} disconnected")
                client_socket.close()
                break

            request_str = request.decode()
            headers = {}
            for line in request_str.split("\r\n")[1:]:
                if ": " in line:
                    key, value = line.split(": ", 1)
                    headers[key] = value
            server_name = headers.get("Host", "").split(":")[0]
            server_config = server_manager.find_server(server_name)

            if server_config:
                print(f"Найден виртуальный сервер: {server_config['server_name']}")
                handle_client(client_socket, request, server_config)
            else:
                print(f"Виртуальный сервер не найден для {server_name}")
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
                client_socket.sendall(response.encode())

    except ConnectionResetError:
        return None
    except:
        raise


def read_request(client_socket: socket, cid: int, delimiter=b"") -> bytearray:
    request = bytearray()
    try:
        while True:
            request_data = client_socket.recv(1024)
            print(f"\n[Client #{cid}] REQUEST:\n{request_data.decode()}\n")
            if not request_data:
                return request
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
