#!/usr/bin/env python3
"""
Encoding of the Hamiltonian Cycle Problem
Ported from C to Python by Claude, based on code by Marijn Heule
Original last edited on March 3, 2021

The encoding consists of three constraints:
1. When using LFSR, none of the bit-vectors can be all-zero (redundant but useful in practice)
2. Apart from the last position, each position must have exactly one successor
3. Apart from the first position, each position must have exactly one predecessor
4. The successor is encoded using two linear-feedback shift registers:
   one with 1 + x^1 + x^2 and one with 1 + x^2 + x^3
"""

import sys

from pysat.solvers import Glucose3, Cadical195
from threading import Timer
import time

TIME_BUDGET = 120

def lfsr(n, size, xor):
    """Linear-feedback shift register implementation"""
    m = n << 1
    x = m & (1 << size)
    if x:
        m = m - x + 1
    m ^= x >> xor
    return m


def bit(s, b):
    """Calculate bit variable index"""
    return 2 * nEdge + s * nBits + b + 1


def atmostone(array, size):
    """Generate at-most-one constraints"""
    global maxVar, cnf

    if size > 1:
        cnf.append([-array[0], -array[1]])
    
    if size > 2:
        cnf.append([-array[0], -array[2]])
        cnf.append([-array[1], -array[2]])
    
    if size == 4:
        cnf.append([-array[0], -array[3]])
        cnf.append([-array[1], -array[3]])
        cnf.append([-array[2], -array[3]])
    
    if size > 4:
        cnf.append([-array[0], maxVar])
        cnf.append([-array[1], maxVar])
        cnf.append([-array[2], maxVar])
        
        array_copy = array.copy()
        for i in range(3, size):
            array_copy[i - 3] = array[i]
        array_copy[size - 3] = maxVar
        maxVar += 1
        atmostone(array_copy, size - 2)


