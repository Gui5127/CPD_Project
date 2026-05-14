import multiprocessing
import time


def is_prime(n: int) -> bool:
    if n < 2:
        return False

    if n in (2, 3):
        return True

    if n % 2 == 0 or n % 3 == 0:
        return False

    divisor = 5

    while divisor * divisor <= n:
        if n % divisor == 0 or n % (divisor + 2) == 0:
            return False

        divisor += 6

    return True

def find_max_prime_sequential(timeout: int) -> int:
    start = time.time()

    candidate = 2
    max_prime = 2

    while time.time() - start < timeout:

        if is_prime(candidate):
            max_prime = candidate

        candidate += 1

    return max_prime


def prime_worker(start, step, end_time, shared_max):
    candidate = start

    while time.time() < end_time:

        if is_prime(candidate):

            if candidate > shared_max.value:
                shared_max.value = candidate

        candidate += step


def find_max_prime_parallel(timeout: int, workers: int) -> int:

    end_time = time.time() + timeout

    shared_max = multiprocessing.Value('q', 2)

    processes = []

    for i in range(workers):

        start = 3 + (i * 2)
        step = workers * 2

        p = multiprocessing.Process(
            target=prime_worker,
            args=(start, step, end_time, shared_max)
        )

        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    return shared_max.value