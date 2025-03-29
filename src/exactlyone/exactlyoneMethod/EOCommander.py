from exactlyone.ExactlyOneMethod import ExactlyOneMethod
from exactlyone.exactlyoneMethod.EOBinomial import EOBinomial
import math

class EOCommander(ExactlyOneMethod):
    
    def __init__(self, var_manager=None):
        super().__init__(var_manager)
    
    def at_most_one(self, cnf, literals):
        n = len(literals)
        m = int(math.sqrt(n))
        k = n//m
        C = [self.new_var() for i in range(m)]
        
        EOBinomial.AMO(cnf, C)
        
        G = [[] for i in range(m)]
        for i in range(m):
            G[i] = [literals[j] for j in range(i*k, (i+1)*k)] if i != m-1 else [literals[j] for j in range(i*k, n)]
            cnf.append([-C[i]] + G[i]) # ALO
            
            for ii in range(len(G[i])): # AMO
                for jj in range(ii+1, len(G[i])):
                    cnf.append([-C[i], -G[i][ii], -G[i][jj]])
        
            for j in range(len(G[i])):
                cnf.append([C[i], -G[i][j]])