import random
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
import timeit

K = 10 # Broadcast set size
N = 20 # Number of slots
L = 3  # Security parameter

# Construct K x N (sparse) bipartite graph
data = np.ones(K*L)
col1 = np.arange(K)
col_ind = np.repeat(col1,L)
# row_ind = np.random.randint(N, size=K*L)
array_list = [np.random.choice(np.arange(N), size=L, replace=False) for _ in range(K)]
row_ind = np.concatenate(array_list)
# row_ind = np.random.choice(N, size=K * L, replace=False)

graph = csr_matrix((data, (row_ind, col_ind)), dtype=np.int8)

start = timeit.default_timer()
matching = maximum_bipartite_matching(graph, perm_type='row')
end = timeit.default_timer()


twodmatrix = row_ind.reshape(K,L)
print(twodmatrix)
print(matching)
print("expanded matching ", matching[:, np.newaxis])
# 2dmatrix is a 2d array of dimensions K*L
karray = [None]*K
for i in range(K):
    ind = -1
    for j in range(L):
        if(matching[i]==row_ind[i*L+j]):
            ind = j
            print(ind)
            break
    karray[i] = twodmatrix[i][ind]

print(karray)

# Create an array of indices to select from 2dmatrix
matching_expanded = matching[:, np.newaxis]  # Broadcast matching for comparison
indices = np.where(matching_expanded == twodmatrix[np.arange(K), :])
print(indices)
# karray_indices = np.where(matching[:, None] == row_ind.reshape(K, L))[1]
# print(matching[:, None] == row_ind.reshape(K, L))
# print(np.where(matching[:, None] == row_ind.reshape(K, L)))
print('indices are ',indices[1],' length is ',len(indices[1]))
karraynew = twodmatrix[np.arange(K), indices[1]]
print(karraynew.tolist())

# print('Matching exists:', np.all(matching != 1))
print('Matching exists:', not np.any(matching == -1))
print('Time elapsed:', end - start)
