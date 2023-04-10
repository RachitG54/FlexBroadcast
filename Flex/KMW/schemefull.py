#!/usr/bin/env python3

from math import ceil,floor, log2,sqrt
from operator import mod

from classes import *
from schemeKMW import *
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element
from petrelic.bn import Bn
import sqlite3
from os.path import exists

import random
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
import timeit

def floattrunc(a):
    return format(a, ".7f")

def setupfull(N,Nnew = None,d=None,M = None):
    if (Nnew == None):
        Nnew = int(2*N)
    if (d == None):
        d = 20
    crs = setup(Nnew,M)
    crsnew = (crs,Nnew,d)
    return crsnew

def storecrsfull(crsfull=None):
    if(crsfull==None):
        raise SystemExit('Invalid Storing')
        return

    serialized_crs = crsfull[0].serialize()
    data_to_pack = (serialized_crs, crsfull[1], crsfull[2])
    crsstr = msgpack.packb(data_to_pack, use_bin_type=True)
    return crsstr

def readcrsfull(crsstr=None):
    if(crsstr==None):
        raise SystemExit('Invalid Loading')
        return
    unpacked_data = msgpack.unpackb(crsstr, raw=False)
    deserialized_crs = CRS()
    deserialized_crs.deserialize(unpacked_data[0])
    crsfull = (deserialized_crs,unpacked_data[1],unpacked_data[2])
    return crsfull


def keygenfull(crsnew):

    if(crsnew[1] == None or crsnew[2] == None):
        raise SystemExit('Invalid Parameters')

    Nnew = crsnew[1]
    d = crsnew[2]
    slots = [None]*d
    keys = [None]*d
    var = np.random.choice(Nnew,d,replace=False)
    # print(var)
    for i in range(d):
        slots[i] = int(var[i])
        # slots[i] = random.randrange(Nnew)
        keys[i] = keygen(crsnew[0],slots[i])

    # print(Nnew,slots)
    ki = (slots,keys)
    return ki

def storekeygenfull(keygenfull=None):
    if(keygenfull==None):
        raise SystemExit('Invalid Storing')
        return
    serialized_keys = [key.serialize() for key in keygenfull[1]]
    data_to_pack = (keygenfull[0], serialized_keys)
    keygenstr = msgpack.packb(data_to_pack, use_bin_type=True)
    return keygenstr

def readkeygenfull(keygenstr=None,crsnew=None):
    if(keygenstr==None):
        raise SystemExit('Invalid Loading')
        return
    unpacked_data = msgpack.unpackb(keygenstr, raw=False)
    slots = unpacked_data[0]
    serialized_keys = unpacked_data[1]
    d = crsnew[2]
    deserialized_keys = [Key(None,None,None,None,None) for _ in range(d)]
    for i in range(d):
        deserialized_keys[i].deserialize(serialized_keys[i])

    ki = (slots,deserialized_keys)
    return ki

def lazykeygenfull(k1,crsnew):

    if(crsnew[1] == None or crsnew[2] == None):
        raise SystemExit('Invalid Parameters')

    Nnew = crsnew[1]
    d = crsnew[2]
    slots = [None]*d
    keys = [None]*d
    var = np.random.choice(Nnew,d,replace=False)
    # print(var)
    for i in range(d):
        slots[i] = int(var[i])
        # slots[i] = random.randrange(Nnew)
        # keys[i] = k1[1][i]
        # keys[i] = lazykeygen2(crsnew[0], slots[i]):
        keys[i] = Key(k1[1][i].N,k1[1][i].slot,k1[1][i].Ti,k1[1][i].Vj,k1[1][i].sk) 

    # print(Nnew,slots)
    ki = (slots,keys)
    return ki

