from primos import find_max_prime_parallel
from primos import find_max_prime_sequential
import multiprocessing
import time
from game_of_life_gui import run_gui


def run_sequential(timeout):

    print("\n===== TESTE SEQUENCIAL =====\n")

    start = time.time()

    result = find_max_prime_sequential(timeout)

    elapsed = time.time() - start

    print(f"Timeout: {timeout}s")
    print(f"Maior primo encontrado: {result}")
    print(f"Tempo real: {elapsed:.2f}s")


def run_parallel(timeout, workers):

    print("\n===== TESTE PARALELO =====\n")

    start = time.time()

    result = find_max_prime_parallel(timeout, workers)

    elapsed = time.time() - start

    print(f"Workers: {workers}")
    print(f"Timeout: {timeout}s")
    print(f"Maior primo encontrado: {result}")
    print(f"Tempo real: {elapsed:.2f}s")


def choose_timeout():
    return int(input("\nInsere o timeout (em segundos): "))


def choose_workers():
    return int(input("\nInsere o número de workers: "))


def main():

    while True:

        print("\n==============================")
        print("      MENU DE TESTES")
        print("==============================\n")

        print("1. Teste Sequencial")
        print("2. Teste Paralelo")
        print("3. Game of Life")
        print("4. Sair")

        choice = input("\nEscolha uma opção: ")

        if choice == "1":

            timeout = choose_timeout()
            run_sequential(timeout)

        elif choice == "2":

            timeout = choose_timeout()
            workers = choose_workers()
            run_parallel(timeout, workers)

        elif choice == "3":

            run_gui()

        elif choice == "4":

            print("\nA terminar programa...\n")
            break

        else:

            print("\nOpção inválida.\n")


if __name__ == "__main__":

    multiprocessing.freeze_support()

    main()