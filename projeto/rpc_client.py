import socket
import json
import struct


HOST = "localhost"
PORT = 5000


# =========================================================
# SEND MESSAGE
# =========================================================

def send_message(sock, message_dict):

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

    def __init__(self):

        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.sock.connect((HOST, PORT))

    def request(self, method, params):

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

        self.sock.close()