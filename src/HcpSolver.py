from VariableManager import VariableManager
from pysat.solvers import Solver
from Graph import Graph
from threading import Timer
from utils.common import interrupt
import os

TIME_BUDGET = 600

class HcpSolver:
    def __init__(self, successor, exactly_one):
        self.successor = successor
        self.exactly_one = exactly_one
        self.var_manager = VariableManager()
        
        successor.set_exactly_one_method(exactly_one)
        successor.set_var_manager(self.var_manager)
        exactly_one.set_var_manager(self.var_manager)
        
        self.sat_solver = Solver(name = 'g4', use_timer = True)
        self.graph = Graph()
        self.result = None
        self.hcpCnf = []
        

    def solve(self, cnf):
        print("Running SAT solver...")

        result = {
            "nofVariables": None,
            "nofClauses": None,
            "status": None,
            "model": None,
            "time": None,
            "vOfHC": None
        }
        
        sat_solver = self.sat_solver
        sat_solver.append_formula(cnf)
        
        result["nofClauses"] = sat_solver.nof_clauses()
        result["nofVariables"] = sat_solver.nof_vars()
        
        timer = Timer(TIME_BUDGET, interrupt, [sat_solver])
        timer.start()
        
        sat_status = sat_solver.solve_limited(expect_interrupt=True)

        if sat_status is False:
            elapsed_time = float(format(sat_solver.time(), ".3f"))
            result["status"] = "UNSAT"
            result["time"] = elapsed_time
        else:
            solution = sat_solver.get_model()
            if solution is None:
                result["status"] = "TIMEOUT"
                result["time"] = 9999
            else:
                elapsed_time = float(format(sat_solver.time(), ".3f"))
                result["model"] = solution
                result["status"] = "SAT"
                result["time"] = elapsed_time
                
        timer.cancel()
        sat_solver.delete()
        return result
    
    def solve_cadical(self, cnf):
        
        def write_to_input():
            # Write data to the file
            with open(input_file, 'w') as writer:
                # Write each clause to the file
                for clause in cnf:
                    for literal in clause: writer.write(str(literal) + " ")
                    writer.write("\n")
            cnf.clear()
            print(f"Input written to {input_file}.\n")
            
        def handle_output():
            result_text = "TIMEOUT"
            time_run = TIME_BUDGET
            solution = []

            try:
                with open(output_file, 'r') as file:
                    lines = file.readlines()
            except FileNotFoundError:
                print(f"Output file '{output_file}' not found.")
                result["status"] = "TIMEOUT"
                result["time"] = TIME_BUDGET
                return
            if lines[0] != "-1\n":
                time_run = float(lines[1])
                print(f"Time run: {time_run}s.")
                if lines[0] == "0\n": result_text = "UNSAT"
                else:
                    result_text = "SAT"
                    solution = list(map(int, lines[2].split()))
            
            result["model"] = solution
            result["status"] = result_text
            result["time"] = time_run
            
            # Delete the output file after handling
            os.remove(output_file)
            
        result = {
            "nofVariables": None,
            "nofClauses": None,
            "status": None,
            "model": None,
            "time": None,
            "vOfHC": None
        }
        
        result["nofClauses"] = len(cnf)
        result["nofVariables"] = self.var_manager.get_var()
        
        input_file = 'src/utils/all_cadical/input.txt'
        output_file = 'src/utils/all_cadical/output.txt'
        
        write_to_input()
        print("Running SAT solver...")
        bashCommand = f"./src/utils/all_cadical/runlim -r {TIME_BUDGET + 10} -o src/utils/all_cadical/report.txt python src/utils/all_cadical/cadical.py"
        os.system(bashCommand)
        
        handle_output()
        return result
    
    def print_result(self, model, graph, getH, result):
        N = graph.v
        if model is None:
            print("No solution found.")
            return
        HCP = []
        for i in range(1, N+1):
            for j in range(1, N+1):
                if getH(i, j) in model:
                    # print(i, "->", j)
                    HCP.append((i, j))
                        
        print("Hamiltonian cycle:", end=" ")
        vertex = 1
        num = 1
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
            num += 1
        print("Veticles of HC: ", num)
        result["vOfHC"] = num

        