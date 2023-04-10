#!/usr/bin/env python3
from classes import *
from schemeKMW import *
from schemefull import *
# import inspect module
import inspect
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element
import random
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

N=10
Nnew=20 #vertices on the right
d = 6 # degree

M=None

# print("Precomputation full scheme test. Expected output - 8 should not decrypt")

crsnew = setupfull(N,Nnew,d,M)

karray = [None]*N
karraytest = [None]*(N)
for i in range(N):
	karray[i] = keygenfull(crsnew)
	if (i!= N-2):
		karraytest[i]=karray[i]

# any random message
m = GT.generator()**GT.order().random()

precomputetimeenc = [0, 0, 0, 0, 0, 0, 0]

start = timeit.default_timer()
ct = encfull(crsnew,karraytest,m,False,None,precomputetimeenc)
end = timeit.default_timer()
preenctime = (end-start)

start = timeit.default_timer()
ct2 = encfull(crsnew,karraytest,m) #Running encrypt
end = timeit.default_timer()
enctime = (end-start)

print('Testing Decryption')

for i in range(N):
	precomputetimedec = [0, 0, 0, 0, 0, 0, 0]

	start = timeit.default_timer()
	newm = decfull(crsnew,karraytest,karray[i],ct,False,None,None,[0],0,precomputetimedec)
	end = timeit.default_timer()
	predectime = (end-start)

	start = timeit.default_timer()
	newm2 = decfull(crsnew,karraytest,karray[i],ct2) #Running Decrypt
	end = timeit.default_timer()
	dectime = (end-start)

	if(not (newm.eq(m))):
		print("Failed: user", i)
	else:
		print("Success: user", i)

print("Benchmarks")

print('Encryption time:', enctime, 'seconds')
print('Decryption time:', dectime, 'seconds')

print('Precomputation Encryption time:', preenctime - precomputetimeenc[1], 'seconds')
print('Precomputation Decryption time:', predectime - precomputetimedec[1], 'seconds')

print('Encryption time after precomputation:', precomputetimeenc[1], 'seconds')
print('Decryption time after precomputation:', precomputetimedec[1], 'seconds')