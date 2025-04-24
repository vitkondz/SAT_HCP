from exactlyone.ExactlyOneMethod import ExactlyOneMethod
from pypblib import pblib
from pypblib.pblib import PBConfig, Pb2cnf, WeightedLit
from utils.common import add_cnf

class EOPbLib(ExactlyOneMethod):
    
    def __init__(self, var_manager=None):
        super().__init__(var_manager)
    
    def at_most_one(self, cnf, literals):
        pass
    
    def exactly_one(self, cnf, literals):
        var_idx = self.var_manager.get_var()
        
        pbConfig = PBConfig()
        pbConfig.set_AMK_Encoder(pblib.AMK_CARD)
        pb2 = Pb2cnf(pbConfig)
        formula = []
        
        max_var = pb2.encode_at_least_k(literals, 1, formula, var_idx + 1)
        max_var = pb2.encode_at_most_k(literals, 1, formula, max_var + 1)
        
        for clause in formula:
            add_cnf(clause)
            
        self.var_manager.set_var(max_var)