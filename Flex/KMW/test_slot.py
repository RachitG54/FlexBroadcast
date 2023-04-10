#!/usr/bin/env python3
from classes import *
from schemeKMW import *
# import inspect module
import inspect
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element

N=7
M=None

start = timeit.default_timer()
crs = setup(N,M)
end = timeit.default_timer()

crstime = (end - start)

karray = [None]*(N)
karraytest = [None]*(N)

pkdtime = 0
for i in range(N):
	idash = (5*i+1)%N
	start = timeit.default_timer()
	karray[i] = keygen(crs,idash)
	end = timeit.default_timer()
	pkdtime += (end-start)
	if (not (i==N-4 or i== N-2)):
		karraytest[i]=karray[i]

# any random message
m = GT.generator()**GT.order().random()

start = timeit.default_timer()
ct = enc(crs,karraytest,m)
end = timeit.default_timer()
enctime = (end-start)

ctsize = 0
for c in ct:
	ctsize += c.get_size()

print('Testing Decryption')
dectime = 0
for i in range(N):
	start = timeit.default_timer()
	newm = dec(crs,karraytest,karray[i],ct)
	end = timeit.default_timer()
	dectime += (end-start)

	if(not (newm.eq(m))):
		print("Failed: slot", karray[i].slot)
	else:
		print("Success: slot",karray[i].slot)

print("Benchmarks")

print('CRS generation time:', crstime, 'seconds')
print('Public key directory generation time: ', pkdtime, 'seconds')
print('Encryption time:', enctime, 'seconds')
print('Decryption time:', dectime/N, 'seconds')

print('CRS size:',crs.get_size(), 'bytes')

pkdsz = karray[0].get_pksize()
skdsz = karray[0].get_sksize()

print('Public Key per user size:',pkdsz, 'bytes')
print('Secret Key per user size:',skdsz, 'bytes')
print('Public Key directory size:',pkdsz*N, 'bytes')

print('Ciphertext size:',ctsize, 'bytes')