def simkeygenfull(simgpelt,crsnew):

    if(crsnew[1] == None or crsnew[2] == None):
        raise SystemExit('Invalid Parameters')

    Nnew = crsnew[1]
    d = crsnew[2]
    slots = [None]*d
    keys = [None]*d
    var = np.random.choice(Nnew,d,replace=False)
    # sizesim = len(simgpelt)

    # print(var)

    for i in range(d):
        slots[i] = int(var[i])
        # slots[i] = random.randrange(Nnew)
        keys[i] = simkeygen(simgpelt,crsnew[0],slots[i])

    # for i in range(d):
    #     slots[i] = int(var[i])
    #     # slots[i] = random.randrange(Nnew)
    #     # keys[i] = k1[1][i]
    #     # keys[i] = lazykeygen2(crsnew[0], slots[i]):
    #     index = random.randint(0, d-1)
    #     keys[i] = Key(k1[1][i].N,k1[1][i].slot,k1[1][i].Ti,k1[1][i].Vj,k1[1][i].sk) 

    # print(Nnew,slots)
    ki = (slots,keys)
    return ki

def simkeygenfull2(simgpelt,crsnew):

    if(crsnew[1] == None or crsnew[2] == None):
        raise SystemExit('Invalid Parameters')

    Nnew = crsnew[1]
    d = crsnew[2]
    slots = [None]*d
    keys = [None]*d
    var = np.random.choice(Nnew,d,replace=False)
    for i in range(d):
        slots[i] = int(var[i])
        # slots[i] = random.randrange(Nnew)
        keys[i] = simkeygen2(simgpelt,crsnew[0],slots[i])

    # print(Nnew,slots)
    ki = (slots,keys)
    return ki

def encfull(crsnew, karraynew, m,reuse = False, s = None,precompute=None):

    # start = timeit.default_timer()
    karraynew = [i for i in karraynew if i is not None]
    d = crsnew[2]
    bsz = len(karraynew)
    # print(bsz,d)
    col1 = np.arange(bsz)
    col_ind = np.repeat(col1,d)
    # print(col_ind)
    # row_ind = np.ones(bsz*d,dtype=np.int32)
    # print(row_ind)

    # for i in range(bsz):
    #     for j in range(d):
    #         ind = j+d*i
    #         # print(karraynew[i][0][j])
    #         row_ind[ind] = int(karraynew[i][0][j])

    # print(row_ind)
    # row_ind = row_ind.astype(np.int8)


    row_ind = np.zeros(bsz*d,dtype=np.int32)
    # row_ind_list = []
    for i in range(bsz):
        row_ind[i*d : (i+1)*d] = karraynew[i][0]
        # row_ind_list.append(karraynew[i][0])

    # row_ind_list = [karraynew[i][0] for i in range(bsz)]
    # row_ind = np.concatenate(row_ind_list)

    # end = timeit.default_timer()
    # randstuff1 = (end-start)

    # if not(np.array_equal(row_ind, row_ind2)):
    #     print("Error happened in setting new params")

    # start = timeit.default_timer()
    data = np.ones(bsz*d)
    graph = csr_matrix((data, (row_ind, col_ind)), dtype=np.int32)
    # end = timeit.default_timer()
    # randstuff2 = (end-start)

    start = timeit.default_timer()
    matching = maximum_bipartite_matching(graph, perm_type='row')
    end = timeit.default_timer()
    gtime = (end-start)


    # start = timeit.default_timer()
    # if  any(map(lambda i : i == -1, matching)):
    if (np.any(matching == -1)):
        print("Error happened in finding a matching")

    # end = timeit.default_timer()
    # randstuff1 = (end-start)
    # print('Matching exists:', not any(map(lambda i : i == -1, matching)))
    # print('Matching takes time:', end - start)

    # karray = [None]*bsz

    # # print(graph)
    # # print(matching)
    # for i in range(bsz):
    #     ind = -1
    #     for j in range(d):
    #         if(matching[i]==karraynew[i][0][j]):
    #             ind = j
    #             print(i,j)
    #             break
    #     karray[i] = karraynew[i][1][ind]
        # print('slot is ',karray[i].slot)


    # matching_expanded = matching[:, np.newaxis]  # Broadcast matching for comparison
    # print(karraynew[np.arange(bsz),0,:])
    # indices = np.where(matching_expanded == karraynew[np.arange(bsz), 0, :])

    # start = timeit.default_timer()
    indices = np.where(matching[:, None] == row_ind.reshape(bsz, d))[1]
    # print(indices)
    karray = [None]*bsz
    for i in range(bsz):
        karray[i] = karraynew[i][1][indices[i]]
        # print('slot2 is ',karray2[i].slot)
    # karray2 = karraynew[np.arange(bsz), 1, indices[1]]  # Retrieve the corresponding values

    # if(karray!=karray2):
    #     raise SystemExit('Some Error in new matching code')

    # end = timeit.default_timer()
    # randstuff1 = (end-start)

    if(precompute==None):
        ct = enc(crsnew[0],karray,m,reuse,s)
    else:
        start = timeit.default_timer()
        precomputeelt = precomputeenc(crsnew[0], karray)
        end = timeit.default_timer()
        precompute[0] += end-start

        start = timeit.default_timer()
        ct = encprecompute(crsnew[0],karray,m,reuse,s,precomputeelt)
        end = timeit.default_timer()
        precompute[1] += end-start

        # print(precomputeelt)
        # for elt in precomputeelt:
        precompute[2] = len(precomputeelt[0].to_binary())

        precompute[2] += (4*bsz)

        precompute[3] += gtime
        # precompute[4] += randstuff1
        # precompute[5] += randstuff2


    return ct

