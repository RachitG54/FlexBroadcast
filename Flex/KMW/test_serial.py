#!/usr/bin/env python3
from classes import *
from schemeKMW import *
# import inspect module
import inspect
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element

N=7
M=None
# print("Serialization slotted scheme test. Expected output - 2 and 5 should not decrypt")

crssave = setup(N,M)
crsstr = crssave.serialize()
# print(len(crsstr))

crs = CRS()
crs.deserialize(crsstr)

karray = [None]*(N)
karray2 = [None]*(N)
karraytest = [None]*(N)
for i in range(N):
	idash = (5*i+1)%N
	karray2[i] = keygen(crs,idash)
	tempstr = karray2[i].serialize()
	karray[i] = Key(None,None,None,None,None)
	karray[i].deserialize(tempstr)
	if (not (i==N-4 or i== N-2)):
		karraytest[i]=karray[i]

# any random message
m = GT.generator()**GT.order().random()
ct = enc(crs,karraytest,m)


print('Testing Decryption')
for i in range(N):
	newm = dec(crs,karraytest,karray[i],ct)
	if(not (newm.eq(m))):
		print("Failed: slot", karray[i].slot)
	else:
		print("Success: slot",karray[i].slot)


print('Benchmarks')
print('CRS size:',crssave.get_size(), 'bytes')
print('Public Key per user size:',karray[0].get_pksize(), 'bytes')
print('Secret Key per user size:',karray[0].get_sksize(), 'bytes')
print('Serialized CRS size:',len(crsstr), 'bytes')
print('Serialized key per user size (includes public and secret keys):',len(tempstr), 'bytes')