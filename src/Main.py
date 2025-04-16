from successor.successorMethod.Unary import Unary
from successor.successorMethod.BinaryAdder import BinaryAdder

from exactlyone.exactlyoneMethod.EOBinomial import EOBinomial
from exactlyone.exactlyoneMethod.EOBinary import EOBinary
from exactlyone.exactlyoneMethod.EOCommander import EOCommander
from exactlyone.exactlyoneMethod.EOProduct import EOProduct
from exactlyone.exactlyoneMethod.EOSequentialEncounter import EOSequentialEncounter
from exactlyone.exactlyoneMethod.EOPbLib import EOPbLib
from exactlyone.exactlyoneMethod.EOHybrid import EOHybrid

from HcpSolver import HcpSolver
from utils.common import get_files_from_folder


# data_folder = 'src/data/vset'
# data_folder = 'src/data/fhcpcs'
# data_folder = 'src/data/fhcpsl'
data_folder = 'src/data/fhcppp'

listFiles = get_files_from_folder(data_folder)[9:10]

# with open("log-file.txt", "a") as f: f.write('EOHybrid pre2 s no-sb \n')
# for path in listFiles:

#     hcpSolver = HcpSolver(BinaryAdder(), EOHybrid())
#     graph = hcpSolver.graph
#     graph.load_graph_from_file(path)
#     cnf = hcpSolver.hcpCnf
#     print("Start build clauses for: ", path.split("/")[-1])
#     cnf = hcpSolver.successor.build_clauses(cnf, graph)
#     result = hcpSolver.solve_cadical(cnf)
#     print(result["status"])
#     # hcpSolver.print_result(result["model"], graph, hcpSolver.successor.getH, result)
    
#     with open("log-file.txt", "a") as f:
#         filename = path.split("/")[-1]
#         status = "valid" if result['vOfHC'] == graph.v else "None"
#         f.write(f"{filename.ljust(30)} {str(result['nofVariables']).ljust(10)} {str(result['nofClauses']).ljust(10)} {result['status'].ljust(10)}  {str(result['time']).ljust(10)} {status.ljust(10)}\n")

# with open("log-file.txt", "a") as f: f.write('EOHybrid pre2 no-s no-sb \n')
# for path in listFiles:

#     hcpSolver = HcpSolver(BinaryAdder(), EOHybrid())
#     graph = hcpSolver.graph
#     graph.load_graph_from_file(path)
#     graph.set_start_vertex(1)
#     cnf = hcpSolver.hcpCnf
#     print("Start build clauses for: ", path.split("/")[-1])
#     cnf = hcpSolver.successor.build_clauses(cnf, graph)
#     result = hcpSolver.solve_cadical(cnf)
#     print(result["status"])
#     # hcpSolver.print_result(result["model"], graph, hcpSolver.successor.getH, result)
    
#     with open("log-file.txt", "a") as f:
#         filename = path.split("/")[-1]
#         status = "valid" if result['vOfHC'] == graph.v else "None"
#         f.write(f"{filename.ljust(30)} {str(result['nofVariables']).ljust(10)} {str(result['nofClauses']).ljust(10)} {result['status'].ljust(10)}  {str(result['time']).ljust(10)} {status.ljust(10)}\n")

with open("log-file.txt", "a") as f: f.write('Pblib pre2 s sb \n')
for path in listFiles:

    hcpSolver = HcpSolver(BinaryAdder(), EOPbLib())
    graph = hcpSolver.graph
    graph.load_graph_from_file(path)
    cnf = hcpSolver.hcpCnf
    print("Start build clauses for: ", path.split("/")[-1])
    cnf = hcpSolver.successor.build_clauses(cnf, graph)
    result = hcpSolver.solve_cadical(cnf)
    print(result["status"])
    # hcpSolver.print_result(result["model"], graph, hcpSolver.successor.getH, result)
    
    with open("log-file.txt", "a") as f:
        filename = path.split("/")[-1]
        status = "valid" if result['vOfHC'] == graph.v else "None"
        f.write(f"{filename.ljust(30)} {str(result['nofVariables']).ljust(10)} {str(result['nofClauses']).ljust(10)} {result['status'].ljust(10)}  {str(result['time']).ljust(10)} {status.ljust(10)}\n")

# with open("log-file.txt", "a") as f: f.write('Pblib pre2 no-s no-sb \n')
# for path in listFiles:

#     hcpSolver = HcpSolver(BinaryAdder(), EOPbLib())
#     graph = hcpSolver.graph
#     graph.load_graph_from_file(path)
#     graph.set_start_vertex(1)
#     cnf = hcpSolver.hcpCnf
#     print("Start build clauses for: ", path.split("/")[-1])
#     cnf = hcpSolver.successor.build_clauses(cnf, graph)
#     result = hcpSolver.solve_cadical(cnf)
#     print(result["status"])
#     # hcpSolver.print_result(result["model"], graph, hcpSolver.successor.getH, result)
    
