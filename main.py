import socket


def main() -> None:
    backlog = 10
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    serv_sock.bind(("127.0.0.1", 53210))
    serv_sock.listen(backlog)
    while True:
        # Бесконечно обрабатываем входящие подключения
        client_sock, client_addr = serv_sock.accept()
        print(f"Conected by {client_addr}")
        while True:
            # Пока клиент не отключился, читаем передаваемые им данные и отправляем их обратно
            data = client_sock.recv(1024)
            if not data:
                # Клиент отключился
                break
            client_sock.sendall(data)


if __name__ == "__main__":
    main()
