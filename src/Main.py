from successor.successorMethod.Unary import Unary
from successor.successorMethod.BinaryAdder import BinaryAdder

from exactlyone.exactlyoneMethod.EOBinomial import EOBinomial
from exactlyone.exactlyoneMethod.EOBinary import EOBinary
from exactlyone.exactlyoneMethod.EOCommander import EOCommander
from exactlyone.exactlyoneMethod.EOProduct import EOProduct
from exactlyone.exactlyoneMethod.EOSequentialEncounter import EOSequentialEncounter
from exactlyone.exactlyoneMethod.EOPbLib import EOPbLib

from HcpSolver import HcpSolver
from utils.common import get_files_from_folder


# data_folder = 'src/data/vset'
data_folder = 'src/data/fhcpcs'
# data_folder = 'src/data/fhcpsl'

listFiles = get_files_from_folder(data_folder)
# print(listFiles)
for path in listFiles:

    hcpSolver = HcpSolver(BinaryAdder(), EOPbLib())
    # hcpSolver.successor.set_is_preprocessing(False)
    graph = hcpSolver.graph
    graph.load_graph_from_file(path)
    cnf = hcpSolver.hcpCnf
    print("Start build clauses for: ", path.split("/")[-1])
    cnf = hcpSolver.successor.build_clauses(cnf, graph)
    result = hcpSolver.solve(cnf)
    print(result["status"])
    hcpSolver.print_result(result["model"], graph, hcpSolver.successor.getH, result)
    
    with open("log-file.txt", "a") as f:
        filename = path.split("/")[-1]
        status = "valid" if result['vOfHC'] == graph.v else "None"
        f.write(f"{filename.ljust(30)} {str(result['nofVariables']).ljust(10)} {str(result['nofClauses']).ljust(10)} {result['status'].ljust(10)}  {str(result['time']).ljust(10)} {status.ljust(10)}\n")