# def encfull2(crsnew, karraynew, m,reuse = False, s = None,precompute=None):

#     karraynew = [i for i in karraynew if i is not None]
#     d = crsnew[2]
#     bsz = len(karraynew)
#     # print(bsz,d)
#     col1 = np.arange(bsz)
#     col_ind = np.repeat(col1,d)


#     row_ind = np.zeros(bsz*d,dtype=np.int32)
#     for i in range(bsz):
#         row_ind[i*d : (i+1)*d] = karraynew[i][0]

#     data = np.ones(bsz*d)
#     graph = csr_matrix((data, (row_ind, col_ind)), dtype=np.int32)

#     start = timeit.default_timer()
#     matching = maximum_bipartite_matching(graph, perm_type='row')
#     end = timeit.default_timer()
#     gtime = (end-start)

#     if (np.any(matching == -1)):
#         print("Error happened in finding a matching")

#     indices = np.where(matching[:, None] == row_ind.reshape(bsz, d))[1]

#     karray = [None]*bsz
#     for i in range(bsz):
#         karray[i] = karraynew[i][1][indices[i]]

#     if(precompute==None):
#         ct = enc(crsnew[0],karray,m,reuse,s)
#     else:
#         start = timeit.default_timer()
#         precomputeelt = precomputeenc(crsnew[0], karray)
#         end = timeit.default_timer()
#         precompute[0] += end-start

#         start = timeit.default_timer()
#         ct = encprecompute(crsnew[0],karray,m,reuse,s,precomputeelt)
#         end = timeit.default_timer()
#         precompute[1] += end-start

#         # print(precomputeelt)
#         # for elt in precomputeelt:
#         precompute[2] = len(precomputeelt[0].to_binary())

#         precompute[2] += (4*bsz)

#         precompute[3] += gtime
#         # precompute[4] += randstuff1
#         # precompute[5] += randstuff2


#     return ct

def enclazyfixfull(crsnew, karraynew, m,reuse = False, s = None,precompute=None):

    karraynew = [i for i in karraynew if i is not None]
    d = crsnew[2]
    bsz = len(karraynew)
    col1 = np.arange(bsz)
    col_ind = np.repeat(col1,d)

    row_ind = np.zeros(bsz*d,dtype=np.int32)
    # row_ind_list = []
    for i in range(bsz):
        row_ind[i*d : (i+1)*d] = karraynew[i][0]

    data = np.ones(bsz*d)
    graph = csr_matrix((data, (row_ind, col_ind)), dtype=np.int32)

    start = timeit.default_timer()
    matching = maximum_bipartite_matching(graph, perm_type='row')
    end = timeit.default_timer()
    gtime = (end-start)

    if (np.any(matching == -1)):
        print("Error happened in finding a matching")

    indices = np.where(matching[:, None] == row_ind.reshape(bsz, d))[1]

    karray = [None]*bsz
    for i in range(bsz):
        karray[i] = karraynew[i][1][indices[i]]

    ct = enclazyfix(crsnew[0],karray,m,reuse,s)
    return ct



