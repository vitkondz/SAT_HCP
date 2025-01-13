# HCP solver solve many instances of Hamiltonian Cycle Problem (HCP) using 
# different successor methods and AMO encodings.
# then write the results to a log file.

from common import *
from successor_functions.unary import unary
from successor_functions.binaryAdder import binaryAdder
from successor_functions.lfsr import lfsr
from config import *

from successor_functions.binaryAdder import getH
# from successor_functions.unary import getH

def HCP_solver(filename, succesor_method, AMO_method):
    graph = init_graph_from_file(filename)
    print(f"Graph {filename} <------------------------------------")
    print("Loading clauses...")
    
    HCPcnf = unary(graph, AMO_method) if succesor_method == "unary" else binaryAdder(graph, AMO_method) if succesor_method == "binaryAdder" else lfsr(graph, AMO_method)
    sat = solve(HCPcnf)
    
    print(sat["status"])
    print("Time:", sat["time"])
    print_result(sat["model"], graph.V, getH, sat)
    print("------------------------------------------------------")
    
    with open("log-file.txt", "a") as f:
        f.write(f"{filename.ljust(15)}  {succesor_method.ljust(15)}  {AMO_method.ljust(30)} {str(sat['nofVariables']).ljust(10)} {str(sat['nofClauses']).ljust(10)} {sat['status'].ljust(10)}  {str(sat['time']).ljust(10)} {sat['vOfHC']}\n")
        # f.write(f"{filename.ljust(25)}  {succesor_method.ljust(15)}  {AMO_method.ljust(30)} {str(sat["nofVariables"]).ljust(10)} {str(sat["nofClauses"]).ljust(10)} {sat['status'].ljust(10)}  {str(sat['time']).ljust(10)} {sat['vOfHC']}\n")
        # f.write(f"{filename.ljust(25)}  {sat['vOfHC']}\n")

if __name__ == '__main__':
    
    for file in graphs:
        for successor in successorMethod:
            for AMO in AMOMethod:
                HCP_solver(file, successor, AMO)
    
                
    
    