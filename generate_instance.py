import random
import sys
from itertools import combinations


def make_instance(group_size, seed):
    rng = random.Random(seed)
    vertices = list(range(4 * group_size))
    rng.shuffle(vertices)

    groups = []
    for start in range(0, len(vertices), group_size):
        groups.append(vertices[start:start + group_size])

    edges = set()
    for first, second in combinations(groups, 2):
        for u, v in zip(first, rng.sample(second, group_size)):
            edges.add((min(u, v), max(u, v)))

    for _ in range(3):
        rng.shuffle(vertices)
        for u, v in zip(vertices[::2], vertices[1::2]):
            edges.add((min(u, v), max(u, v)))

    return sorted(edges)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: python3 generate_instance.py GROUP_SIZE SEED OUTPUT_FILE")

    group_size = int(sys.argv[1])
    seed = int(sys.argv[2])
    filename = sys.argv[3]
    if group_size < 1:
        sys.exit("GROUP_SIZE must be positive.")

    edges = make_instance(group_size, seed)
    with open(filename, "w") as output:
        print(4 * group_size, len(edges), 4, file=output)
        for u, v in edges:
            print(u, v, file=output)
