from primos import is_prime
from game_of_life import game_of_life_sequential
from primos import find_max_prime_parallel
from primos import find_max_prime_sequential


print(is_prime(7))      # True
print(is_prime(10))     # False

print(find_max_prime_sequential(2))
print(find_max_prime_parallel(2, 4))


grid = [
    [0,0,0],
    [1,1,1],
    [0,0,0]
]

result = game_of_life_sequential(grid, 1)

print(result)