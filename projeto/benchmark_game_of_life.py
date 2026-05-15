import time
import random

from game_of_life import *


def random_grid(rows, cols):

    return [
        [random.randint(0, 1) for _ in range(cols)]
        for _ in range(rows)
    ]


def benchmark(function, *args):

    start = time.perf_counter()

    function(*args)

    end = time.perf_counter()

    return end - start


def run_benchmarks():

    rows = 300
    cols = 300
    generations = 50

    grid = random_grid(rows, cols)

    print(f"\nGrid: {rows}x{cols}")
    print(f"Gerações: {generations}\n")

    # Sequencial
    seq_time = benchmark(
        game_of_life_sequential,
        grid,
        generations
    )

    print(f"Sequencial: {seq_time:.4f} segundos\n")

    # Paralelo
    for workers in [2, 4, 8]:

        par_time = benchmark(
            game_of_life_parallel,
            grid,
            generations,
            workers
        )

        speedup = seq_time / par_time

        print(f"Workers: {workers}")
        print(f"Tempo: {par_time:.4f} segundos")
        print(f"Speedup: {speedup:.2f}x\n")


if __name__ == "__main__":

    run_benchmarks()