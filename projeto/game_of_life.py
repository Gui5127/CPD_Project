import multiprocessing
from multiprocessing import shared_memory
import struct


# =========================================================
# CONFIG
# =========================================================

CELL_BYTES_SIZE = 4  # int32


# =========================================================
# SHARED MEMORY HELPERS
# =========================================================

def create_shared_grid(grid):
    """
    Cria uma estrutura de memória partilhada a partir de uma grelha 2D.

    Converte uma matriz Python em shared memory linearizada para permitir
    acesso eficiente por múltiplos processos.

    Args:
        grid (list[list[int]]): grelha inicial (0 = morto, 1 = vivo)

    Returns:
        SharedMemory: objeto de memória partilhada inicializado
    """

    rows = len(grid)
    cols = len(grid[0])

    total_cells = rows * cols

    shm = shared_memory.SharedMemory(
        create=True,
        size=total_cells * CELL_BYTES_SIZE
    )

    buffer = shm.buf

    index = 0

    for row in grid:

        for value in row:

            struct.pack_into(
                'i',
                buffer,
                index * CELL_BYTES_SIZE,
                value
            )

            index += 1

    return shm


def read_cell(buffer, cols, row, col):
    """
    Lê o valor de uma célula específica da memória partilhada.

    Args:
        buffer (memoryview): buffer da shared memory
        cols (int): número de colunas da grelha
        row (int): linha da célula
        col (int): coluna da célula

    Returns:
        int: valor da célula (0 ou 1)
    """

    index = row * cols + col

    return struct.unpack_from(
        'i',
        buffer,
        index * CELL_BYTES_SIZE
    )[0]


def write_cell(buffer, cols, row, col, value):
    """
    Escreve um valor numa célula da memória partilhada.

    Args:
        buffer (memoryview): buffer da shared memory
        cols (int): número de colunas da grelha
        row (int): linha da célula
        col (int): coluna da célula
        value (int): valor a escrever (0 ou 1)

    Returns:
        None
    """

    index = row * cols + col

    struct.pack_into(
        'i',
        buffer,
        index * CELL_BYTES_SIZE,
        value
    )


def shared_to_grid(shm, rows, cols):
    """
    Converte memória partilhada de volta para uma grelha 2D Python.

    Args:
        shm (SharedMemory): memória partilhada
        rows (int): número de linhas
        cols (int): número de colunas

    Returns:
        list[list[int]]: grelha reconstruída
    """

    buffer = shm.buf

    grid = []

    for row in range(rows):

        line = []

        for col in range(cols):

            line.append(
                read_cell(
                    buffer,
                    cols,
                    row,
                    col
                )
            )

        grid.append(line)

    return grid


# =========================================================
# GAME OF LIFE
# =========================================================

def count_neighbors(buffer, rows, cols, row, col):
    """
    Conta o número de vizinhos vivos de uma célula no Game of Life.

    Considera as 8 células adjacentes (incluindo diagonais).

    Args:
        buffer (memoryview): memória partilhada
        rows (int): número de linhas
        cols (int): número de colunas
        row (int): linha da célula
        col (int): coluna da célula

    Returns:
        int: número de vizinhos vivos
    """

    neighbors = 0

    for dr in [-1, 0, 1]:

        for dc in [-1, 0, 1]:

            if dr == 0 and dc == 0:
                continue

            nr = row + dr
            nc = col + dc

            if (
                0 <= nr < rows and
                0 <= nc < cols
            ):

                neighbors += read_cell(
                    buffer,
                    cols,
                    nr,
                    nc
                )

    return neighbors


def next_generation(grid):
    """
    Calcula a próxima geração do Game of Life (versão sequencial).

    Aplica as regras clássicas de Conway:
    - célula viva com 2 ou 3 vizinhos sobrevive
    - célula morta com exatamente 3 vizinhos nasce

    Args:
        grid (list[list[int]]): estado atual

    Returns:
        list[list[int]]: nova geração
    """

    rows = len(grid)
    cols = len(grid[0])

    new_grid = [
        [0 for _ in range(cols)]
        for _ in range(rows)
    ]

    for row in range(rows):

        for col in range(cols):

            alive = grid[row][col]

            neighbors = 0

            for dr in [-1, 0, 1]:

                for dc in [-1, 0, 1]:

                    if dr == 0 and dc == 0:
                        continue

                    nr = row + dr
                    nc = col + dc

                    if (
                        0 <= nr < rows and
                        0 <= nc < cols
                    ):

                        neighbors += grid[nr][nc]

            # Conway rules

            if alive == 1:

                if neighbors in (2, 3):
                    new_grid[row][col] = 1

            else:

                if neighbors == 3:
                    new_grid[row][col] = 1

    return new_grid


