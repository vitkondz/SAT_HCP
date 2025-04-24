from exactlyone.ExactlyOneMethod import ExactlyOneMethod
import math
from utils.common import add_cnf

THRESHOLD = 32 # threshold for cost function

class EOHybrid(ExactlyOneMethod):
    
    def __init__(self, var_manager=None):
        super().__init__(var_manager)
        
    def PW(self, cnf, literals):
        for i in range(len(literals)):
            for j in range(i+1, len(literals)):
                add_cnf([-literals[i], -literals[j]])
                
    def BS(self, cnf, literals):
        n = len(literals)
        m = n//2
        
        T = self.new_var()
        for i in range(n):
            add_cnf([-literals[i], T if i < m else -T])
            
        self.PW(cnf, literals[:m]) if m <= 4 else self.BS(cnf, literals[:m])
            
        self.PW(cnf, literals[m:]) if n-m <= 4 else self.BS(cnf, literals[m:])
            
    def PD(self, cnf, literals):
        n = len(literals)
        m = math.ceil(math.sqrt(n))
        
        R = [self.new_var() for _ in range(m)]
        C = [self.new_var() for _ in range(m)]
        
        # Mij => Ri ∧ Cj
        for i in range(n):
            add_cnf([-literals[i], R[i // m]])
            add_cnf([-literals[i], C[i % m]])
            
        if m <= THRESHOLD:
            self.BS(cnf, R)
            self.BS(cnf, C)
        else:
            self.PD(cnf, R)
            self.PD(cnf, C)
    
    def at_most_one(self, cnf, literals):
        n = len(literals)
        
        if n > THRESHOLD:
            self.PD(cnf, literals)
        elif n > 4:
            self.BS(cnf, literals)
        else:
            self.PW(cnf, literals)