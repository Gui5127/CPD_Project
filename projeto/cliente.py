from rpc_client import RPCClient

def safe_input_int(prompt: str) -> int:
    """
    Lê um inteiro do utilizador de forma segura.

    Repete o input até o utilizador inserir um valor válido.

    Args:
        prompt (str): mensagem a mostrar

    Returns:
        int: valor inteiro válido
    """

    while True:

        try:
            return int(input(prompt))

        except ValueError:
            print("Valor inválido. Introduz um número inteiro.")

def main():
    """
    Interface de linha de comandos para testes RPC.

    Permite:
    - testar primalidade
    - executar versão sequencial/paralela
    - correr Game of Life GUI
    - listar métodos RPC

    Returns:
        None
    """

    rpc = RPCClient()

    while True:

        print("\n===== CLIENTE RPC =====\n")

        print("1. is_prime")
        print("2. find_max_prime_sequential")
        print("3. find_max_prime_parallel")
        print("4. game_of_life")
        print("5. list_methods")
        print("6. sair")

        choice = input("\nEscolha: ")

        # =================================================
        # IS PRIME
        # =================================================

        if choice == "1":

            n = safe_input_int("Número: ")

            response = rpc.request(
                "is_prime",
                {
                    "n": n
                }
            )

            print("\nResposta:")
            print(response)

        # =================================================
        # FIND MAX PRIME SEQUENTIAL
        # =================================================

        elif choice == "2":

            timeout = safe_input_int("Timeout: ")

            response = rpc.request(
                "find_max_prime_sequential",
                {
                    "timeout": timeout,
                }
            )

            print("\nResposta:")
            print(response)

        # =================================================
        # FIND MAX PRIME PARALLEL
        # =================================================

        elif choice == "3":

            timeout = safe_input_int("Timeout: ")

            workers = safe_input_int("Workers: ")

            response = rpc.request(
                "find_max_prime_parallel",
                {
                    "timeout": timeout,
                    "workers": workers
                }
            )

            print("\nResposta:")
            print(response)

        # =================================================
        # GAME OF LIFE GUI
        # =================================================

        elif choice == "4":

            from game_of_life_gui import (
                run_gui
            )

            run_gui()

        # =================================================
        # LIST METHODS
        # =================================================

        elif choice == "5":

            response = rpc.request(
                "list_methods",
                {}
            )

            print("\nResposta:\n")

            for method in response["result"]:

                print(
                    f"Método: {method['name']}"
                )

                print(
                    f"Parâmetros: "
                    f"{method['params']}"
                )

                print(
                    f"Descrição: "
                    f"{method['description']}"
                )

                print()

        # =================================================
        # EXIT
        # =================================================

        elif choice == "6":

            rpc.close()

            print(
                "\nA terminar cliente...\n"
            )

            break

        else:

            print("\nOpção inválida")


if __name__ == "__main__":

    main()