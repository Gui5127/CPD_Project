def count_neighbors(grid, row, col):
    rows = len(grid)
    cols = len(grid[0])

    count = 0

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:

            if dr == 0 and dc == 0:
                continue

            nr = row + dr
            nc = col + dc

            if 0 <= nr < rows and 0 <= nc < cols:
                count += grid[nr][nc]

    return count


def next_generation(grid):

    rows = len(grid)
    cols = len(grid[0])

    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):

            neighbors = count_neighbors(grid, r, c)

            if grid[r][c] == 1:

                if neighbors in (2, 3):
                    new_grid[r][c] = 1

            else:

                if neighbors == 3:
                    new_grid[r][c] = 1

    return new_grid


def game_of_life_sequential(grid, generations):

    current = grid

    for _ in range(generations):
        current = next_generation(current)

    return current