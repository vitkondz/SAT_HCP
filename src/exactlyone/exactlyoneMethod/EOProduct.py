from exactlyone.ExactlyOneMethod import ExactlyOneMethod
from exactlyone.exactlyoneMethod.EOBinomial import EOBinomial
import math

class EOProduct(ExactlyOneMethod):
    
    def __init__(self, var_manager=None):
        super().__init__(var_manager)
    
    def at_most_one(self, cnf, literals):
        n = len(literals)
        p = math.ceil(math.sqrt(n))
        q = math.ceil(n/p)
        R = [self.new_var() for i in range(p)]
        C = [self.new_var() for i in range(q)]
        
        EOBinomial.AMO(cnf, R)
        EOBinomial.AMO(cnf, C)
        for i in range(n):
            cnf.append([-literals[i], R[i//q]])
            cnf.append([-literals[i], C[i%q]])