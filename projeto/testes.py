from primos import find_max_prime_parallel
from primos import find_max_prime_sequential
from primos import is_prime
from game_of_life import game_of_life_sequential
import multiprocessing
import time

TIMEOUT_OPTIONS = [
    5,
    30,
    60,
    120,
    180,
    240,
    300
]


WORKER_OPTIONS = [
    1,
    2,
    3,
    4,
    5,
    6,
    7
]


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


def benchmark_all():

    print("\n===== BENCHMARK COMPLETO =====\n")

    print("\n--- SEQUENCIAL ---\n")

    for timeout in TIMEOUT_OPTIONS:

        start = time.time()

        result = find_max_prime_sequential(timeout)

        elapsed = time.time() - start

        print(f"[SEQ] Timeout={timeout}s | Primo={result} | Tempo={elapsed:.2f}s")

    print("\n--- PARALELO ---\n")

    for workers in WORKER_OPTIONS:

        for timeout in TIMEOUT_OPTIONS:

            start = time.time()

            result = find_max_prime_parallel(timeout, workers)

            elapsed = time.time() - start

            print(
                f"[PAR] Workers={workers} | Timeout={timeout}s "
                f"| Primo={result} | Tempo={elapsed:.2f}s"
            )


def choose_timeout():

    print("\nEscolha timeout:\n")

    for i, timeout in enumerate(TIMEOUT_OPTIONS, start=1):
        print(f"{i}. {timeout}s")

    option = int(input("\nOpção: "))

    return TIMEOUT_OPTIONS[option - 1]


def choose_workers():

    print("\nEscolha número de workers:\n")

    for i, workers in enumerate(WORKER_OPTIONS, start=1):
        print(f"{i}. {workers}")

    option = int(input("\nOpção: "))

    return WORKER_OPTIONS[option - 1]


def main():

    while True:

        print("\n==============================")
        print("      MENU TESTES PRIMOS")
        print("==============================\n")

        print("1. Teste Sequencial")
        print("2. Teste Paralelo")
        print("3. Benchmark Completo")
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

            benchmark_all()

        elif choice == "4":

            print("\nA terminar programa...\n")

            break

        else:

            print("\nOpção inválida.\n")


if __name__ == "__main__":

    multiprocessing.freeze_support()

    main()