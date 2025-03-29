# exactly one version NSC
# def exactly_one(cnf, literals):
#     INF: int = 1_000_000_000
#     k = 1 # for exactly one
#     def find_sqrt(x: int) -> int:
#         for i in range(1, x):
#             if i * i >= x: return i
#         return x

#     n = len(literals) - 1
#     map_register = [[INF for j in range(k + 1)] for i in range(n + 1)]
    
#     lim = find_sqrt(k)
#     id_bonus = 0
#     bonus = []
#     cur = 0
#     for i in range(1, n + 1):
#         cur += 1
#         for j in range(1, cur + 1):
#             map_register[i][j] = new_var()

#         # (1) If a bit is true, the first bit of the corresponding register is true
#         cnf.append([-literals[i], map_register[i][1]])
        
#         # (5) If bit i is off, R[i][i] = 0;
#         cnf.append([literals[i], -map_register[i][cur]])
        
#         if cur != 0:
#             # (2) If R[i - 1][j] = 1, R[i][j] = 1;
#             for j in range(1, cur):
#                 cnf.append([-map_register[i - 1][j], map_register[i][j]])
            
#             # (3) If bit i is on and R[i - 1][j - 1] = 1, R[i][j] = 1;
#             for j in range(2, cur + 1):
#                 cnf.append([-literals[i], -map_register[i - 1][j - 1], map_register[i][j]])
            
#             # (4) If bit i is off and R[i - 1][j] = 0, R[i][j] = 0;
#             for j in range(1, cur):
#                 cnf.append([literals[i], map_register[i - 1][j], -map_register[i][j]])

#             # (6) If R[i - 1][j - 1] = 0, R[i][j] = 0;
#             for j in range(2, cur + 1):
#                 cnf.append([map_register[i - 1][j - 1], -map_register[i][j]])

#         if cur == lim or i == n:
#             # add a bonus bar
#             if id_bonus == 0: bonus.append(map_register[i])
#             else:
#                 a = map_register[i]
#                 b = bonus[id_bonus - 1]

#                 bonus.append([INF for _ in range(k + 1)])
#                 for j in range(1, min(i, k) + 1):
#                     bonus[id_bonus][j] = new_var()

#                 for j in range(1, k + 1):
#                     cnf.append([-a[j], bonus[id_bonus][j]])
#                     cnf.append([-b[j], bonus[id_bonus][j]])
#                 for j1 in range(1, k + 1):
#                     for j2 in range(1, k + 1):
#                         if j1 + j2 <= k: cnf.append([-a[j1], -b[j2], bonus[id_bonus][j1 + j2]])
#                         else: cnf.append([-a[j1], -b[j2]])
#                         if j1 + j2 - 1 <= k: cnf.append([a[j1], b[j2], -bonus[id_bonus][j1 + j2 - 1]])
#             id_bonus += 1
#             cur = 0

#     cnf.append([bonus[id_bonus - 1][k]])

