import socket

def manipulator(host: str, port: int):
    """Создает сервер TCP и принимает данные, затем выводит на консоль.

    :param host: Адрес хоста
    :type host: str
    :param port: Порт
    :type port: int
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)

        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected to {addr}")

            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print("Received data from controller:", data.decode())

if __name__ == "__main__":
    manipulator("0.0.0.0", 8090)
