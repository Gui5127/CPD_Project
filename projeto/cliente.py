import socket
import json


HOST = "localhost"
PORT = 5000


def send_request(request):

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client.connect((HOST, PORT))

    client.sendall(
        json.dumps(request).encode()
    )

    response = client.recv(4096)

    client.close()

    return json.loads(response.decode())


def main():

    while True:

        print("\n===== CLIENTE RPC =====\n")

        print("1. is_prime")
        print("2. find_max_prime")
        print("3. game_of_life")
        print("4. list_methods")
        print("5. sair")

        choice = input("\nEscolha: ")

        if choice == "1":

            n = int(input("Número: "))

            request = {
                "method": "is_prime",
                "params": {
                    "n": n
                }
            }

        elif choice == "2":

            timeout = int(input("Timeout: "))
            workers = int(input("Workers: "))

            request = {
                "method": "find_max_prime",
                "params": {
                    "timeout": timeout,
                    "workers": workers
                }
            }

        elif choice == "3":

            grid = [
                [0,1,0],
                [0,1,0],
                [0,1,0]
            ]

            generations = int(
                input("Generations: ")
            )

            request = {
                "method": "game_of_life",
                "params": {
                    "grid": grid,
                    "generations": generations
                }
            }

        elif choice == "4":

            request = {
                "method": "list_methods",
                "params": {}
            }

        elif choice == "5":

            break

        else:

            print("Opção inválida")
            continue

        response = send_request(request)

        print("\nResposta:")
        print(response)


if __name__ == "__main__":

    main()