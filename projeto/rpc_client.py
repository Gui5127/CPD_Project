import socket
import json
import struct


HOST = "localhost"
PORT = 5000


# =========================================================
# SEND MESSAGE
# =========================================================

def send_message(sock, message_dict):
    """
    Envia mensagem JSON ao servidor RPC.

    Args:
        sock (socket): socket ativo
        message_dict (dict): mensagem

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

    sock.sendall(
        header + message
    )


# =========================================================
# RECEIVE EXACT
# =========================================================

def recv_exact(sock, size):
    """
    Lê exatamente um número fixo de bytes de um socket TCP.

    Args:
        sock (socket): socket TCP ativo
        size (int): número de bytes a ler

    Returns:
        bytes | None: dados recebidos ou None se a ligação for fechada
    """

    data = b""

    while len(data) < size:

        packet = sock.recv(
            size - len(data)
        )

        if not packet:
            return None

        data += packet

    return data


# =========================================================
# RECEIVE MESSAGE
# =========================================================

def receive_message(sock):
    """
    Recebe e decodifica uma mensagem completa do servidor RPC.

    Args:
        sock (socket): socket ativo

    Returns:
        dict | None: resposta RPC decodificada ou None se falhar
    """

    header = recv_exact(sock, 4)

    if not header:
        return None

    message_size = struct.unpack(
        "!I",
        header
    )[0]

    message_data = recv_exact(
        sock,
        message_size
    )

    if not message_data:
        return None

    return json.loads(
        message_data.decode()
    )


# =========================================================
# RPC CLIENT
# =========================================================

class RPCClient:
    """
    Cliente RPC baseado em sockets TCP.

    Responsável por:
    - estabelecer ligação com o servidor RPC
    - enviar pedidos estruturados (method + params)
    - receber respostas JSON do servidor

    Métodos:
        request(method, params): envia chamada RPC e devolve resposta
        close(): encerra a ligação ao servidor
    """

    def __init__(self):
        """
        Inicializa o cliente RPC e estabelece ligação TCP com o servidor.

        Utiliza HOST e PORT definidos globalmente.
        """

        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.sock.connect((HOST, PORT))

    def request(self, method, params):
        """
        Envia um pedido RPC ao servidor e aguarda resposta.

        Args:
            method (str): nome do método remoto a executar
            params (dict): parâmetros da chamada RPC

        Returns:
            dict: resposta do servidor (result ou error)
        """

        request = {
            "method": method,
            "params": params
        }

        send_message(
            self.sock,
            request
        )

        response = receive_message(
            self.sock
        )

        return response

    def close(self):
        """
        Fecha a ligação TCP com o servidor RPC.

        Deve ser chamado para libertar recursos corretamente.
        """

        self.sock.close()