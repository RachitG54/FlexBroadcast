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

# print("Full scheme test. Expected output - 8 should not decrypt")
print("Refer to this test for seeing how to instantiate the scheme")

# print("Running CRS on",N,"users","with the slotted scheme (right side of the bipartite graph) instantiated on",Nnew, "users and degree",d)
start = timeit.default_timer()
crsnew2 = setupfull(N,Nnew,d,M) #Running CRS
end = timeit.default_timer()
crstime = (end-start)

# print("Storing CRS")
crsstr = storecrsfull(crsnew2) #Storing CRS
# print("Reading stored CRS")
crsnew = readcrsfull(crsstr) #Reading CRS


karray = [None]*N
karray2 = [None]*N
karraytest = [None]*(N)


pkdtime = 0
for i in range(N):
	start = timeit.default_timer()
	karray2[i] = keygenfull(crsnew) #generating a key
	end = timeit.default_timer()
	pkdtime += (end-start)

	tempstr = storekeygenfull(karray2[i]) #storing a key
	karray[i] = readkeygenfull(tempstr,crsnew) #reading a key
	if (i!= N-2):
		karraytest[i]=karray[i] #test array does not include node N-2, hence that should not decrypt


m = GT.generator()**GT.order().random()

start = timeit.default_timer()
ct = encfull(crsnew,karraytest,m) #Running encrypt
end = timeit.default_timer()
enctime = (end-start)

print('Testing Decryption')
dectime = 0
for i in range(N):
	start = timeit.default_timer()
	newm = decfull(crsnew,karraytest,karray[i],ct) #Running Decrypt
	end = timeit.default_timer()
	dectime += (end-start)
	if(not (newm.eq(m))):
		print("Failed: user", i)
	else:
		print("Success: user",i)

print("Benchmarks")

print('CRS generation time:', crstime, 'seconds')
print('Public key directory generation time: ', pkdtime, 'seconds')
print('Encryption time:', enctime, 'seconds')
print('Decryption time:', dectime/N, 'seconds')

crssize = crsnew[0].get_size()
print('CRS size:',crsnew[0].get_size(), 'bytes')

pkdsz = 0
skdsz = 0
for j in range(d):
	pkdsz += (4+karray[0][1][j].get_pksize())
	skdsz += (4+karray[0][1][j].get_sksize())


print('Public Key per user size:',pkdsz, 'bytes')
print('Secret Key per user size:',skdsz, 'bytes')

print('Public Key directory size:',pkdsz*N, 'bytes')

print('Ciphertext size:',ct[0].get_size(), 'bytes')