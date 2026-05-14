import socket


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 5000))
    server.listen()

    print("Servidor ativo")


if __name__ == "__main__":
    start_server()