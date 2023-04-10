#!/usr/bin/env python3
from classes import *
from scheme import *
import inspect
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element
import timeit

N=8
M=None

# print("Central scheme slot test. Expected output - 4 and 6 should not decrypt")

start = timeit.default_timer()
mkey = setup(N,M)
end = timeit.default_timer()

setuptime = (end - start)

mpk = mkey[0]
msk = mkey[1]

setS = []
settest = []
skarr = [None]*(N)


keygentime = 0
for i in range(N):
	start = timeit.default_timer()
	skarr[i] = keygen(mpk,msk,i)
	end = timeit.default_timer()
	keygentime += (end-start)

	setS.append(i)
	if (not (i==N-4 or i== N-2)):
		settest.append(i)


start = timeit.default_timer()
m = GT.generator()**GT.order().random()
ct = enc(mpk,settest,m)
end = timeit.default_timer()
enctime = (end-start)


ctsize = ct.get_size()


print('Testing Decryption')
dectime = 0
for i in range(N):
	start = timeit.default_timer()
	newm = dec(mpk,settest,skarr[i],ct)
	end = timeit.default_timer()
	dectime += (end-start)

	if(not (newm.eq(m))):
		print("Failed: slot", i)
	else:
		print("Success: slot",i)

print("Benchmarks")

print('Setup time:', setuptime, 'seconds')
print('Key generation time: ', keygentime/N, 'seconds')
print('Encryption time:', enctime, 'seconds')
print('Decryption time:', dectime/N, 'seconds')

print('mpk size:', mpk.get_size(), 'bytes')
print('msk size:', msk.get_size(), 'bytes')
print('Secret Key per user size:',skarr[0].get_size(), 'bytes')

print('Ciphertext size:',ctsize, 'bytes')