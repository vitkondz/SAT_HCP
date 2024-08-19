import time

from common import *

# function to get variable for H and P
def getH(i, j):
    global H
    if (i, j) not in H:
        H[(i, j)] = new_var()
    return H[(i, j)]

def getP(i, bit):  # P(i, bit) = 1 if the i-th bit of the Pi is 1
    global P
    if (i, bit) not in P:
        P[(i, bit)] = new_var()
    return P[(i, bit)]

def exactly_one(cnf, literals):
    ALO(cnf, literals)
    AMO_binomial(cnf, literals)

# add variables with default value to the cnf
def add_default_variables(cnf, n, m, graph):
    # Hij = 0 if the arc (i, j) is not in the graph
    for i in range(1, n+1):
        for j in range(1, n+1):
            if j not in graph.graph[i]:
                cnf.append([-getH(i, j)])
    # P1 = 1 (00..01)
    for bit in range(m):
        if bit == 0:
            cnf.append([getP(1, bit)])
        else:
            cnf.append([-getP(1, bit)])

# each vertex has exactly one outgoing arc - constraints (1)
def vertex_outgoing_arcs(cnf, n):
    for i in range(1, n+1):
        literals = []
        for j in range(1, n+1):
            literals.append(getH(i, j))
        exactly_one(cnf, literals)

# each vertex has exactly one incoming arc - constraints (2)
def vertex_incoming_arcs(cnf, n):
    for j in range(1, n+1):
        literals = []
        for i in range(1, n+1):
            literals.append(getH(i, j))
        exactly_one(cnf, literals)
        
# H1i -> Pi = 2 (00..10) - constraints (3")
def vertex_start(cnf, n, m):
    for i in range(2, n+1):
        for bit in range(m):
            if bit == 1: 
                cnf.append([-getH(1, i), getP(i, bit)])
            else:
                cnf.append([-getH(1, i), -getP(i, bit)])
                
# Hi1 -> Pi = n - constraints (4")
def vertex_end(cnf, n, m):
    # find the n in LFSR 2 bits tap
    binaryN = bin(1)[2:].zfill(m)
    for i in range(2, n+1):
        successor = "".zfill(m)
        for j in range(m-2, -1, -1):
            successor = successor[:j] + binaryN[j+1] + successor[j+1:]
        # alt = int(binaryN[0]) ^ int(binaryN[2]) ^ int(binaryN[3]) ^ int(binaryN[5])
        alt = int(binaryN[0]) ^ int(binaryN[1])
        successor = successor[:m-1] + str(alt)
        binaryN = successor
    
    binaryN = binaryN[::-1]
    for i in range(2, n+1):
        for bit in range(m):
            if binaryN[bit] == '1':
                cnf.append([-getH(i, 1), getP(i, bit)])
            else:
                cnf.append([-getH(i, 1), -getP(i, bit)])
                
# Hij -> Pj = Pi + 1 - constraints (5")
def vertex_positions(cnf, n, m):
    for i in range(2, n+1):
        for j in range(2, n+1):
            for bit in range(m-1):
                # Xi = Yi+1
                cnf.append([-getH(i, j), -getP(i, bit), getP(j, bit+1)])
                cnf.append([-getH(i, j), getP(i, bit), -getP(j, bit+1)])
            # >> Y0 = Xm-1 ^ Xm-2
            # -Y0 v (Xm-1 v Xm-2)
            cnf.append([-getH(i, j), -getP(j, 0), getP(i, m-1), getP(i, m-2)])
            # -Y0 v (-Xm-1 v -Xm-2)
            cnf.append([-getH(i, j), -getP(j, 0), -getP(i, m-1), -getP(i, m-2)])
            # Xm-1 v Y0 v -Xm-2
            cnf.append([-getH(i, j), getP(i, m-1), getP(j, 0), -getP(i, m-2)])
            # Xm-2 v Y0 v -Xm-1
            cnf.append([-getH(i, j), getP(i, m-2), getP(j, 0), -getP(i, m-1)])

def lfsr(graph):
    n = graph.V
    
    global H, P
    H = {}
    P = {}
    m = math.ceil(math.log(n+1, 2))
    cnf = []
    
    add_default_variables(cnf, n, m, graph)
    vertex_outgoing_arcs(cnf, n)
    vertex_incoming_arcs(cnf, n)
    vertex_start(cnf, n, m)
    vertex_end(cnf, n, m)
    vertex_positions(cnf, n, m)
    
    return cnf

if __name__ == '__main__':
    
    graph = init_graph_from_file("graphs/v_set/v-50-5.txt")
    
    HCPcnf = lfsr(graph)
    
    isSat = solve(HCPcnf)
    
    if isSat[0] is not None:
        print("Solution found")
        print_result(isSat[0], graph.V, getH)
        print("Number of clauses:", len(HCPcnf))
        print("Time:", isSat[1])
    else:
        print("No solution")
    