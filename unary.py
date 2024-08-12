from pysat.solvers import Glucose3
import time

# class Graph impliment by adjacency list
class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = {i: [] for i in range(1, self.V+1)}

    def add_edge(self, u, v):
        self.graph[u].append(v)

    def setGraph(self, graph):
        self.graph = graph
        
# function to load graph from file
def load_graph(url):
    graph = {}
    with open(url) as f:
        for line in f:
            if line.startswith("p"):
                n = int(line.split()[2])
                graph = {i: [] for i in range(1, n+1)}
            elif line.startswith("e"):
                u, v = map(int, line.split()[1:])
                if v not in graph[u]:
                    graph[u].append(v)
            # else:
            #     u, v = map(int, line.split())
            #     if v not in graph[u]:
            #         graph[u].append(v)
            #     if u not in graph[v]:
            #         graph[v].append(u)
    return graph
        
def init_matrices(graph):
    n = len(graph.graph)
    # Hij = True iff the arc (i, j) in the Hamiltonian cycle
    H = [[0] * (n+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for j in range(1, n+1):
            H[i][j] = (i-1) * n + (j-1) + 1
    
    # Uip = True iff vertex i's position is p
    U = [[0] * (n+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for p in range(1, n+1):
            U[i][p] = (i-1) * n + (p-1) + 1 + n*n
    
    return H, U

# AMO, ALO, EO constraints
def at_least_one(cnf, literals):
    cnf.append(literals)
    
def at_most_one(cnf, literals):
    for i in range(len(literals)):
        for j in range(i+1, len(literals)):
            cnf.append([-literals[i], -literals[j]])
            
def exactly_one(cnf, literals):
    at_least_one(cnf, literals)
    at_most_one(cnf, literals)
    
    
# add variables default with True/False to the cnf
def add_default_variables(cnf, n, H, U, graph):
    # Hij = 0 if the arc (i, j) is not in the graph
    for i in range(1, n+1):
        for j in range(1, n+1):
            if j not in graph.graph[i]:
                cnf.append([-H[i][j]])
    # U11 is initialized to True -- value: n*n+1
    cnf.append([U[1][1]])
    
# each vertex has exactly one outgoing arc - constraints (1)
def vertex_outgoing_arcs(cnf, n, H):
    for i in range(1, n+1):
        literals = []
        for j in range(1, n+1):
            literals.append(H[i][j])
        exactly_one(cnf, literals)
    
# each vertex has exactly one incoming arc - constraints (2)
def vertex_incoming_arcs(cnf, n, H):
    for j in range(1, n+1):
        literals = []
        for i in range(1, n+1):
            literals.append(H[i][j])
        exactly_one(cnf, literals)

# H1i -> Ui2 - constraints (3')
def vertex_start(cnf, n, H, U):
    for i in range(2, n+1):
        cnf.append([-H[1][i], U[i][2]])

# Hi1 -> Uin - constraints (4')
def vertex_end(cnf, n, H, U):
    for i in range(2, n+1):
        cnf.append([-H[i][1], U[i][n]])
        
# Hij ^ Uip -> Uj(p+1) - constraints (5')
def vertex_positions(cnf, n, H, U):
    for i in range(2, n+1):
        for j in range(2, n+1):
            for p in range(2, n):
                cnf.append([-H[i][j], -U[i][p], U[j][p+1]])

# exactly one position for each vertex - constraints (6)
def vertex_EO_positions(cnf, n, U):
    for i in range(1, n+1):
        literals = [U[i][p] for p in range(1, n+1)]
        exactly_one(cnf, literals)

if __name__ == '__main__':
    
    # example   
    # gr = {1: [2], 2: [1, 4], 3: [1, 4], 4: [3]}
    # gr = {1: [2, 4], 2: [1, 3, 4, 5], 3: [2, 5], 4: [1, 2, 5], 5: [2, 3, 4]}
    # gr = {1: [2, 4], 2: [1, 3, 4, 5], 3: [2, 5], 4: [1, 2], 5: [2, 3]}
    gr = load_graph("graphs/hc-15.col")
    
    N = len(gr)
    
    # initialize graph
    graph = Graph(N)
    graph.setGraph(gr)
    
    H, U = init_matrices(graph)
    HCPcnf = []
        
    # HCP unary encoding constraints
    add_default_variables(HCPcnf, N, H, U, graph)   # default variables
    vertex_outgoing_arcs(HCPcnf, N, H)              # constraints (1)
    vertex_incoming_arcs(HCPcnf, N, H)              # constraints (2)
    vertex_start(HCPcnf, N, H, U)                   # constraints (3')
    vertex_end(HCPcnf, N, H, U)                     # constraints (4')
    vertex_positions(HCPcnf, N, H, U)               # constraints (5')
    vertex_EO_positions(HCPcnf, N, U)               # constraints (6)
    
    # print("hcp")
    # print(HCPcnf)
    
    
    # SAT solver
    solver = Glucose3()
    solver.append_formula(HCPcnf)
    
    start = time.time()
    if solver.solve():
        end = time.time()
        print("Time:", end-start)
        print("Solution found")
        model = solver.get_model()
        HCP = []
        for var in model:
            if var > 0 and var <= N * N:
                i = (var - 1) // N + 1
                j = (var - 1) % N + 1
                print(i, "->", j)
                HCP.append((i, j))
                
        print("Hamiltonian cycle:", end=" ")
        vertex = 1
        while True:
            print(vertex, end=" ")
            for i, j in HCP:
                if i == vertex:
                    vertex = j
                    break
            if vertex == 1:
                print("-> 1")
                break
            print("->", end=" ")
    else:
        end = time.time()
        print("Time:", end-start)
        print("No solution")    
    
 