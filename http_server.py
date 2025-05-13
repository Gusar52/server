import socket
import threading
import os
import sys

directory = "."

if "--directory" in sys.argv:
    idx = sys.argv.index("--directory")
    if idx + 1 < len(sys.argv):
        directory = sys.argv[idx + 1]


def handle_client(client_socket):
    request_data = client_socket.recv(1024).decode()
    lines = request_data.split("\r\n")
    request_line = lines[0]
    method, path, _ = request_line.split(" ")
    headers = {}

    for line in lines[1:]:
        if ": " in line:
            key, value = line.split(": ", 1)
            headers[key] = value

    if path == "/":
        response = "HTTP/1.1 200 OK\r\n\r\n"

    elif method == "POST" and path.startswith("/files/"):
        filename = path[len("/files/"):]
        file_path = os.path.join(directory, filename)
        content_length = int(headers.get("Content-Length", "0"))
        body = request_data.split("\r\n\r\n", 1)[1]

        while len(body.encode()) < content_length:
            body += client_socket.recv(1024).decode()

        with open(file_path, "w") as f:
            f.write(body[:content_length])

        response = "HTTP/1.1 201 Created\r\n\r\n"

    elif path.startswith("/files/"):

        try:

            filename = path[len("/files/"):]
            file_path = os.path.join(directory, filename)

            if os.path.isfile(file_path):

                with open(file_path, "rb") as f:
                    content = f.read()

                response = (
                               "HTTP/1.1 200 OK\r\n"
                               "Content-Type: application/octet-stream\r\n"
                               f"Content-Length: {len(content)}\r\n"
                               "\r\n"
                           ).encode() + content
                client_socket.send(response)
                client_socket.close()
                return
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"

        except Exception as e:
            print("Error:", e)

    elif path.startswith("/echo/"):
        echo_str = path[len("/path/"):]
        content_length = len(echo_str)
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {content_length}\r\n"
            "\r\n"
            f"{echo_str}\r\n"
        )

    elif path == "/user-agent":
        user_agent = headers.get("User-Agent", "")
        content_length = len(user_agent)
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {content_length}\r\n"
            "\r\n"
            f"{user_agent}"
        )

    else:

        response = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 13\r\n"
            "\r\n"
            "404 Not Found"
        )

    client_socket.sendall(response.encode())

    client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 4221))
    server_socket.listen(5)
    print("Server listening on port 4221...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            thread = threading.Thread(target=handle_client, args=(client_socket,))
            thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()