def game_of_life_sequential(
    grid,
    generations
):
    """
    Executa o Game of Life de forma sequencial por múltiplas gerações.

    Args:
        grid (list[list[int]]): estado inicial
        generations (int): número de iterações

    Returns:
        list[list[int]]: estado final após todas as gerações
    """

    current = grid

    for _ in range(generations):

        current = next_generation(current)

    return current


# =========================================================
# PARALLEL WORKER
# =========================================================

def persistent_worker(
    task_queue,
    result_queue
):
    """
    Worker persistente para execução paralela do Game of Life.

    Recebe tarefas via fila e processa segmentos da grelha usando memória
    partilhada. Após processar, devolve sinal de conclusão.

    Args:
        task_queue (Queue): fila de tarefas
        result_queue (Queue): fila de resultados

    Returns:
        None
    """

    while True:

        task = task_queue.get()

        if task is None:
            break

        (
            worker_id,
            shm_name_current,
            shm_name_next,
            rows,
            cols,
            start_row,
            end_row
        ) = task

        current_shm = shared_memory.SharedMemory(
            name=shm_name_current
        )

        next_shm = shared_memory.SharedMemory(
            name=shm_name_next
        )

        current_buffer = current_shm.buf
        next_buffer = next_shm.buf

        for row in range(start_row, end_row):

            for col in range(cols):

                alive = read_cell(
                    current_buffer,
                    cols,
                    row,
                    col
                )

                neighbors = count_neighbors(
                    current_buffer,
                    rows,
                    cols,
                    row,
                    col
                )

                value = 0

                if alive == 1:

                    if neighbors in (2, 3):
                        value = 1

                else:

                    if neighbors == 3:
                        value = 1

                write_cell(
                    next_buffer,
                    cols,
                    row,
                    col,
                    value
                )

        current_shm.close()
        next_shm.close()

        result_queue.put(worker_id)


# =========================================================
# PARALLEL VERSION
# =========================================================

def game_of_life_parallel(
    grid,
    generations,
    workers
):
    """
    Executa o Game of Life em paralelo utilizando múltiplos processos.

    A grelha é dividida em blocos de linhas e cada worker processa uma parte
    em memória partilhada. Após cada geração, ocorre sincronização.

    Args:
        grid (list[list[int]]): estado inicial
        generations (int): número de iterações
        workers (int): número de processos

    Returns:
        list[list[int]]: estado final após todas as gerações
    """

    rows = len(grid)
    cols = len(grid[0])

    current_shm = create_shared_grid(grid)

    next_shm = shared_memory.SharedMemory(
        create=True,
        size=rows * cols * CELL_BYTES_SIZE
    )

    task_queue = multiprocessing.Queue()

    result_queue = multiprocessing.Queue()

    processes = []

    # Criar workers persistentes
    for _ in range(workers):

        p = multiprocessing.Process(
            target=persistent_worker,
            args=(
                task_queue,
                result_queue
            )
        )

        p.start()

        processes.append(p)

    chunk_size = rows // workers

    for _ in range(generations):

        # Distribuir tarefas
        for i in range(workers):

            start_row = i * chunk_size

            if i == workers - 1:
                end_row = rows
            else:
                end_row = start_row + chunk_size

            task_queue.put(
                (
                    i,
                    current_shm.name,
                    next_shm.name,
                    rows,
                    cols,
                    start_row,
                    end_row
                )
            )

        # Esperar workers
        for _ in range(workers):

            result_queue.get()

        # Swap memória
        current_shm, next_shm = (
            next_shm,
            current_shm
        )

    # Terminar workers
    for _ in range(workers):

        task_queue.put(None)

    for p in processes:

        p.join()

    # Converter resultado final
    result = shared_to_grid(
        current_shm,
        rows,
        cols
    )

    # Cleanup
    current_shm.close()
    current_shm.unlink()

    next_shm.close()
    next_shm.unlink()

    return result