import socket
import threading
import json
import inspect

from primos import (
    is_prime,
    find_max_prime_parallel
)

from game_of_life import (
    game_of_life_sequential
)


HOST = "localhost"
PORT = 5000


# =========================================================
# MÉTODOS RPC
# =========================================================

METHODS = {
    "is_prime": is_prime,
    "find_max_prime": find_max_prime_parallel,
    "game_of_life": game_of_life_sequential
}


# =========================================================
# LIST METHODS
# =========================================================

def list_methods():

    methods_info = []

    for name, func in METHODS.items():

        signature = inspect.signature(func)

        methods_info.append({
            "name": name,
            "params": list(signature.parameters.keys()),
            "description": func.__doc__ or "Sem descrição"
        })

    return methods_info


METHODS["list_methods"] = list_methods


# =========================================================
# CLIENT HANDLER
# =========================================================

def handle_client(conn, addr):

    print(f"\nCliente ligado: {addr}")

    try:

        while True:

            data = conn.recv(4096)

            if not data:
                break

            try:

                request = json.loads(data.decode())

                method = request.get("method")

                params = request.get("params", {})

                if method not in METHODS:

                    response = {
                        "error": "Método inexistente"
                    }

                else:

                    func = METHODS[method]

                    result = func(**params)

                    response = {
                        "result": result
                    }

            except Exception as e:

                response = {
                    "error": str(e)
                }

            conn.sendall(
                json.dumps(response).encode()
            )

    finally:

        conn.close()

        print(f"Cliente desligado: {addr}")


# =========================================================
# SERVER
# =========================================================

def start_server():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.bind((HOST, PORT))

    server.listen()

    print(f"\nServidor ativo em {HOST}:{PORT}\n")

    while True:

        conn, addr = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr)
        )

        thread.start()


if __name__ == "__main__":

    start_server()