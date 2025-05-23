from functools import lru_cache
import socket
import os
import sys

directory = "."

if "--directory" in sys.argv:
    idx = sys.argv.index("--directory")
    if idx + 1 < len(sys.argv):
        directory = sys.argv[idx + 1]


def handle_client(client_socket: socket, request: bytearray, server_config: dict):
    print("----handle Client----")
    request_data = request.decode()
    lines = request_data.split("\r\n")
    request_line = lines[0]
    method, path, _ = request_line.split(" ")
    headers = {}
    print(method, path)
    for line in lines[1:]:
        if ": " in line:
            key, value = line.split(": ", 1)
            headers[key] = value

    # if path == "/":
    #     response = "HTTP/1.1 200 OK\r\n\r\n"

    if method == "POST" and path.startswith("/files/"):
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
        # Пробуем обработать как статический файл
        root = server_config['root']
        file_path = root +  os.path.join(directory, path.lstrip('/'))
        print(f"-----------------------{file_path}-----------------------")
        if os.path.exists(file_path):
            response = serve_static_file(file_path, server_config['index'])
        else:
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/plain\r\n"
                "Content-Length: 13\r\n"
                "\r\n"
                "404 Not Found"
            )
    # print(response)
    client_socket.sendall(response.encode())


@lru_cache(maxsize=52)
def get_content(path):
    with open(path, "rb") as f:
        return f.read()
# статика в класическом виде jpg|jpeg|gif|png|ico|css|zip|tgz|gz|rar|bz2
# |doc|xls|exe|pdf|ppt|txt|tar|mid|midi|wav|bmp|rtf|js|swf|flv|mp3


def serve_static_file(path, index_file: str):
    print(path)
    if os.path.isdir(path):
        index_file = os.path.join(path, index_file)
        if os.path.isfile(index_file):
            content = get_content(index_file)
            return (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(content)}\r\n"
                "\r\n" + content.decode()
            )
        return generate_directory_listing(path)

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
        f"\r\n" + content.decode()
    )


def generate_directory_listing(directory_path):
    try:
        files = os.listdir(directory_path)
        html = f"<html><head><title>Index of {directory_path}</title></head><body><h1>Index of {directory_path}</h1><ul>"
        for f in files:
            full_path = os.path.join(directory_path, f)
            if os.path.isdir(full_path):
                f += "/"
            html += f'<li><a href="{f}">{f}</a></li>'
        html += "</ul></body></html>"

        return (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: text/html\r\n"
            f"Content-Length: {len(html)}\r\n"
            f"\r\n{html}"
        )
    except OSError:
        return "HTTP/1.1 403 Forbidden\r\n\r\n"
