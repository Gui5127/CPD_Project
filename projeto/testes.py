from primos import find_max_prime_parallel
from primos import find_max_prime_sequential
from primos import is_prime
import multiprocessing
import time
from game_of_life_gui import run_gui

def safe_int(prompt: str, min_value=None) -> int:
    """
    Garante as validações dos parâmetros de entrada.

    Args:
        prompt (str): mensagem de input
        min_value (int | None): valor mínimo permitido

    Returns:
        int: inteiro válido
    """

    while True:

        try:
            value = int(input(prompt))

            if min_value is not None and value < min_value:
                print(f"Valor inválido. Deve ser >= {min_value}")
                continue

            return value

        except ValueError:
            print("Entrada inválida. Introduz um número inteiro.")

def run_is_prime(n):
    """
    Executa teste de primalidade e imprime resultado.

    Args:
        n (int): número a testar

    Returns:
        None
    """

    if n <= 0:
        print("O número deve ser positivo.")
        return

    print("\n===== TESTE É PRIMO =====\n")

    result = is_prime(n)

    print(f"O número é primo? {result}")


def run_sequential(timeout):
    """
    Executa teste da versão sequencial.

    Args:
        timeout (int): tempo limite

    Returns:
        None
    """

    if timeout <= 0:
        print("Timeout inválido.")
        return


    print("\n===== TESTE SEQUENCIAL =====\n")

    start = time.time()

    result = find_max_prime_sequential(timeout)

    elapsed = time.time() - start

    print(f"Timeout: {timeout}s")
    print(f"Maior primo encontrado: {result}")
    print(f"Tempo real: {elapsed:.2f}s")


def run_parallel(timeout, workers):
    """
    Executa teste da versão paralela.

    Args:
        timeout (int): tempo limite
        workers (int): número de processos

    Returns:
        None
    """

    if timeout <= 0:
        print("Timeout inválido.")
        return

    if workers <= 0:
        print("Workers inválidos.")
        return

    print("\n===== TESTE PARALELO =====\n")

    start = time.time()

    result = find_max_prime_parallel(timeout, workers)

    elapsed = time.time() - start

    print(f"Workers: {workers}")
    print(f"Timeout: {timeout}s")
    print(f"Maior primo encontrado: {result}")
    print(f"Tempo real: {elapsed:.2f}s")

def choose_number():
    """
    Solicita ao utilizador um número inteiro através de input.

    A função lê a entrada do utilizador e converte-a para inteiro,
    representando o número que será utilizado em testes (ex: primalidade).

    Returns:
        int: número introduzido pelo utilizador
    """
    return safe_int("\nInsere o número a testar: ")

def choose_timeout():
    """
    Solicita ao utilizador um valor de timeout em segundos.

    Este valor é utilizado para limitar o tempo de execução de algoritmos
    (por exemplo, busca de números primos).

    Returns:
        int: timeout em segundos introduzido pelo utilizador
    """
    return safe_int("\nInsere o timeout (em segundos): ", min_value=1)


def choose_workers():
    """
    Solicita ao utilizador o número de workers (processos) a utilizar.

    Este valor define o nível de paralelismo em tarefas como processamento
    distribuído ou execução paralela de algoritmos.

    Returns:
        int: número de workers introduzido pelo utilizador
    """
    return safe_int("\nInsere o número de workers: ", min_value=1)


def main():
    """
    Menu interativo para testes de:
    - primalidade
    - execução sequencial
    - execução paralela
    - Game of Life GUI

    Returns:
        None
    """

    while True:

        print("\n==============================")
        print("      MENU DE TESTES")
        print("==============================\n")

        print("1. Teste é Primo")
        print("2. Teste Sequencial")
        print("3. Teste Paralelo")
        print("4. Game of Life")
        print("5. Sair")

        choice = input("\nEscolha uma opção: ")

        if choice == "1":

            n = choose_number()

            run_is_prime(n)

        elif choice == "2":

            timeout = choose_timeout()
            run_sequential(timeout)

        elif choice == "3":

            timeout = choose_timeout()
            workers = choose_workers()
            run_parallel(timeout, workers)

        elif choice == "4":

            run_gui()

        elif choice == "5":

            print("\nA terminar programa...\n")
            break

        else:

            print("\nOpção inválida.\n")


if __name__ == "__main__":

    multiprocessing.freeze_support()

    main()