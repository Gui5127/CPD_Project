from game_of_life import *


def test_blinker():

    grid = [
        [0,1,0],
        [0,1,0],
        [0,1,0]
    ]

    expected = [
        [0,0,0],
        [1,1,1],
        [0,0,0]
    ]

    result = game_of_life_sequential(grid, 1)

    assert result == expected


def test_parallel_equals_sequential():

    grid = [
        [0,1,0],
        [0,1,0],
        [0,1,0]
    ]

    seq = game_of_life_sequential(grid, 5)

    par = game_of_life_parallel(grid, 5, 4)

    assert seq == par


if __name__ == "__main__":

    test_blinker()

    test_parallel_equals_sequential()

    print("Todos os testes passaram.")