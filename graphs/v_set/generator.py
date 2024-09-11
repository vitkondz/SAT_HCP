# generate a graph with N of vertices and E of edges for each vertex
# and write in file
import random

N = 900
# estimate number of edges of each vertex
E = 5
url = f"v-{N}-{E}.txt"

graph = {i: [] for i in range(1, N+1)}

for i in range(1, N):
    graph[i].append(i+1)
    
graph[N].append(1)

for i in range(1, N+1):
    for j in range(E-1):
        v = random.randint(1, N)
        if i != v and v not in graph[i]:
            graph[i].append(v)
    # shuffer random the list
    random.shuffle(graph[i])
    
            
with open(url, "w") as f:
    f.write(f"p edge {N} {sum([len(graph[i]) for i in graph])}\n")
    for i in graph:
        for j in graph[i]:
            f.write(f"{i} {j}\n")

# print(graph)
print("done")


