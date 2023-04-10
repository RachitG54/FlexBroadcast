#!/usr/bin/env python3
from classes import *
from schemeKMW import *
# import inspect module
import inspect
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element

N=7
M=None

# print("Precomputation slotted scheme test. Expected output - 2 and 5 should not decrypt")

crs = setup(N,M)
karray = [None]*(N)
karraytest = [None]*(N)
for i in range(N):
	idash = (5*i+1)%N
	karray[i] = keygen(crs,idash)
	if (not (i==N-4 or i== N-2)):
		karraytest[i]=karray[i]

m = GT.generator()**GT.order().random()


start = timeit.default_timer()
elt = precomputeenc(crs, karraytest)
end = timeit.default_timer()
preenctime1 = (end-start)

start = timeit.default_timer()
ct = encprecompute(crs,karraytest,m,False,None,elt)
end = timeit.default_timer()
preenctime2 = (end-start)


start = timeit.default_timer()
ct2 = enc(crs,karraytest,m)
end = timeit.default_timer()
enctime = (end-start)

print('Testing Decryption')
for i in range(N):
	start = timeit.default_timer()
	eltdec = precomputedec(crs, karraytest,karray[i],0)
	end = timeit.default_timer()
	predectime1 = (end-start)

	start = timeit.default_timer()
	newm = decprecompute(crs,karraytest,karray[i],ct,False,None,None,0,eltdec)
	end = timeit.default_timer()
	predectime2 = (end-start)


	start = timeit.default_timer()
	newm2 = dec(crs,karraytest,karray[i],ct2)
	end = timeit.default_timer()
	dectime = (end-start)

	if(not (newm.eq(m))):
		print("Failed: slot", karray[i].slot)
	else:
		print("Success: slot",karray[i].slot)

print("Benchmarks")

print('Encryption time:', enctime, 'seconds')
print('Decryption time:', dectime, 'seconds')

print('Precomputation Encryption time:', preenctime1, 'seconds')
print('Precomputation Decryption time:', predectime1, 'seconds')

print('Encryption time after precomputation:', preenctime2, 'seconds')
print('Decryption time after precomputation:', predectime2, 'seconds')