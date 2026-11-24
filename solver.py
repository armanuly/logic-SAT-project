import sys

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