def main(argv):
    print("Start encoding...")
    global nNode, nEdge, nBits, maxVar, cnf
    cnf = []
    
    if len(argv) < 2:
        print("Usage: python hcp-encode.py <graph_file> [cycle_size]")
        return 1
    
    # Read graph file
    with open(argv[1], 'r') as graph_file:
        for line in graph_file:
            if line.startswith('p'):
                parts = line.strip().split()
                nNode = int(parts[2])
                nEdge = int(parts[3])
                break
    
    # Calculate cycle size
    cycle = 2
    if cycle <= nNode:
        cycle *= 3
    if cycle <= nNode:
        cycle *= 5
    if cycle <= nNode:
        cycle *= 7
    while cycle <= nNode:
        cycle *= 2
    
    if len(argv) > 2:
        cycle = int(argv[2])
    
    # Calculate number of bits needed
    nBits = 0
    k = 1
    while True:
        if (cycle % (1 << k)) == 0:
            nBits += 1
        else:
            break
        k += 1
    
    if (cycle % 3) == 0:
        nBits += 2
    if (cycle % 5) == 0:
        nBits += 3
    if (cycle % 7) == 0:
        nBits += 3
    if (cycle % 511) == 0:
        nBits += 9
    if (cycle % 1023) == 0:
        nBits += 10
    if (cycle % 2047) == 0:
        nBits += 11
    
    # Initialize adjacency matrix
    adj = [[0 for _ in range(nNode)] for _ in range(nNode)]
    
    # Parse graph edges
    max_edge_var = 0
    with open(argv[1], 'r') as graph_file:
        for line in graph_file:
            if line.startswith('e'):
                parts = line.strip().split()
                i = int(parts[1]) - 1
                j = int(parts[2]) - 1
                max_edge_var += 1
                adj[i][j] = max_edge_var
                max_edge_var += 1
                adj[j][i] = max_edge_var
    
    # Calculate vertex degrees
    degree = [0] * nNode
    for i in range(nNode):
        for j in range(i + 1, nNode):
            if adj[i][j]:
                degree[i] += 1
                degree[j] += 1
    
    # Find minimum degree vertex
    minDegree = nNode
    minVertex = 0
    maxDegree = 0
    
    for i in range(nNode):
        if degree[i] < minDegree:
            minDegree = degree[i]
            minVertex = i
        if degree[i] > maxDegree:
            maxDegree = degree[i]
    
    extra = 0
    if minDegree > 2:
        extra = minDegree - 1
    first = minVertex
    
    # Calculate number of clauses for steps
    stepCls = 0
    k = 1
    while True:
        if (cycle % (1 << k)) == 0:
            stepCls += 2 * k
        else:
            break
        k += 1
    
    if (cycle % 3) == 0:
        stepCls += 6
    if (cycle % 5) == 0:
        stepCls += 10
    if (cycle % 7) == 0:
        stepCls += 8
    if (cycle % 511) == 0:
        stepCls += 20
    if (cycle % 1023) == 0:
        stepCls += 22
    if (cycle % 2047) == 0:
        stepCls += 24
    
    # Count variables and clauses
    nVar = 2 * nEdge + nBits * nNode
    nCls = (minDegree + 1) * nBits + stepCls * (2 * nEdge - minDegree) + 1 + minDegree
    
    if (cycle % 3) == 0:
        nCls += nNode
    if (cycle % 5) == 0:
        nCls += nNode * 2
    if (cycle % 7) == 0:
        nCls += nNode
    if (cycle % 511) == 0:
        nCls += nNode
    if (cycle % 1023) == 0:
        nCls += nNode
    if (cycle % 2047) == 0:
        nCls += nNode
    
    for i in range(nNode):
        size = sum(1 for j in range(nNode) if adj[i][j])
        if size > 4:
            nVar += (size - 3) // 2
        if size == 2:
            nCls += 2
        elif size > 2:
            nCls += 3 * (size - 2) + 1
    
    for i in range(nNode):
        size = sum(1 for j in range(nNode) if adj[j][i])
        if size > 4:
            nVar += (size - 3) // 2
        if size == 2:
            nCls += 2
        elif size > 2:
            nCls += 3 * (size - 2) + 1
    
    # Output CNF header
    print(f"p cnf {nVar} {nCls}")
    
    # Ensure bitvectors representing LFSR cannot be ZERO
    for i in range(nNode):
        b = 0
        k = 1
        while True:
            if (cycle % (1 << k)) == 0:
                b += 1
            else:
                break
            k += 1
        
        if (cycle % 3) == 0:
            cnf.append([bit(i, b), bit(i, b+1)])
            b += 2
        if (cycle % 5) == 0:
            cnf.append([-bit(i, b), -bit(i, b+2)])
            cnf.append([-bit(i, b+1), -bit(i, b+2)])
            b += 3
        if (cycle % 7) == 0:
            cnf.append([bit(i, b), bit(i, b+1), bit(i, b+2)])
            b += 3
        if (cycle % 511) == 0:
            cnf.append([bit(i, b+j) for j in range(9)])
            b += 9
        if (cycle % 1023) == 0:
            cnf.append([bit(i, b+j) for j in range(10)])
            b += 10
        if (cycle % 2047) == 0:
            cnf.append([bit(i, b+j) for j in range(11)])
            b += 11
    
    # Exactly one successor constraints
    maxVar = 2 * nEdge + nBits * nNode + 1
    
    neighbors = [0] * maxDegree
    
    for i in range(nNode):
        size = 0
        for j in range(nNode):
            if adj[i][j]:
                neighbors[size] = adj[i][j]
                size += 1
        
        cnf.append([neighbors[j] for j in range(size)])
        atmostone(neighbors[:size], size)

    # Exactly one predecessor constraints
    for i in range(nNode):
        size = 0
        for j in range(nNode):
            if adj[j][i]:
                neighbors[size] = adj[j][i]
                size += 1
        
        cnf.append([neighbors[j] for j in range(size)])
        atmostone(neighbors[:size], size)
    
    # One of first neighbors must be the final connection
    size = 0
    first_neighbors = []
    for i in range(nNode):
        if adj[i][first]:
            first_neighbors.append(i)
            size += 1
    
    cnf.append([adj[neighbor][first] for neighbor in first_neighbors])

    # Symmetry breaking
    for i in range(size):
        clause = [adj[first][first_neighbors[j]] for j in range(i)]
        if clause:
            clause.append(-adj[first_neighbors[i]][first])
            cnf.append(clause)
        else:
            cnf.append([-adj[first_neighbors[i]][first]])
    
    # Initialize starting position
    b = 0
    k = 1
    while True:
        if (cycle % (1 << k)) == 0:
            cnf.append([-bit(first, b)])
            b += 1
        else:
            break
        k += 1
    
    if (cycle % 3) == 0:
        cnf.append([bit(first, b)])
        b += 1
        cnf.append([-bit(first, b)])
        b += 1
    if (cycle % 5) == 0:
        cnf.append([-bit(first, b)])
        b += 1
        cnf.append([-bit(first, b)])
        b += 1
        cnf.append([-bit(first, b)])
        b += 1
    if (cycle % 7) == 0:
        cnf.append([bit(first, b)])
        b += 1
        cnf.append([-bit(first, b)])
        b += 1
        cnf.append([-bit(first, b)])
        b += 1
    
    if (cycle % 511) == 0:
        cnf.append([bit(first, b)])
        b += 1
        for k in range(2, 10):
            cnf.append([-bit(first, b)])
            b += 1
    if (cycle % 1023) == 0:
        cnf.append([bit(first, b)])
        b += 1
        for k in range(2, 11):
            cnf.append([-bit(first, b)])
            b += 1
    if (cycle % 2047) == 0:
        cnf.append([bit(first, b)])
        b += 1
        for k in range(2, 12):
            cnf.append([-bit(first, b)])
            b += 1

    # Initialize termination position (one of the neighbors of first)
    for j in range(minDegree):
        b = 0
        
        k = 1
        while True:
            if (cycle % (1 << k)) == 0:
                clause = [-adj[first_neighbors[j]][first]]
                if ((nNode - 1) & (1 << k) // 2) == 0:
                    clause.append(-bit(first_neighbors[j], b))
                else:
                    clause.append(bit(first_neighbors[j], b))
                cnf.append(clause)
                b += 1
            else:
                break
            k += 1
            
        if (cycle % 3) == 0:
            mask = 1
            for i in range((nNode - 1) % 3):
                mask = lfsr(mask, 2, 1)
            for i in range(2):
                clause = [-adj[first_neighbors[j]][first]]
                if (mask & 1) == 0:
                    clause.append(-bit(first_neighbors[j], b+i))
                else:
                    clause.append(bit(first_neighbors[j], b+i))
                cnf.append(clause)
                mask = mask >> 1
            b += 2
        
        if (cycle % 5) == 0:
            mask = (nNode + 4) % 5
            for i in range(3):
                clause = [-adj[first_neighbors[j]][first]]
                if (mask & 1) == 0:
                    clause.append(-bit(first_neighbors[j], b+i))
                else:
                    clause.append(bit(first_neighbors[j], b+i))
                cnf.append(clause)
                mask = mask >> 1
            b += 3
        
        if (cycle % 7) == 0:
            mask = 1
            for i in range((nNode - 1) % 7):
                mask = lfsr(mask, 3, 1)
            for i in range(3):
                clause = [-adj[first_neighbors[j]][first]]
                if (mask & 1) == 0:
                    clause.append(-bit(first_neighbors[j], b+i))
                else:
                    clause.append(bit(first_neighbors[j], b+i))
                cnf.append(clause)
                mask = mask >> 1
            b += 3
        
        if (cycle % 511) == 0:
            mask = 1
            for i in range((nNode - 1) % 511):
                mask = lfsr(mask, 9, 4)
            for i in range(9):
                clause = [-adj[first_neighbors[j]][first]]
                if (mask & 1) == 0:
                    clause.append(-bit(first_neighbors[j], b+i))
                else:
                    clause.append(bit(first_neighbors[j], b+i))
                cnf.append(clause)
                mask = mask >> 1
            b += 9
        
        if (cycle % 1023) == 0:
            mask = 1
            for i in range((nNode - 1) % 1023):
                mask = lfsr(mask, 10, 3)
            for i in range(10):
                clause = [-adj[first_neighbors[j]][first]]
                if (mask & 1) == 0:
                    clause.append(-bit(first_neighbors[j], b+i))
                else:
                    clause.append(bit(first_neighbors[j], b+i))
                cnf.append(clause)
                mask = mask >> 1
            b += 10
        
        if (cycle % 2047) == 0:
            mask = 1
            for i in range((nNode - 1) % 2047):
                mask = lfsr(mask, 11, 2)
            for i in range(11):
                clause = [-adj[first_neighbors[j]][first]]
                if (mask & 1) == 0:
                    clause.append(-bit(first_neighbors[j], b+i))
                else:
                    clause.append(bit(first_neighbors[j], b+i))
                cnf.append(clause)
                mask = mask >> 1
            b += 11

    # Enforce next relationship
    for i in range(nNode):
        for j in range(nNode):
            if adj[i][j] and j != first:
                b = 0
                if (cycle % 2) == 0:
                    cnf.append([-adj[i][j], bit(j, b), bit(i, b)])
                    cnf.append([-adj[i][j], -bit(j, b), -bit(i, b)])
                    b += 1
                
                k = 2
                while True:
                    if (cycle % (1 << k)) == 0:
                        for l in range(1, k):
                            cnf.append([-adj[i][j], bit(i, b-l), bit(j, b), -bit(i, b)])
                            cnf.append([-adj[i][j], bit(i, b-l), -bit(j, b), bit(i, b)])
                        clause = [-bit(i, b-l) for l in range(1, k)] + [-adj[i][j], bit(j, b), bit(i, b)]
                        cnf.append(clause)
                        clause = [-bit(i, b-l) for l in range(1, k)] + [-adj[i][j], -bit(j, b), -bit(i, b)]
                        cnf.append(clause)
                        b += 1
                    else:
                        break
                    k += 1
                
                if (cycle % 3) == 0:
                    cnf.append([-adj[i][j], bit(j, b), -bit(i, b+1)])
                    cnf.append([-adj[i][j], -bit(j, b), bit(i, b+1)])
                    cnf.append([-adj[i][j], bit(j, b+1), bit(i, b), -bit(i, b+1)])
                    cnf.append([-adj[i][j], bit(j, b+1), -bit(i, b), bit(i, b+1)])
                    cnf.append([-adj[i][j], -bit(j, b+1), bit(i, b), bit(i, b+1)])
                    cnf.append([-adj[i][j], -bit(j, b+1), -bit(i, b), -bit(i, b+1)])
                    b += 2
                
                if (cycle % 5) == 0:
                    cnf.append([-adj[i][j], -bit(j, b), -bit(i, b)])
                    cnf.append([-adj[i][j], -bit(j, b), -bit(i, b+2)])
                    cnf.append([-adj[i][j], bit(j, b), bit(i, b), bit(i, b+2)])
                    cnf.append([-adj[i][j], bit(j, b+1), bit(i, b), -bit(i, b+1)])
                    cnf.append([-adj[i][j], bit(j, b+1), -bit(i, b), bit(i, b+1)])
                    cnf.append([-adj[i][j], -bit(j, b+1), bit(i, b), bit(i, b+1)])
                    cnf.append([-adj[i][j], -bit(j, b+1), -bit(i, b), -bit(i, b+1)])
                    cnf.append([-adj[i][j], -bit(j, b+2), bit(i, b)])
                    cnf.append([-adj[i][j], -bit(j, b+2), bit(i, b+1)])
                    cnf.append([-adj[i][j], bit(j, b+2), -bit(i, b), -bit(i, b+1)])
                    b += 3
                
                if (cycle % 7) == 0:
                    cnf.append([-adj[i][j], bit(j, b), -bit(i, b+2)])
                    cnf.append([-adj[i][j], -bit(j, b), bit(i, b+2)])
                    cnf.append([-adj[i][j], bit(j, b+1), -bit(i, b)])
                    cnf.append([-adj[i][j], -bit(j, b+1), bit(i, b)])
                    cnf.append([-adj[i][j], bit(j, b+2), bit(i, b+1), -bit(i, b+2)])
                    cnf.append([-adj[i][j], bit(j, b+2), -bit(i, b+1), bit(i, b+2)])
                    cnf.append([-adj[i][j], -bit(j, b+2), bit(i, b+1), bit(i, b+2)])
                    cnf.append([-adj[i][j], -bit(j, b+2), -bit(i, b+1), -bit(i, b+2)])
                    b += 3
                
                # Handle larger cycle values (511, 1023, 2047)
                # This part is considerably simplified from the original C code
                # 511 case
                if (cycle % 511) == 0:
                    cnf.append([-adj[i][j], bit(j, b), -bit(i, b+8)])
                    cnf.append([-adj[i][j], -bit(j, b), bit(i, b+8)])
                    for idx in range(1, 5):
                        cnf.append([-adj[i][j], bit(j, b+idx), -bit(i, b+idx-1)])
                        cnf.append([-adj[i][j], -bit(j, b+idx), bit(i, b+idx-1)])
                    cnf.append([-adj[i][j], bit(j, b+5), bit(i, b+4), -bit(i, b+8)])
                    cnf.append([-adj[i][j], bit(j, b+5), -bit(i, b+4), bit(i, b+8)])
                    cnf.append([-adj[i][j], -bit(j, b+5), bit(i, b+4), bit(i, b+8)])
                    cnf.append([-adj[i][j], -bit(j, b+5), -bit(i, b+4), -bit(i, b+8)])
                    for idx in range(6, 9):
                        cnf.append([-adj[i][j], bit(j, b+idx), -bit(i, b+idx-1)])
                        cnf.append([-adj[i][j], -bit(j, b+idx), bit(i, b+idx-1)])
                    b += 9
                
                # 1023 case
                if (cycle % 1023) == 0:
                    cnf.append([-adj[i][j], bit(j, b), -bit(i, b+9)])
                    cnf.append([-adj[i][j], -bit(j, b), bit(i, b+9)])
                    for idx in range(1, 7):
                        cnf.append([-adj[i][j], bit(j, b+idx), -bit(i, b+idx-1)])
                        cnf.append([-adj[i][j], -bit(j, b+idx), bit(i, b+idx-1)])
                    cnf.append([-adj[i][j], bit(j, b+7), bit(i, b+6), -bit(i, b+9)])
                    cnf.append([-adj[i][j], bit(j, b+7), -bit(i, b+6), bit(i, b+9)])
                    cnf.append([-adj[i][j], -bit(j, b+7), bit(i, b+6), bit(i, b+9)])
                    cnf.append([-adj[i][j], -bit(j, b+7), -bit(i, b+6), -bit(i, b+9)])
                    for idx in range(8, 10):
                        cnf.append([-adj[i][j], bit(j, b+idx), -bit(i, b+idx-1)])
                        cnf.append([-adj[i][j], -bit(j, b+idx), bit(i, b+idx-1)])
                    b += 10
                
                # 2047 case
                if (cycle % 2047) == 0:
                    cnf.append([-adj[i][j], bit(j, b), -bit(i, b+10)])
                    cnf.append([-adj[i][j], -bit(j, b), bit(i, b+10)])
                    for idx in range(1, 9):
                        cnf.append([-adj[i][j], bit(j, b+idx), -bit(i, b+idx-1)])
                        cnf.append([-adj[i][j], -bit(j, b+idx), bit(i, b+idx-1)])
                    cnf.append([-adj[i][j], bit(j, b+9), bit(i, b+8), -bit(i, b+10)])
                    cnf.append([-adj[i][j], bit(j, b+9), -bit(i, b+8), bit(i, b+10)])
                    cnf.append([-adj[i][j], -bit(j, b+9), bit(i, b+8), bit(i, b+10)])
                    cnf.append([-adj[i][j], -bit(j, b+9), -bit(i, b+8), -bit(i, b+10)])
                    cnf.append([-adj[i][j], bit(j, b+10), -bit(i, b+9)])
                    cnf.append([-adj[i][j], -bit(j, b+10), bit(i, b+9)])
                    
                    b += 11
    
    # with open('output1.cnf', 'w') as f:
    #     # Write header with number of variables and clauses
    #     f.write(f"p cnf {nVar} {nCls}\n")
    #     # Write each clause
    #     for clause in cnf:
    #         f.write(" ".join(str(lit) for lit in clause) + " 0\n")
    # return

    # Solver ---------------------------------
    result = {
        "status": None,
        "model": None,
        "time": None,
        "time2": None,
    }
    
    
    # sat_solver = Glucose3(use_timer = True)
    sat_solver = Cadical195(use_timer = True)
    sat_solver.append_formula(cnf)
    
    timer = Timer(TIME_BUDGET, lambda s: s.interrupt(), [sat_solver])
    timer.start()
    
    print("Starting solve... Cycle = ", cycle)
    start_time = time.time()
    status = sat_solver.solve_limited(expect_interrupt=True)
    elapsed_time_2 = float(format(time.time() - start_time, ".3f"))
    
    solution = None
    if status is False:
        elapsed_time = float(format(sat_solver.time(), ".3f"))
        print("UNSAT")
        result["time"] = elapsed_time
        result["status"] = 'UNSAT'
        result["time2"] = elapsed_time_2
        print("Time: ", elapsed_time)
    else:
        solution = sat_solver.get_model()
        if solution is None:
            print("TIMEOUT")
            result["time"] = 99999
            result["status"] = 'TIMEOUT'
        else:
            elapsed_time = float(format(sat_solver.time(), ".3f"))
            result["model"] = solution
            print("SAT")
            result["time"] = elapsed_time
            result["time2"] = elapsed_time_2
            result["status"] = "SAT"
            print("Time: ", elapsed_time)
    
    timer.cancel()
    sat_solver.delete()
    
    # ------------------------------------------------------------
    isHC = 'Wrong'
    if solution: 
        is_valid, message = validate(argv[1], solution)
        if is_valid:
            print(f"c {message}")
            isHC = 'Verified'
        else:
            print(f"c {message}")
    # ------------------------------------------------------------
    
    with open('logfile.txt', 'a') as logfile:
        filename = argv[1].split('/')[-1]
        logfile.write(f"{filename.ljust(15)} {str(cycle).ljust(10)} {str(result['status']).ljust(10)} {str(maxVar).ljust(10)} {str(len(cnf)).ljust(10)} {str(result['time2']).ljust(10)} {str(isHC)} \n")
        
        
    # ------------------------------------------------------------

def validate(graph, solution):
    """
    Validate that the solution contains a valid Hamiltonian cycle
    Args:
        graph: Original graph file path
        solution: List of integers representing the solution
    Returns:
        bool: True if solution is valid, False otherwise
    """
    # Read the graph file to get n_node and edges
    n_node = 0
    n_edge = 0
    with open(graph, 'r') as graph_file:
        for line in graph_file:
            if line.startswith('p edge'):
                parts = line.strip().split()
                n_node = int(parts[2])
                n_edge = int(parts[3])
                break
    
    # Initialize lookup table and adjacency matrix
    lookup = [0] * (4 * n_edge + 2)  # +2 to account for 1-based indexing and max_edge+1
    adj = [[0 for _ in range(n_node)] for _ in range(n_node)]
    
    # Parse graph edges
    max_edge = 0
    with open(graph, 'r') as graph_file:
        for line in graph_file:
            if line.startswith('e'):
                parts = line.split()
                i = int(parts[1])
                j = int(parts[2])
                
                # Record edge and its reverse
                max_edge += 1
                adj[i-1][j-1] = max_edge
                lookup[2*max_edge] = i - 1
                lookup[2*max_edge+1] = j - 1
                
                max_edge += 1
                adj[j-1][i-1] = max_edge
                lookup[2*max_edge] = j - 1
                lookup[2*max_edge+1] = i - 1
    
    # Initialize next array
    next_node = [0] * (n_node + 1)
    
    # Process the solution
    for val in solution:
        # Process positive edges within range
        if val > 0 and val <= 2 * n_edge:
            a = lookup[2*val] + 1
            b = lookup[2*val+1] + 1
            next_node[a] = b
    
    # Verify the cycle
    visited = [0] * (n_node + 1)
    a = 1  # Start with node 1
    
    for i in range(1, n_node + 2):
        # print(a , ' -> ', end='')
        if visited[a]:
            if (i - visited[a]) == n_node:
                return True, f"\nVERIFIED HCP of size {n_node}"
            else:
                return False, f"\nERROR: cycle of size {i - visited[a]} out of {n_node}"
        
        visited[a] = i
        a = next_node[a]
    
    return False, "ERROR: No valid cycle found"


if __name__ == "__main__":
    # These need to be global as they are used across functions
    nNode = 0
    nEdge = 0
    nBits = 0
    maxVar = 0
    cnf = []
    
    
    argvs = [
        # ['encode', 'graphs/graph0.edge', 6],
        # ['encode', 'graphs/graph48.edge', 2],
        # ['encode', 'graphs/graph48.edge', 6],
        # ['encode', 'graphs/graph48.edge', 12],
        # ['encode', 'graphs/graph48.edge', 60],
        # ['encode', 'graphs/graph48.edge', 105],
        # ['encode', 'graphs/graph48.edge', 420],
        # ['encode', 'graphs/graph162.edge', 2],
        # ['encode', 'graphs/graph162.edge', 6],
        # ['encode', 'graphs/graph162.edge', 12],
        # ['encode', 'graphs/graph162.edge', 60],
        # ['encode', 'graphs/graph162.edge', 105],
        # ['encode', 'graphs/graph162.edge', 420],
        # ['encode', 'graphs/graph171.edge', 2],
        # ['encode', 'graphs/graph171.edge', 6],
        # ['encode', 'graphs/graph171.edge', 12],
        # ['encode', 'graphs/graph171.edge', 60],
        # ['encode', 'graphs/graph171.edge', 105],
        # ['encode', 'graphs/graph171.edge', 420],
        # ['encode', 'graphs/graph197.edge', 2],
        # ['encode', 'graphs/graph197.edge', 6],
        # ['encode', 'graphs/graph197.edge', 12],
        # ['encode', 'graphs/graph197.edge', 60],
        # ['encode', 'graphs/graph197.edge', 105],
        # ['encode', 'graphs/graph197.edge', 420],
        # ['encode', 'graphs/graph223.edge', 2],
        # ['encode', 'graphs/graph223.edge', 6],
        # ['encode', 'graphs/graph223.edge', 12],
        # ['encode', 'graphs/graph223.edge', 60],
        # ['encode', 'graphs/graph223.edge', 105],
        # ['encode', 'graphs/graph223.edge', 420],
        # ['encode', 'graphs/graph237.edge', 2],
        # ['encode', 'graphs/graph237.edge', 6],
        # ['encode', 'graphs/graph237.edge', 12],
        # ['encode', 'graphs/graph237.edge', 60],
        # ['encode', 'graphs/graph237.edge', 105],
        # ['encode', 'graphs/graph237.edge', 420],
        # ['encode', 'graphs/graph249.edge', 2],
        # ['encode', 'graphs/graph249.edge', 6],
        # ['encode', 'graphs/graph249.edge', 12],
        # ['encode', 'graphs/graph249.edge', 60],
        # ['encode', 'graphs/graph249.edge', 105],
        # ['encode', 'graphs/graph249.edge', 420],
        # ['encode', 'graphs/graph252.edge', 2],
        # ['encode', 'graphs/graph252.edge', 6],
        # ['encode', 'graphs/graph252.edge', 12],
        # ['encode', 'graphs/graph252.edge', 60],
        # ['encode', 'graphs/graph252.edge', 105],
        # ['encode', 'graphs/graph252.edge', 420],
        # ['encode', 'graphs/graph254.edge', 2],
        # ['encode', 'graphs/graph254.edge', 6],
        # ['encode', 'graphs/graph254.edge', 12],
        # ['encode', 'graphs/graph254.edge', 60],
        # ['encode', 'graphs/graph254.edge', 105],
        # ['encode', 'graphs/graph254.edge', 420],
        # ['encode', 'graphs/graph255.edge', 2],
        # ['encode', 'graphs/graph255.edge', 6],
        # ['encode', 'graphs/graph255.edge', 12],
        # ['encode', 'graphs/graph255.edge', 60],
        # ['encode', 'graphs/graph255.edge', 105],
        # ['encode', 'graphs/graph255.edge', 420],
        ['encode', 'graphs/graph424.edge', 2],
        ['encode', 'graphs/graph424.edge', 6],
        ['encode', 'graphs/graph424.edge', 12],
        ['encode', 'graphs/graph424.edge', 60],
        ['encode', 'graphs/graph424.edge', 105],
        ['encode', 'graphs/graph424.edge', 420],
        ['encode', 'graphs/graph446.edge', 2],
        ['encode', 'graphs/graph446.edge', 6],
        ['encode', 'graphs/graph446.edge', 12],
        ['encode', 'graphs/graph446.edge', 60],
        ['encode', 'graphs/graph446.edge', 105],
        ['encode', 'graphs/graph446.edge', 420],
        ['encode', 'graphs/graph470.edge', 2],
        ['encode', 'graphs/graph470.edge', 6],
        ['encode', 'graphs/graph470.edge', 12],
        ['encode', 'graphs/graph470.edge', 60],
        ['encode', 'graphs/graph470.edge', 105],
        ['encode', 'graphs/graph470.edge', 420],
        ['encode', 'graphs/graph491.edge', 2],
        ['encode', 'graphs/graph491.edge', 6],
        ['encode', 'graphs/graph491.edge', 12],
        ['encode', 'graphs/graph491.edge', 60],
        ['encode', 'graphs/graph491.edge', 105],
        ['encode', 'graphs/graph491.edge', 420],
        ['encode', 'graphs/graph506.edge', 2],
        ['encode', 'graphs/graph506.edge', 6],
        ['encode', 'graphs/graph506.edge', 12],
        ['encode', 'graphs/graph506.edge', 60],
        ['encode', 'graphs/graph506.edge', 105],
        ['encode', 'graphs/graph506.edge', 420],
        ['encode', 'graphs/graph522.edge', 2],
        ['encode', 'graphs/graph522.edge', 6],
        ['encode', 'graphs/graph522.edge', 12],
        ['encode', 'graphs/graph522.edge', 60],
        ['encode', 'graphs/graph522.edge', 105],
        ['encode', 'graphs/graph522.edge', 420],
        ['encode', 'graphs/graph526.edge', 2],
        ['encode', 'graphs/graph526.edge', 6],
        ['encode', 'graphs/graph526.edge', 12],
        ['encode', 'graphs/graph526.edge', 60],
        ['encode', 'graphs/graph526.edge', 105],
        ['encode', 'graphs/graph526.edge', 420],
        ['encode', 'graphs/graph529.edge', 2],
        ['encode', 'graphs/graph529.edge', 6],
        ['encode', 'graphs/graph529.edge', 12],
        ['encode', 'graphs/graph529.edge', 60],
        ['encode', 'graphs/graph529.edge', 105],
        ['encode', 'graphs/graph529.edge', 420],
    ]
    for argv in argvs:
        main(argv)