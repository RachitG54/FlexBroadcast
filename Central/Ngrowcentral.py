#!/usr/bin/env python3
from classes import *
from scheme import *
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
import math

K = int(sys.argv[1])
logNarr = [10, 11, 12, 13, 14]
repeat = 100

logK =  int(math.log2(K))

#file input output for timing numbers
name = "timing"+str(K)+"Ngrowcentral.csv"
with open(name, 'w') as file:
	writer = csv.writer(file,delimiter='\t')
	writer.writerow(["N", "K", "Bsetsize", "CRSgen", "pkdgen", "enc", "dec", "graphtime", "CRSsize", "pkdsize", "skdsize", "ctsize"])

	for iteri in logNarr:
		if (iteri<logK):
			continue;
		logN = iteri
		if (logN > 32):
			raise SystemExit('Setting invalid params in experiment')

		N = 2 ** iteri

		ind = logK
		mainlogK = logK
		mainK = 2** mainlogK


		start = timeit.default_timer()
		mkey = setup(N,None)
		end = timeit.default_timer()
		crstime = end-start

		mpk = mkey[0]
		msk = mkey[1]
		skarr = [None]*(N)

		start = timeit.default_timer()
		for i in range(N):
			skarr[i] = keygen(mpk,msk,i)
		end = timeit.default_timer()

		singlekeytime = (end-start)/N
		pkdtime = (singlekeytime*1)

		# setting test set
		setS = []
		settest = []

		for i in range(K):
			setS.append(i)
			if (not (i==K-4 or i== K-2)):
				settest.append(i)

		# any random message
		m = GT.generator()**GT.order().random()
		print(N,K,mainK)

		start = timeit.default_timer()
		for rep in range(repeat):
			ct = enc(mpk,setS,m)
		end = timeit.default_timer()
		enctime = (end-start)/repeat

		start = timeit.default_timer()

		for rep in range(repeat):
			newm = dec(mpk,setS,skarr[0],ct)
		end = timeit.default_timer()

		dectime = (end-start)/repeat
		print('Ending Timing Measurement')

		if(not (newm.eq(m))):
			print("Does not decrypt")
			print(m)


		pkdsz = 0
		skdsz = 0

		pkdsz += mpk.get_size()
		skdsz += skarr[0].get_size()

		pkdsize = pkdsz
		skdsize = skdsz*N

		
		ctsize = ct.get_size()
		writer.writerow([str(N), K, mainK, crstime, pkdtime, enctime, dectime, 0, 0, pkdsize, skdsize, ctsize])

		