def decfull(crsnew, karraynew, ksknew,ct,reuse = False, ct1=None,ct2=None,gtime=[0],lazysample=0,precompute=None):

    karraynew = [i for i in karraynew if i is not None]
    d = crsnew[2]
    bsz = len(karraynew)

    col1 = np.arange(bsz)
    col_ind = np.repeat(col1,d)

    # row_ind_list = [karraynew[i][0] for i in range(bsz)]
    # row_ind = np.concatenate(row_ind_list)


    row_ind = np.zeros(bsz*d,dtype=np.int32)
    for i in range(bsz):
        row_ind[i*d : (i+1)*d] = karraynew[i][0]

    data = np.ones(bsz*d)
    graph = csr_matrix((data, (row_ind, col_ind)), dtype=np.int32)

    start = timeit.default_timer()
    matching = maximum_bipartite_matching(graph, perm_type='row')
    end = timeit.default_timer() 

    if (np.any(matching == -1)):
        print("Error happened in finding a matching")

    gtime[0] = end-start
    karray = [None]*bsz

    indices = np.where(matching[:, None] == row_ind.reshape(bsz, d))[1]

    karray = [None]*bsz
    ksk=None
    for i in range(bsz):
        karray[i] = karraynew[i][1][indices[i]]
        if(ksknew[0] == karraynew[i][0]):
            ksk = ksknew[1][indices[i]]

    if (ksk==None):
        ksk = ksknew[1][0]

    if(precompute==None):
        mcomputed=dec(crsnew[0],karray,ksk,ct,reuse,ct1,ct2,lazysample)
    else:
        start = timeit.default_timer()
        precomputeelt = precomputedec(crsnew[0],karray,ksk,lazysample)
        end = timeit.default_timer()
        precompute[0] += end-start

        start = timeit.default_timer()
        mcomputed = decprecompute(crsnew[0],karray,ksk,ct,reuse,ct1,ct2,lazysample,precomputeelt)
        end = timeit.default_timer()
        precompute[1] += end-start

        precompute[2] = len(precomputeelt.to_binary())
        precompute[2] += (4*bsz)

        precompute[3] += gtime[0]

    return mcomputed

# def decfull2(crsnew, karraynew, ksknew,ct,reuse = False, ct1=None,ct2=None,gtime=[0],lazysample=0,precompute=None):

#     karraynew = [i for i in karraynew if i is not None]
#     d = crsnew[2]
#     bsz = len(karraynew)

#     col1 = np.arange(bsz)
#     col_ind = np.repeat(col1,d)
    

#     row_ind = np.zeros(bsz*d,dtype=np.int32)
#     for i in range(bsz):
#         row_ind[i*d : (i+1)*d] = karraynew[i][0]

#     data = np.ones(bsz*d)
#     graph = csr_matrix((data, (row_ind, col_ind)), dtype=np.int32)

#     start = timeit.default_timer()
#     matching = maximum_bipartite_matching(graph, perm_type='row')
#     end = timeit.default_timer() 

#     if (np.any(matching == -1)):
#         print("Error happened in finding a matching")

#     gtime[0] = end-start
#     karray = [None]*bsz

#     indices = np.where(matching[:, None] == row_ind.reshape(bsz, d))[1]

#     karray = [None]*bsz
#     ksk=None
#     for i in range(bsz):
#         karray[i] = karraynew[i][1][indices[i]]
#         if(ksknew[0] == karraynew[i][0]):
#             ksk = ksknew[1][indices[i]]

#     if (ksk==None):
#         ksk = ksknew[1][0]

#     if(precompute==None):
#         mcomputed=dec2(simgpelt,crsnew[0],karray,ksk,ct,reuse,ct1,ct2,lazysample)
#     else:
#         start = timeit.default_timer()
#         precomputeelt = precomputedec(crsnew[0],karray,ksk,lazysample)
#         end = timeit.default_timer()
#         precompute[0] += end-start

#         start = timeit.default_timer()
#         mcomputed = decprecompute(crsnew[0],karray,ksk,ct,reuse,ct1,ct2,lazysample,precomputeelt)
#         end = timeit.default_timer()
#         precompute[1] += end-start

#         precompute[2] = len(precomputeelt.to_binary())
#         precompute[2] += (4*bsz)

#         precompute[3] += gtime[0]

#     return mcomputed
