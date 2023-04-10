#!/usr/bin/env python3

from math import ceil,floor, log2,sqrt
from operator import mod

from classes import *
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element
from petrelic.bn import Bn
import sqlite3
from os.path import exists
import timeit
import numpy as np
import random

#for these experiments, assume there is no binning, M=N, binning is done in the outer layer

def setup(N,M = None,filename=None,rorw=None):
    """
    N : maximum number of users in a broadcast slot
    """
    if (M == None):
        M = N
    crs = CRS(N,M)
    # crs.save_to_file(filename,rorw)
    return crs


def keygen(crs, slot):
    """
    crs : pp's for the scheme
    slot   : slot number where slot <= N

    M : number of broadcasts bucketed for one ciphertext
    Mct : maximum number of cts
    """
    if slot >= crs.N:
        raise SystemExit('Setting invalid slot')
    N = crs.N
    M = crs.M

    Mct = ceil(N/M)
    sk = G1.order().random()
    Ti = crs.g1 ** sk

    # # binning code
    # Vj = [None] * (M)
    # # integer division
    # index = slot // M
    # start = index*M
    # end = (index+1)*M
    # for i in range(start,end):
    #     indarr = i-start
    #     indslot = slot - start

    #     if (indarr == M-1-slot):
    #         continue
    #     elif (indarr >= M):
    #         break
    #     indarr = i - start
    #     Vj[indarr] = crs.Ag1[indarr] ** sk

    # assume no binning
    Vj = [None] * (N)
    for i in range(0,N):
        if (i == N-1-slot):
            continue
        elif (i >= N):
            break
        Vj[i] = crs.Ag1[i] ** sk

    ki = Key(N,slot,Ti,Vj,sk)
    return ki

def lazykeygen(k1,crs, slot):
    if(slot == k1.slot):
        raise SystemExit('Invalid slot copying')
        return k1
    N = k1.N
    # assume no binning
    Vj = [None]*(N)
    for i in range(0,N):
        Vj[i] = k1.Vj[i]

    Vj[N-1-k1.slot] = k1.Vj[N-1-slot]
    Vj[N-1-slot] = None

    ki = Key(N,slot,k1.Ti,Vj,k1.sk)
    return ki


def simkeygen(simgpelt, crs, slot):
    """
    crs : pp's for the scheme
    slot   : slot number where slot <= N

    M : number of broadcasts bucketed for one ciphertext
    Mct : maximum number of cts
    """
    if slot >= crs.N:
        raise SystemExit('Setting invalid slot')
    N = crs.N
    M = crs.M

    Mct = ceil(N/M)
    simsz = len(simgpelt)

    sk = G1.order().random()
    Ti = crs.g1 ** sk
    # index = random.randint(0, simsz-1)
    # Ti = simgpelt[index]

    randomindexarr = np.random.choice(simsz,N)
    # print(simsz,N)
    # print(randomindexarr)

    # assume no binning
    Vj = [None] * (N)
    for i in range(0,N):
        if (i == N-1-slot):
            continue
        elif (i >= N):
            break
        Vj[i] = simgpelt[randomindexarr[i]]

    ki = Key(N,slot,Ti,Vj,sk)
    return ki

def simkeygen2(simgpelt, crs, slot):
    if slot >= crs.N:
        raise SystemExit('Setting invalid slot')
    N = crs.N
    M = crs.M

    Mct = ceil(N/M)
    simsz = len(simgpelt)

    sk = G1.order().random()
    Ti = crs.g1 ** sk

    # ki = Key(N,slot,Ti,None,sk)

    # index = random.randint(0, simsz-N-10)
    # Vj = [None] * (N)
    ki = Key(N,slot,Ti,simgpelt,sk)
    # print(len(simgpelt[index:index+N]))
    return ki

# def lazykeygen2(crs, slot):
#     N = crs.N
#     Vj = [None]*(N)
#     # for i in range(0,N):
#     #     Vj[i] = G1.hash_to_point()

#     Vj[N-1-k1.slot] = k1.Vj[N-1-slot]
#     Vj[N-1-slot] = None

#     ki = Key(N,slot,k1.Ti,Vj,k1.sk)
#     return ki