#     with open("log-file.txt", "a") as f:
#         filename = path.split("/")[-1]
#         status = "valid" if result['vOfHC'] == graph.v else "None"
#         f.write(f"{filename.ljust(30)} {str(result['nofVariables']).ljust(10)} {str(result['nofClauses']).ljust(10)} {result['status'].ljust(10)}  {str(result['time']).ljust(10)} {status.ljust(10)}\n")


# ---------------------------------------------------------------------------

# with open("log-file.txt", "a") as f: f.write('EOHybrid pre1 s no-sb \n')
# for path in listFiles:

#     hcpSolver = HcpSolver(BinaryAdder(), EOHybrid())
#     graph = hcpSolver.graph
#     graph.load_graph_from_file(path)
#     cnf = hcpSolver.hcpCnf
#     print("Start build clauses for: ", path.split("/")[-1])
#     hcpSolver.successor.set_is_preprocessing(False)
#     cnf = hcpSolver.successor.build_clauses(cnf, graph)
#     result = hcpSolver.solve_cadical(cnf)
#     print(result["status"])
#     # hcpSolver.print_result(result["model"], graph, hcpSolver.successor.getH, result)
    
#     with open("log-file.txt", "a") as f:
#         filename = path.split("/")[-1]
#         status = "valid" if result['vOfHC'] == graph.v else "None"
#         f.write(f"{filename.ljust(30)} {str(result['nofVariables']).ljust(10)} {str(result['nofClauses']).ljust(10)} {result['status'].ljust(10)}  {str(result['time']).ljust(10)} {status.ljust(10)}\n")

# with open("log-file.txt", "a") as f: f.write('EOHybrid pre1 no-s no-sb \n')
# for path in listFiles:

#     hcpSolver = HcpSolver(BinaryAdder(), EOHybrid())
#     graph = hcpSolver.graph
#     graph.load_graph_from_file(path)
#     graph.set_start_vertex(1)
#     cnf = hcpSolver.hcpCnf
#     print("Start build clauses for: ", path.split("/")[-1])
#     hcpSolver.successor.set_is_preprocessing(False)
#     cnf = hcpSolver.successor.build_clauses(cnf, graph)
#     result = hcpSolver.solve_cadical(cnf)
#     print(result["status"])
#     # hcpSolver.print_result(result["model"], graph, hcpSolver.successor.getH, result)
    
#     with open("log-file.txt", "a") as f:
#         filename = path.split("/")[-1]
#         status = "valid" if result['vOfHC'] == graph.v else "None"
#         f.write(f"{filename.ljust(30)} {str(result['nofVariables']).ljust(10)} {str(result['nofClauses']).ljust(10)} {result['status'].ljust(10)}  {str(result['time']).ljust(10)} {status.ljust(10)}\n")

# with open("log-file.txt", "a") as f: f.write('Pblib pre1 s no-sb \n')
# for path in listFiles:

#     hcpSolver = HcpSolver(BinaryAdder(), EOPbLib())
#     graph = hcpSolver.graph
#     graph.load_graph_from_file(path)
#     cnf = hcpSolver.hcpCnf
#     print("Start build clauses for: ", path.split("/")[-1])
#     hcpSolver.successor.set_is_preprocessing(False)
#     cnf = hcpSolver.successor.build_clauses(cnf, graph)
#     result = hcpSolver.solve_cadical(cnf)
#     print(result["status"])
#     # hcpSolver.print_result(result["model"], graph, hcpSolver.successor.getH, result)
    
#     with open("log-file.txt", "a") as f:
#         filename = path.split("/")[-1]
#         status = "valid" if result['vOfHC'] == graph.v else "None"
#         f.write(f"{filename.ljust(30)} {str(result['nofVariables']).ljust(10)} {str(result['nofClauses']).ljust(10)} {result['status'].ljust(10)}  {str(result['time']).ljust(10)} {status.ljust(10)}\n")

# with open("log-file.txt", "a") as f: f.write('Pblib pre1 no-s no-sb \n')
# for path in listFiles:

#     hcpSolver = HcpSolver(BinaryAdder(), EOPbLib())
#     graph = hcpSolver.graph
#     graph.load_graph_from_file(path)
#     graph.set_start_vertex(1)
#     cnf = hcpSolver.hcpCnf
#     print("Start build clauses for: ", path.split("/")[-1])
#     hcpSolver.successor.set_is_preprocessing(False)
#     cnf = hcpSolver.successor.build_clauses(cnf, graph)
#     result = hcpSolver.solve_cadical(cnf)
#     print(result["status"])
#     # hcpSolver.print_result(result["model"], graph, hcpSolver.successor.getH, result)
    
#     with open("log-file.txt", "a") as f:
#         filename = path.split("/")[-1]
#         status = "valid" if result['vOfHC'] == graph.v else "None"
#         f.write(f"{filename.ljust(30)} {str(result['nofVariables']).ljust(10)} {str(result['nofClauses']).ljust(10)} {result['status'].ljust(10)}  {str(result['time']).ljust(10)} {status.ljust(10)}\n")

