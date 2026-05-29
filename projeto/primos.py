import multiprocessing
import time


SEGMENT_SIZE = 10_000_000


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

        if candidate == 2:
            candidate = 3
        else:
            candidate += 2

    return max_prime


def pipeline_worker(
    worker_id,
    workers,
    pipeline_order,
    segment_starts,
    segment_primes,
    next_segment_start,
    shared_max,
    end_time,
    lock
):

    while time.time() < end_time:

        with lock:

            # Encontrar posição atual
            my_position = -1

            for i in range(workers):

                if pipeline_order[i] == worker_id:
                    my_position = i
                    break

            my_segment_start = (
                segment_starts[worker_id]
            )

            my_segment_end = (
                my_segment_start + SEGMENT_SIZE
            )

            # Primeiro worker
            if my_position == 0:
                target_prime = 2
            else:

                previous_worker = (
                    pipeline_order[my_position - 1]
                )

                target_prime = (
                    segment_primes[previous_worker]
                )

        candidate = my_segment_start

        if candidate <= 2:
            candidate = 2
        elif candidate % 2 == 0:
            candidate += 1

        found = False

        while (
            candidate < my_segment_end and
            time.time() < end_time
        ):

            if is_prime(candidate):

                if candidate > target_prime:

                    with lock:

                        # Revalidar posição
                        my_position = -1

                        for i in range(workers):

                            if (
                                pipeline_order[i] ==
                                worker_id
                            ):

                                my_position = i
                                break

                        if my_position > 0:

                            previous_worker = (
                                pipeline_order[
                                    my_position - 1
                                ]
                            )

                            previous_prime = (
                                segment_primes[
                                    previous_worker
                                ]
                            )

                            if candidate > previous_prime:

                                # Atualizar primo
                                segment_primes[
                                    worker_id
                                ] = candidate

                                # Worker reciclado
                                recycled_worker = (
                                    previous_worker
                                )

                                # Novo segmento
                                new_segment = (
                                    next_segment_start.value
                                )

                                next_segment_start.value += (
                                    SEGMENT_SIZE
                                )

                                # PRINT DO SALTO DE SEGMENTO
                                """print(
                                    f"[Worker {recycled_worker}] "
                                    f"saltou para segmento "
                                    f"{new_segment} -> "
                                    f"{new_segment + SEGMENT_SIZE}"
                                )"""

                                segment_starts[
                                    recycled_worker
                                ] = new_segment

                                segment_primes[
                                    recycled_worker
                                ] = 0

                                # Rotação manual
                                for j in range(
                                    my_position - 1,
                                    workers - 1
                                ):

                                    pipeline_order[j] = (
                                        pipeline_order[
                                            j + 1
                                        ]
                                    )

                                pipeline_order[
                                    workers - 1
                                ] = recycled_worker

                                # Máximo global
                                if (
                                    candidate >
                                    shared_max.value
                                ):

                                    shared_max.value = (
                                        candidate
                                    )

                        else:

                            # Primeiro worker
                            segment_primes[
                                worker_id
                            ] = candidate

                            if (
                                candidate >
                                shared_max.value
                            ):

                                shared_max.value = (
                                    candidate
                                )

                    found = True

                    break

            if candidate == 2:
                candidate = 3
            else:
                candidate += 2

        if not found:
            time.sleep(0.0005)


def find_max_prime_parallel(
    timeout: int,
    workers: int
) -> int:

    end_time = time.time() + timeout

    # Arrays partilhados
    pipeline_order = multiprocessing.Array(
        'i',
        range(workers)
    )

    segment_starts = multiprocessing.Array(
        'q',
        [
            i * SEGMENT_SIZE
            for i in range(workers)
        ]
    )

    segment_primes = multiprocessing.Array(
        'q',
        [0] * workers
    )

    next_segment_start = multiprocessing.Value(
        'q',
        workers * SEGMENT_SIZE
    )

    shared_max = multiprocessing.Value(
        'q',
        2
    )

    lock = multiprocessing.Lock()

    processes = []

    for worker_id in range(workers):

        p = multiprocessing.Process(
            target=pipeline_worker,
            args=(
                worker_id,
                workers,
                pipeline_order,
                segment_starts,
                segment_primes,
                next_segment_start,
                shared_max,
                end_time,
                lock
            )
        )

        processes.append(p)

        p.start()

    for p in processes:
        p.join()

    return shared_max.value