def enc(crs, karray, m,reuse=False,s=None):
    """
    Parameters
    ----------
    crs : common reference string
    karray : array of pks
    m : element of GT


    M : number of broadcasts bucketed for one ciphertext
    Mct : maximum number of cts

    Returns
    -------
    ct : Ciphertext
    """
    N = crs.N
    M = crs.M
    Mct = ceil(N/M)
    # print('Mct is ',Mct)
    ct = [None] * (Mct)
    intmul = [None]*(Mct)

    for i in range(Mct):
        intmul[i] = G1.neutral_element()

    # # binning code
    # for ind in range(len(karray)):
    #     if(karray[ind]==None):
    #         continue
    #     indslot = karray[ind].slot
    #     indct = indslot//M

    #     indstart = indct*M
    #     indend = (indct+1)*M

    #     indpos = indslot-indstart

    #     # print('indct is ',indct,'inslot is ',indslot)
    #     intmul[indct] *= (crs.Ag1[indpos] * karray[ind].Ti)
    #     # print(intmul[indct])

    # assume no binning

    # start = timeit.default_timer()
    for ind in range(len(karray)):
        if(karray[ind]==None):
            continue
        indslot = karray[ind].slot
        indct = indslot//M
        # print(karray[ind].Ti)
        # print(karray[ind])
        intmul[indct] *= (crs.Ag1[indslot] * karray[ind].Ti)

    # end = timeit.default_timer()
    # cryptotime = (end-start)
    # print("Encrypt time is ",cryptotime)
    for i in range(Mct):
        if (reuse):
            ct1 = None
            ct2 = None
        else:
            s = G2.order().random()
            Zs = crs.Z ** s
            # print(s)
            ct1 = Zs * m;
            ct2 = crs.g2 ** s
        # print('i is ',i,'intmul is ',intmul[i])
        ct3 = intmul[i] ** (-s)
        ct[i] = Ciphertext(ct1,ct2,ct3)
    return ct

def enclazyfix(crs, karray, m,reuse=False,s=None):
    """
    Parameters
    ----------
    crs : common reference string
    karray : array of pks
    m : element of GT


    M : number of broadcasts bucketed for one ciphertext
    Mct : maximum number of cts

    Returns
    -------
    ct : Ciphertext
    """
    N = crs.N
    M = crs.M
    Mct = ceil(N/M)
    # print('Mct is ',Mct)
    ct = [None] * (Mct)
    intmul = [None]*(Mct)

    for i in range(Mct):
        intmul[i] = G1.neutral_element()

    for ind in range(len(karray)):
        if(karray[ind]==None):
            continue
        indslot = karray[ind].slot
        indct = indslot//M

        sk = G1.order().random()
        Ti = crs.g1 ** sk
        karray[ind].Ti = Ti
    return ct



def precomputeenc(crs, karray):
    N = crs.N
    M = crs.M
    if(N != M):
        raise SystemExit('This case should not happen')

    Mct = ceil(N/M)
    intmul = [None]*(Mct)

    for i in range(Mct):
        intmul[i] = G1.neutral_element()

    for ind in range(len(karray)):
        if(karray[ind]==None):
            continue
        indslot = karray[ind].slot
        indct = indslot//M
        intmul[indct] *= (crs.Ag1[indslot] * karray[ind].Ti)
    return intmul

def encprecompute(crs, karray, m,reuse=False,s=None,elt=None):
    if(elt == None):
        raise SystemExit('Error with precomputing elements')
    N = crs.N
    M = crs.M
    Mct = ceil(N/M)
    # print('Mct is ',Mct)
    ct = [None] * (Mct)
    intmul = [None]*(Mct)

    if(N != M):
        raise SystemExit('This case should not happen')

    for i in range(Mct):
        intmul[i] = elt[i]

    for i in range(Mct):
        if (reuse):
            ct1 = None
            ct2 = None
        else:
            s = G2.order().random()
            Zs = crs.Z ** s
            # print(s)
            ct1 = Zs * m;
            ct2 = crs.g2 ** s
        # print('i is ',i,'intmul is ',intmul[i])
        ct3 = intmul[i] ** (-s)
        ct[i] = Ciphertext(ct1,ct2,ct3)
    return ct

