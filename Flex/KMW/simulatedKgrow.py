#!/usr/bin/env python3
from classes import *
from schemefull import *
# import inspect module
import inspect
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element
import random
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
import timeit
import sys
import csv
import sqlite3
from os.path import exists
import os
import math
import gc

ratmat = [None]*(33)
degmat = [None]*(33)

ratmat[10] = [1, 1, 1, 1, 1, 2.236, 2.189, 2.162, 2.133, 2.025, 1.197]
degmat[10] = [1, 2, 4, 8, 16, 8, 7, 6, 5, 4, 4]

ratmat[11] = [1, 1, 1, 1, 1, 2.19727, 2.16016, 2.14258, 2.13477, 2.11328, 2.01367, 1.57617]
degmat[11] = [1, 3, 5, 9, 17, 9, 8, 7, 6, 5, 4, 3]

ratmat[12] = [1, 1, 1, 1, 1, 2.404, 2.396, 2.426, 2.121, 2.121, 2.105, 2.006, 1.569]
degmat[12] = [1, 2, 4, 8, 16, 9, 8, 7, 7, 6, 5, 4, 3]

ratmat[13] = [1, 1, 1, 1, 1, 2.3457, 2.33789, 2.35742, 2.40234, 2.11133, 2.11328, 2.10156, 2.00391, 1.56543]
degmat[13] = [1, 3, 5, 9, 17, 10, 9, 8, 7, 7, 6, 5, 4, 3]

ratmat[14] = [1, 1, 1, 1, 1, 2.30078, 2.29297, 2.30664, 2.33984, 2.39062, 2.10547, 2.11133, 2.09961, 2.00195, 1.56445]
degmat[14] = [1, 3, 5, 9, 17, 11, 10, 9, 8, 7, 7, 6, 5, 4, 3]

ratmat[16] = [1, 1, 1, 1, 1, 2.416, 2.424, 2.457, 2.256, 2.285, 2.326, 2.383, 2.102, 2.109, 2.098, 2.002, 1.563]
degmat[16] = [1, 2, 4, 8, 15, 12, 11, 10, 10, 9, 8, 7, 7, 6, 5, 4, 3]

ratmat[20] = [1, 1, 1, 1, 1, 1, 2.438, 2.467, 2.51, 2.348, 2.387, 2.434, 2.494, 2.279, 2.322, 2.38, 2.101, 2.107, 2.098, 2.002, 1.563]
degmat[20] = [1, 2, 4, 8, 15, 32, 14, 13, 12, 12, 11, 10, 9, 9, 8, 7, 7, 6, 5, 4, 3]

ratmat[24] = [1, 1, 1, 1, 1, 1, 2.445, 2.475, 2.51, 2.552, 2.416, 2.455, 2.502, 2.346, 2.385, 2.432, 2.494, 2.28, 2.322, 2.381, 2.102]
degmat[24] = [1, 2, 4, 8, 15, 32, 17, 16, 15, 14, 14, 13, 12, 12, 11, 10, 9, 9, 8, 7, 7]

ratmat[28] = [1, 1, 1, 1, 1, 1, 2.451, 2.479, 2.51, 2.547, 2.436, 2.469, 2.506, 2.551, 2.416, 2.455, 2.502, 2.346, 2.385, 2.432, 2.494]
degmat[28] = [1, 2, 4, 8, 15, 32, 20, 19, 18, 17, 17, 16, 15, 14, 14, 13, 12, 12, 11, 10, 9]

ratmat[32] = [1, 1, 1, 1, 1, 1, 2.566, 2.6, 2.51, 2.541, 2.576, 2.477, 2.508, 2.545, 2.436, 2.469, 2.506, 2.551, 2.416, 2.455, 2.502]
degmat[32] = [1, 2, 4, 8, 15, 32, 22, 21, 21, 20, 19, 19, 18, 17, 17, 16, 15, 14, 14, 13, 12]

# ratarr = [2]*100
# degarr = [14]*100

# N = int(sys.argv[1])
# K = int(sys.argv[2])

N = int(sys.argv[1])
# K = int(sys.argv[2])

# N = 2 ** 20
# K = 1024
# logK =  int(math.log2(K))

logN = int(math.log2(N))

degarr = degmat[logN]
ratarr = ratmat[logN]
if (degarr == None or ratarr == None):
	print("this shouldn't happen")
	degarr = degmat[20]
	ratarr = ratmat[20]

repeat = 100
cachetest = 10


rangemin = 5
rangemax = 11

# val = int(sys.argv[2])

# sizesim = (2**val)*1000
sizesim = 100000
simgpelt = [None]*sizesim

# flagsim = None 
#file input output for timing numbers
# name = "timing"+str(N)+"_"+str(K)+".csv"
# name = "timing"+str(N)+"Kgrowsim.csv"


expname = "timing"+str(N)+"Kgrowsim"
parname = str(rangemin)+"-"+str(rangemax)
# parname = str(val)
fname = "./benchmarks/"+expname + "/"

if not exists(fname):
    os.makedirs(fname)

name = fname+parname+"bench.csv"

