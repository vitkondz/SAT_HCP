# HCP solver solve many instances of Hamiltonian Cycle Problem (HCP) using 
# different successor methods and AMO encodings.
# then write the results to a log file.

from common import *
from unary import unary
from binaryAdder import binaryAdder
from lfsr import lfsr

fileNameSet = [
    "hc-4",
    "hc-5",
    "hc-6",
    "hc-7",
    "hc-8",     # no solution
    "hc-9",     # no solution
    "hc-10",    # no solution
    "hc-11",
    "hc-12",
    "hc-13",    # no solution
    "hc-14",
    "hc-15",    # no solution
    "v-10-3",
    "v-15-3",
    "v-30-4",
    "v-39-3",
    "v-50-5",
    "v-65-3",
    "v-78-5",
    "v-82-5",
    "v-99-7",
    "v-100-2",
    "v-100-5",
    "v-120-5",
    "v-123-5",
    "v-123-7",
    "v-133-5",
    "v-133-7",
    "v-151-7",
    "v-163-5",
    "v-163-7",
    "v-200-3",  
    "v-200-5",
    "v-300-3",
    # "v-300-5",
    # "v-400-3",
    # "v-400-5",
    # "v-500-5",
    # "v-600-5",
    # "v-700-5",
    # "v-800-5",
    # "v-900-5",
    # "v-1000-5",
    # "graphs/benmark_set/SH_64.hcp",
    # "graphs/benmark_set/GPN_122.hcp",
    # "graphs/benmark_set/SNm_124.hcp",
    # "graphs/benmark_set/SH_125.hcp",
    # "graphs/benmark_set/GP3_126.hcp",
    # "graphs/benmark_set/GP0m_130.hcp",
    # "graphs/benmark_set/FLS_170.hcp",
    # "graphs/benmark_set/GPN_244.hcp",
    # "graphs/benmark_set/GP3_246.hcp",
    # "graphs/benmark_set/GP0m_250.hcp",
    # "graphs/benmark_set/SH_250.hcp",
    # "graphs/benmark_set/SNm_252.hcp",
]

successorMethodSet = [
    # "unary", 
    "binaryAdder",
    # "lfsr"
]
from binaryAdder import getH

AMOMethodSet = [
    "AMO_binomial", 
    # "AMO_binary", 
    # "AMO_sequential_encounter", 
    # "AMO_commander", 
    # "AMO_product"
]


def HCP_solver(filename, succesor_method, AMO_method):
    if filename.startswith("hc"):
        graph = init_graph_from_file(f"graphs/hc_set/{filename}.col")
    else:
        graph = init_graph_from_file(f"graphs/v_set/{filename}.txt")
    # graph = init_graph_from_file(filename)
    print(f"Graph {filename} <------------------------------------")
    print("Loading clauses...")
    
    HCPcnf = unary(graph, AMO_method) if succesor_method == "unary" else binaryAdder(graph, AMO_method) if succesor_method == "binaryAdder" else lfsr(graph, AMO_method)
    sat = solve(HCPcnf)
    
    print(sat["status"])
    print("Time:", sat["time"])
    print_result(sat["model"], graph.V, getH, sat)
    print("------------------------------------------------------")
    
    with open("log-file.txt", "a") as f:
        # f.write(f"{filename.ljust(15)}  {succesor_method.ljust(15)}  {AMO_method.ljust(30)} {str(sat["nofVariables"]).ljust(10)} {str(sat["nofClauses"]).ljust(10)} {sat['status'].ljust(10)}  {sat['time'].ljust(10)} {sat['vOfHC']}\n")
        f.write(f"{filename.ljust(15)}  {sat['vOfHC']}\n")

if __name__ == '__main__':
    
    for file in fileNameSet:
        for successor in successorMethodSet:
            for AMO in AMOMethodSet:
                HCP_solver(file, successor, AMO)
    
                
    
    