def precomputedec(crs, karray, ksk, lazysample=0):
    N = crs.N
    M = crs.M
    Mct = ceil(N/M)

    indct = ksk.slot//M
    if(N != M):
        raise SystemExit('This case should not happen')

    elt = G1.neutral_element()

    for i in range(len(karray)):
        if(karray[i]==None):
            continue
        currslot = karray[i].slot
        currslotct = currslot//M

        start = indct*M
        kindarr = ksk.slot - start

        if(currslotct != indct):
            continue

        if (currslot == ksk.slot and lazysample == 0):
            continue
        elif(currslot == ksk.slot and lazysample == 1):
            #code to calculate decrypt operation even if we lazily sample incorrect pks
            lazyfix = N-2-ksk.slot
            if(lazyfix<0): 
                lazyfix = 1
            elt *= (crs.Ag1[N-1]*karray[i].Vj[lazyfix])
            continue
        if(crs.Ag1[N+currslot-ksk.slot]==None):
            print("Debug 1: ",currslot," ",ksk.slot)

        if(karray[i].Vj[N-1-ksk.slot]==None):
            print("Debug 2: ",currslot," ",ksk.slot)
        elt *= (crs.Ag1[N+currslot-ksk.slot]*karray[i].Vj[N-1-ksk.slot])

    indslot = ksk.slot
    elt *= (crs.Ag1[N-1-indslot] ** ksk.sk)
    return elt

def dec(crs, karray, ksk,ct,reuse=False,ct1=None,ct2=None,lazysample=0):
    """
    Parameters
    ----------
    crs : common reference string
    karray : array of pks
    kak : secret key for some slot
    ct : Ciphertext

    Returns
    -------
    m : element of GT
    """

    # print('debug information: ',ksk.slot)
    # for i in range(len(karray)):
    #     print('slot of pk array is ', karray[i].slot)

    N = crs.N
    M = crs.M
    Mct = ceil(N/M)

    indct = ksk.slot//M
    if(reuse):
        val1 = ct1
        val2 = ct2
    else:
        val1 = ct[indct].ct1
        val2 = ct[indct].ct2

    intval = G1.neutral_element()

    # cnt = 0
    for i in range(len(karray)):
        if(karray[i]==None):
            continue

        currslot = karray[i].slot
        currslotct = currslot//M

        start = indct*M
        kindarr = ksk.slot - start

        if(currslotct != indct):
            continue

        if (currslot == ksk.slot and lazysample == 0):
            continue
        elif(currslot == ksk.slot and lazysample == 1):
            #code to calculate decrypt operation even if we lazily sample incorrect pks
            lazyfix = N-2-ksk.slot
            if(lazyfix<0): 
                lazyfix = 1
            intval *= (crs.Ag1[N-1]*karray[i].Vj[lazyfix])
            continue

        # # binning code
        # intval *= (crs.Ag1[M+currslot-ksk.slot]*karray[i].Vj[M-1-kindarr])

        if(crs.Ag1[N+currslot-ksk.slot]==None):
            print("Debug 1: ",currslot," ",ksk.slot)

        if(karray[i].Vj[N-1-ksk.slot]==None):
            print("Debug 2: ",currslot," ",ksk.slot)

        # assume no binning
        intval *= (crs.Ag1[N+currslot-ksk.slot]*karray[i].Vj[N-1-ksk.slot])


    indslot = ksk.slot

    # # binning code
    # indstart = indct*M
    # indend = (indct+1)*M
    # indpos = indslot-indstart
    # intval *= (crs.Ag1[M-1-indpos] ** ksk.sk)
    # val3 = ct[indct].ct3.pair(crs.Ag2[M-1-indpos])
    # # print("N ",N,"M ",M)

    # assume no binning
    intval *= (crs.Ag1[N-1-indslot] ** ksk.sk)
    val3 = ct[indct].ct3.pair(crs.Ag2[N-1-ksk.slot])
    res = val1*val3*(intval.pair(val2))
    return res


def decprecompute(crs, karray, ksk,ct,reuse=False,ct1=None,ct2=None,lazysample=0,elt=None):
    if(elt == None):
        raise SystemExit('Error with precomputing elements')
    N = crs.N
    M = crs.M
    Mct = ceil(N/M)

    indct = ksk.slot//M
    if(reuse):
        val1 = ct1
        val2 = ct2
    else:
        val1 = ct[indct].ct1
        val2 = ct[indct].ct2

    intval = G1.neutral_element()
    intval *= elt
    indslot = ksk.slot
    val3 = ct[indct].ct3.pair(crs.Ag2[N-1-ksk.slot])
    res = val1*val3*(intval.pair(val2))
    return res

