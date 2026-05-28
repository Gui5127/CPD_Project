from rpc_client import RPCClient


def main():

    rpc = RPCClient()

    while True:

        print("\n===== CLIENTE RPC =====\n")

        print("1. is_prime")
        print("3. find_max_prime_sequential")
        print("3. find_max_prime_parallel")
        print("4. game_of_life")
        print("5. list_methods")
        print("6. sair")

        choice = input("\nEscolha: ")

        # =================================================
        # IS PRIME
        # =================================================

        if choice == "1":

            n = int(
                input("Número: ")
            )

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

        elif choice == "3":

            timeout = int(
                input("Timeout: ")
            )

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

            timeout = int(
                input("Timeout: ")
            )

            workers = int(
                input("Workers: ")
            )

            response = rpc.request(
                "find_max_prime",
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

        elif choice == "3":

            from game_of_life_gui import (
                run_gui
            )

            run_gui()

        # =================================================
        # LIST METHODS
        # =================================================

        elif choice == "4":

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

        elif choice == "5":

            rpc.close()

            print(
                "\nA terminar cliente...\n"
            )

            break

        else:

            print("\nOpção inválida")


if __name__ == "__main__":

    main()