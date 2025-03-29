class Graph:
    def __init__(self):
        self.v = None
        self.graph = None
        self.is_directed = False
        
    def add_edge(self, u, v):
        self.graph[u].append(v)
    
    def set_graph(self, graph):
        self.graph = graph
        
    def set_is_directed(self, is_directed):
        self.is_directed = is_directed
        
    def load_graph_from_file(self, url):
        test_set = url.split('/')[-2]
        
        if test_set == "vset":
            graph = {}
            with open(url) as f:
                for line in f:
                    if line.startswith("p"):
                        n = int(line.split()[2])
                        graph = {i: [] for i in range(1, n+1)}
                    else:
                        if line.startswith("e"):
                            u, v = map(int, line.split()[1:])
                        else:
                            u, v = map(int, line.split())
                        if v not in graph[u]:
                            graph[u].append(v)
            self.graph = graph
            self.v = len(graph)
            self.is_directed = True
        
        if test_set == 'fhcpcs':
            graph = {}
            with open(url) as f:
                for line in f:
                    if line.startswith("DIMENSION"):
                        n = int(line.split(':')[1])
                        graph = {i: [] for i in range(1, n+1)}
                    else:
                        # if line start with number differ -1
                        if line[0].isdigit():
                            u, v = map(int, line.split())
                            if v not in graph[u]:
                                graph[u].append(v)
                            if u not in graph[v]:
                                graph[v].append(u)
            self.graph = graph
            self.v = len(graph)
            
        if test_set == 'tsphcp':
            graph = {}
            with open(url) as f:
                for line in f:
                    if line.startswith("D"):
                        n = int(line.split(':')[1])
                        graph = {i: [] for i in range(1, n+1)}
                    else:
                        if line.strip()[0].isdigit() and int(line.strip()[0]) != -1:
                            u, v = map(int, line.split())
                            if v not in graph[u]:
                                graph[u].append(v)  
            self.graph = graph
            self.v = len(graph)
            
        if test_set == 'fhcpsl':
            graph = {}
            with open(url) as f:
                for line in f:
                    if line.startswith("DIMENSION"):
                        n = int(line.split(':')[1])
                        graph = {i: [] for i in range(1, n+1)}
                    else:
                        # if line start with number differ -1
                        if line[0].isdigit():
                            u, v = map(int, line.split())
                            if v not in graph[u]:
                                graph[u].append(v)
                            if u not in graph[v]:
                                graph[v].append(u)
            self.graph = graph
            self.v = len(graph)
            
        