with open(name, 'w') as file:
	writer = csv.writer(file,delimiter='\t')
	writer.writerow(["N", "K", "Bsetsize", "CRSgen", "pkdgen", "enc", "dec", "graphtime", "CRSsize", "pkdsize", "skdsize", "ctsize"])

	# this is stored in log
	# for iteri in range(2,15):
	# for iteri in range(val,val+1):
	for iteri in range(rangemin,rangemax):
		if (iteri>logN):
			break;
		K = 2 ** iteri
		logK =  int(math.log2(K))
		ind = logK
		mainlogK = ind
		mainK = 2** mainlogK

		mainKnew = ceil(mainK*ratarr[mainlogK])
		d = ceil(degarr[mainlogK])
		# d = 20
		print(mainK,mainKnew,d)


		start = timeit.default_timer()
		crsnew = setupfull(mainK,mainKnew,d,None)
		end = timeit.default_timer()
		crstime = end-start
		# print('CRS generation time:', end - start)

		# print(ratarr[mainlogK],degarr[mainlogK])

		karray = [None]*(K)
		# karraytest = [None]*(N)

		start = timeit.default_timer()
		for i in range(cachetest):
			karray[i] = keygenfull(crsnew)
		end = timeit.default_timer()

		#code for picking up simulated group elements
		# only when val type experiment is set
		# sizesim = min(K*K,sizesim)
		if(simgpelt[0]==None):
			print("simulating group elements")
			for i in range(sizesim):
			    r = G1.order().random()
			    simgpelt[i] = crsnew[0].g1 ** r

			    # r = G1.order().random()
			    # simgpelt[i] = G1.hash_to_point(str(i))
			print("simulation finished")

		# Klimit = 4096
		for i in range(cachetest,K):
			# karray[i] = simkeygenfull(simgpelt, crsnew)
			karray[i] = simkeygenfull2(simgpelt, crsnew)
			# if(i>Klimit):
			# 	index = random.randint(0, Klimit)
			# 	karray[i]=simkeygenfull(karray[index], crsnew)
			# else:
			# 	karray[i] = simkeygenfull(simgpelt, crsnew)

		# print('Key generation time:', end - start)
		# print('Per user key generation time:', (end - start)/K)
		# print('Key generation time:', ((end - start)*N)/K)

		singlekeytime = (end-start)/cachetest
		pkdtime = (singlekeytime*1)

		# any random message
		m = GT.generator()**GT.order().random()
		# m = GT.neutral_element()
		# print(m)
		# print(len(karray))

		bucket = ceil(K/mainK)

		# ctdumset = [None]*bucket
		# s = G2.order().random()
		# Zs = crsnew[0].Z ** s
		# ct1 = Zs * m;
		# ct2 = crsnew[0].g2 ** s
		# for i in range(bucket):
		# 	minind = i*mainK
		# 	maxind = min((i+1)*mainK,K)
		# 	# print(minind,maxind)
		# 	newkarray = karray[minind:maxind]
		# 	ctdumset[i] = enclazyfixfull(crsnew,newkarray,m,True,s)

		gc.collect()

		ctarr = [None]*bucket

				
		start = timeit.default_timer()

		for rep in range(repeat):
			s = G2.order().random()
			Zs = crsnew[0].Z ** s
			ct1 = Zs * m;
			ct2 = crsnew[0].g2 ** s
			for i in range(bucket):
				minind = i*mainK
				maxind = min((i+1)*mainK,K)
				# print(minind,maxind)
				newkarray = karray[minind:maxind]
				# ctarr[i] = encfull(crsnew,newkarray,m,True,s)
				ctarr[i] = encfull(crsnew,newkarray,m,True,s)

		end = timeit.default_timer()
		enctime = (end-start)/repeat
		# cur.execute("INSERT OR IGNORE INTO timing(rowid, enc) VALUES(?,?)",(1,end-start))
		# print('Encryption time:', end - start)


		rightind = 1 // mainK
		minind = rightind*mainK
		maxind = min((rightind+1)*mainK,K)
		newkarray = karray[minind:maxind]

		start = timeit.default_timer()
		for rep in range(repeat):
			gtime=[0]
			newm = decfull(crsnew,newkarray,karray[1],ctarr[rightind],True,ct1,ct2,gtime,1)
			# newm = decfull2(crsnew,newkarray,karray[1],ctarr[rightind],True,ct1,ct2,gtime,1)
		end = timeit.default_timer()
		# print('Decryption time:', end - start)

		dectime = (end-start)/repeat
		# cur.execute("INSERT OR IGNORE INTO timing(rowid, dec) VALUES(?,?)",(1,end-start))
		print('Ending Timing Measurement')

		# if(not (newm.eq(m))):
		# 	print("Does not decrypt")

		crssize = crsnew[0].get_size()
		# print('CRS size:',crsnew[0].get_size())

		pkdsz = 0
		skdsz = 0
		# for i in range(N):
		for j in range(d):
			pkdsz += (4+karray[0][1][j].get_pksize())
			skdsz += (4+karray[0][1][j].get_sksize())

		# print('Public Key directory size:',pkdsz*N)
		# print('Secret Key directory size:',skdsz*N)

		pkdsize = pkdsz*N
		skdsize = skdsz*N

		# print('Public Key per user size:',pkdsz)
		# print('Secret Key per user size:',skdsz)

		ctsize = 0
		ctsize += len(ct1.to_binary())
		ctsize += len(ct2.to_binary())
		for i in range(bucket):
			for c in ctarr[i]:
				ctsize += c.get_size()

		writer.writerow([str(N), K, mainK, crstime, pkdtime, enctime, dectime, gtime[0], crssize, pkdsize, skdsize, ctsize])
	# print('Ciphertext size:',ctsize)

	# for i in range(N):
	# 	newm = dec(crs,karray,karray[i],ct)
	# 	if(not (newm.eq(m))):
	# 		print(str(i)+" does not decrypt")
		# print(newm)
		# print(inspect.getmembers(karray[i]))
		# print(karray[i].__dir__())


	# con.commit()
	# con.close()