# Domatic number with Glucose

## Problem

Given a simple undirected graph $G=(V,E)$ and a positive integer $k$, decide whether its vertices can be partitioned into $k$ dominating sets. A set is dominating if every vertex is either in the set or adjacent to a vertex in the set. The domatic number is the largest number of sets in such a partition. A partition with more than $k$ sets can be reduced to $k$ by merging sets, so the decision problem asks whether the domatic number is at least $k$.

## SAT encoding

The variable $x_{v,c}$ means vertex $v$ belongs to group $c$. Both indices start at zero, and the DIMACS number is `v * k + c + 1`.

1. For each vertex, add a clause containing all its group variables. This requires at least one group.
2. For each vertex and each pair of groups, add a clause with both membership variables negated. This prevents the vertex from belonging to both.
3. For each vertex and each group, add a clause containing that group's variable for the vertex itself and for all of its neighbors. This requires a member of the group in the vertex's closed neighborhood.

The first two rules give a partition. The third makes each group dominating. Conversely, a partition into $k$ dominating sets satisfies all three rules by setting its membership variables true. The encoding uses $nk$ variables. A sequential counter is an alternative to the pairwise clauses in step 2. It uses fewer clauses for large $k$ and adds auxiliary variables.

## Running the solver

Run the commands from the directory containing `solver.py` and `glucose-syrup`. The bundled executable was built on macOS. On another platform, build Glucose 4.2.1 from the [upstream release](https://github.com/audemard/glucose/releases/tag/4.2.1) and put the resulting `glucose-syrup` beside the script. On macOS, with CMake and a C++ compiler installed, these commands build it from the project directory.

```sh
git clone --branch 4.2.1 https://github.com/audemard/glucose.git ../glucose-4.2.1
cmake -S ../glucose-4.2.1 -B ../glucose-4.2.1/build -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build ../glucose-4.2.1/build --target glucose-syrup
cp ../glucose-4.2.1/build/glucose-syrup ./glucose-syrup
```

```sh
python3 solver.py instances/small_sat.txt
python3 solver.py instances/small_unsat.txt
python3 solver.py instances/instance_1000_1.txt
```

The first line of an input file is `n m k`: the number of vertices, edges, and requested groups. The next `m` lines each contain one edge `u v`. Vertices are numbered from `0` to `n-1`. An optional positive integer after the filename overrides `k` for that run. Use `--stats` to show Glucose's statistics or `--print-cnf` to print the formula.

Each run writes `formula.cnf` in the working directory and replaces any previous file with that name. The output gives the formula size, elapsed time, and either `SAT` followed by the dominating sets (`D_1`, `D_2`, etc.) or `UNSAT`.

## Instances

| File | Instance | Expected result |
|---|---|---|
| `small_sat.txt` | Six-vertex cycle with $k=3$ | SAT. The sets {0, 3}, {1, 4}, and {2, 5} each dominate the cycle. |
| `small_unsat.txt` | Five-vertex cycle with $k=3$ | UNSAT. Each dominating set needs at least two vertices, so three disjoint ones would need at least six vertices. |
| `hard_sat.txt` | 3,200 vertices and 9,593 edges with $k=4$ | SAT. Earlier benchmark candidate. |
| `instance_760_7.txt` | 3,040 vertices and 9,113 edges with $k=4$ | SAT. Earlier benchmark candidate. |
| `instance_1000_1.txt` | 4,000 vertices and 11,992 edges with $k=4$ | SAT. Selected hard instance. |

To regenerate the selected hard instance, run the following command. It overwrites that instance file if it already exists.

```sh
python3 generate_instance.py 1000 1 instances/instance_1000_1.txt
```

The arguments are the number of vertices per group, the random seed, and the output path. The generator shuffles the labels, splits them into four equal groups, and adds a random one-to-one matching between each pair of groups. Each vertex belongs to one group and has a neighbor in every other group. This guarantees a partition into four dominating sets. Three extra matchings over all vertices add edges while preserving that partition. The input file lists the edges and the threshold, so Glucose still has to find a partition.

## Experiments

The tests ran on a 16-inch MacBook Pro (2021) with an Apple M1 Pro chip, 16 GB of memory, and macOS Tahoe 26.6.2. The solver was Glucose 4.2.1. The script's `Time:` line measures elapsed time for the Glucose subprocess, including startup and reading the DIMACS file. It excludes graph encoding and model decoding.

For the large cases, each graph was generated with four groups. The group size and seed determine the instance. These were three separate runs with $k=4$.

| File in `instances/` | Vertices per group | Seed | Total vertices | Result | Glucose time (s) |
|---|---:|---:|---:|---|---:|
| `hard_sat.txt` | 800 | 4 | 3,200 | SAT | 2.0068 |
| `instance_760_7.txt` | 760 | 7 | 3,040 | SAT | 1.7036 |
| `instance_1000_1.txt` | 1,000 | 1 | 4,000 | SAT | 44.0178 |

The six-vertex cycle returned `SAT` for $k=3$ in 0.0082 seconds. The five-vertex cycle returned `UNSAT` for $k=3$ in 0.0086 seconds. The 4,000-vertex graph was selected as the hard instance because it returned SAT and took more than 10 seconds. Both the size and seed changed across the large cases, so the measurements describe these particular graphs. From the project folder, run the three included files with their recorded value of $k$.

```sh
python3 solver.py instances/hard_sat.txt | sed -n '1,3p'
python3 solver.py instances/instance_760_7.txt | sed -n '1,3p'
python3 solver.py instances/instance_1000_1.txt | sed -n '1,3p'
```

### Varying the number of groups on a fixed graph

The experiment used the same 4,000-vertex graph (`instances/instance_1000_1.txt`) for every run and changed only the requested number of dominating sets, $k$. The $k=4$ row reuses the hard-instance run above.

| $k$ | Variables | Clauses | Result | Glucose time (s) |
|---:|---:|---:|---|---:|
| 1 | 4,000 | 8,000 | SAT | 0.0094 |
| 2 | 8,000 | 16,000 | SAT | 0.0398 |
| 3 | 12,000 | 28,000 | SAT | 0.0276 |
| 4 | 16,000 | 44,000 | SAT | 44.0178 |
| 5 | 20,000 | 64,000 | Undetermined after 1 hour | - |


The $k=5$ run had not finished after 1 hour experimenting time.

```sh
for k in 1 2 3 4; do
  python3 solver.py instances/instance_1000_1.txt "$k" | sed -n '1,3p'
done
```
