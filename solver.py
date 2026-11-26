import sys
import subprocess
import time

def read_graph(filename):
    f = open(filename, "r")
    lines = []
    for line in f:
        line = line.strip()
        if line != "":
            lines.append(line)
    f.close()

    first = lines[0].split()
    n = int(first[0])
    m = int(first[1])
    k = int(first[2])

    adj = []
    for i in range(n):
        adj.append(set())

    for i in range(1, m + 1):
        parts = lines[i].split()
        u = int(parts[0])
        v = int(parts[1])
        if u != v:
            adj[u].add(v)
            adj[v].add(u)

    return n, k, adj

def build_cnf(n, k, adj):
    clauses = []

    for v in range(n):
        at_least_one = []
        for c in range(k):
            at_least_one.append(v * k + c + 1)
        clauses.append(at_least_one)

        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                var1 = v * k + c1 + 1
                var2 = v * k + c2 + 1
                clauses.append([-var1, -var2])

    for c in range(k):
        for v in range(n):
            clause = [v * k + c + 1]
            for u in adj[v]:
                clause.append(u * k + c + 1)
            clauses.append(clause)

    return n * k, clauses

def write_cnf(num_vars, clauses, filename):
    f = open(filename, "w")
    f.write("p cnf " + str(num_vars) + " " + str(len(clauses)) + "\n")
    for clause in clauses:
        line = ""
        for lit in clause:
            line += str(lit) + " "
        f.write(line + "0\n")
    f.close()

def run_glucose(n, k):
    start = time.time()
    res = subprocess.run(["./glucose", "-model", "formula.cnf"], capture_output=True, text=True)
    elapsed = time.time() - start

    output = res.stdout
    if "s SATISFIABLE" not in output:
        return None, elapsed, output

    groups = []
    for i in range(k):
        groups.append([])

    for line in output.splitlines():
        if line.startswith("v "):
            tokens = line.split()
            for t in tokens[1:]:
                val = int(t)
                if val > 0:
                    v = (val - 1) // k
                    c = (val - 1) % k
                    groups[c].append(v)

    return groups, elapsed, output

if __name__ == "__main__":
    filename = sys.argv[1]
    n, k, adj = read_graph(filename)
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        k = int(sys.argv[2])

    num_vars, clauses = build_cnf(n, k, adj)
    write_cnf(num_vars, clauses, "formula.cnf")

    if "--print-cnf" in sys.argv:
        f = open("formula.cnf", "r")
        print(f.read(), end="")
        f.close()

    groups, elapsed, raw = run_glucose(n, k)

    if "--stats" in sys.argv:
        for line in raw.splitlines():
            if line.startswith("c "):
                print(line)

    print("n =", n, "k =", k, "vars =", num_vars, "clauses =", len(clauses))
    print("Time:", round(elapsed, 4), "s")

    if groups is None:
        print("UNSAT")
    else:
        print("SAT")
        for i in range(k):
            groups[i].sort()
            print("D_" + str(i + 1) + ":", groups[i])
            