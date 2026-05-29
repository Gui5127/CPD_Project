import socket
import threading
import json
import inspect
import struct
import multiprocessing

from primos import (
    is_prime,
    find_max_prime_parallel,
    find_max_prime_sequential
)

from game_of_life import (
    game_of_life_sequential,
    game_of_life_parallel
)


HOST = "localhost"
PORT = 5000


# =========================================================
# RPC METHODS
# =========================================================

METHODS = {

    "is_prime":
        is_prime,

    "find_max_prime_sequential":
        find_max_prime_sequential,

    "find_max_prime_parallel":
        find_max_prime_parallel,

    "game_of_life":
        game_of_life_sequential,

    "game_of_life_parallel":
        game_of_life_parallel
}


# =========================================================
# LIST METHODS
# =========================================================

def list_methods():
    """
    Lista todos os métodos RPC disponíveis no servidor.

    Inclui:
    - nome do método
    - parâmetros aceites
    - descrição (docstring da função)

    Returns:
        list[dict]: lista de métodos disponíveis
    """

    methods_info = []

    for name, func in METHODS.items():

        signature = inspect.signature(
            func
        )

        methods_info.append({

            "name":
                name,

            "params":
                list(signature.parameters.keys()),

            "description":
                func.__doc__ or "Sem descrição"
        })

    return methods_info


METHODS["list_methods"] = list_methods


# =========================================================
# RECEIVE EXACT
# =========================================================

def recv_exact(conn, size):
    """
    Recebe exatamente um número fixo de bytes de um socket.

    Garante que a leitura é completa antes de retornar.

    Args:
        conn (socket): ligação TCP
        size (int): número de bytes a receber

    Returns:
        bytes | None: dados recebidos ou None se conexão fechar
    """

    data = b""

    while len(data) < size:

        packet = conn.recv(
            size - len(data)
        )

        if not packet:
            return None

        data += packet

    return data


# =========================================================
# RECEIVE MESSAGE
# =========================================================

def receive_message(conn):
    """
    Recebe uma mensagem completa via protocolo RPC.

    O protocolo usa:
    - header de 4 bytes (tamanho)
    - payload JSON

    Args:
        conn (socket): ligação TCP

    Returns:
        dict | None: mensagem decodificada ou None
    """

    header = recv_exact(conn, 4)

    if not header:
        return None

    message_size = struct.unpack(
        "!I",
        header
    )[0]

    message_data = recv_exact(
        conn,
        message_size
    )

    if not message_data:
        return None

    return json.loads(
        message_data.decode()
    )


# =========================================================
# SEND MESSAGE
# =========================================================

def send_message(conn, message_dict):
    """
    Envia uma mensagem RPC ao cliente.

    Serializa um dicionário em JSON e envia com header de tamanho.

    Args:
        conn (socket): ligação TCP
        message_dict (dict): mensagem a enviar

    Returns:
        None
    """

    message = json.dumps(
        message_dict
    ).encode()

    header = struct.pack(
        "!I",
        len(message)
    )

    conn.sendall(
        header + message
    )


# =========================================================
# CLIENT HANDLER
# =========================================================

def handle_client(conn, addr):
    """
    Gerencia a comunicação com um cliente RPC.

    Executa pedidos em loop, despacha métodos dinamicamente e devolve
    resultados ou erros.

    Args:
        conn (socket): ligação do cliente
        addr (tuple): endereço do cliente

    Returns:
        None
    """

    print(f"\nCliente ligado: {addr}")

    conn.settimeout(60)

    try:

        while True:

            request = receive_message(conn)

            if request is None:
                break

            try:

                method = request.get(
                    "method"
                )

                params = request.get(
                    "params",
                    {}
                )

                if method not in METHODS:

                    response = {
                        "error":
                            "Método inexistente"
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

            send_message(
                conn,
                response
            )

    except socket.timeout:

        print(
            f"Timeout cliente: {addr}"
        )

    finally:

        conn.close()

        print(
            f"Cliente desligado: {addr}"
        )


# =========================================================
# SERVER
# =========================================================

def start_server():
    """
    Inicia o servidor RPC.

    - abre socket TCP
    - escuta conexões
    - cria uma thread por cliente

    Returns:
        None
    """

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.bind((HOST, PORT))

    server.listen()

    print(
        f"\nServidor ativo "
        f"em {HOST}:{PORT}\n"
    )

    while True:

        conn, addr = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        )

        thread.start()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    multiprocessing.freeze_support()

    start_server()