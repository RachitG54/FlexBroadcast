#!/usr/bin/env python3

from math import ceil,floor, log2,sqrt
from operator import mod

from classes import *
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element
from petrelic.bn import Bn
import sqlite3
from os.path import exists

#for these experiments, assume there is no binning, M=N, binning is done in the outer layer

def setup(N,M = None):
    """
    N : maximum number of users in a broadcast slot
    """
    if (M == None):
        M = N

    g1 = G1.generator()
    g2 = G2.generator()
    z = G1.order().random()
    Ag1 = [None] * (2*N)
    for i in range(2*N):
        if i == (N):
            continue
        Ag1[i] = g1 ** (z.mod_pow(i+1,G1.order()))

    Ag2 = [None] * (N)
    for i in range(N):
        Ag2[i] = g2 ** (z.mod_pow(i+1,G2.order()))

    val = g1 ** (z.mod_pow(N+1,G1.order()))
    Z = val.pair(g2)
    vexp = G1.order().random()
    v = g1 ** vexp

    mpk = MPK(N,M,g1,g2,Ag1,Ag2,Z,v)
    msk = MSK(z)
    return (mpk,msk)


def keygen(mpk, msk, slot):
    """
    msk : msk for the scheme
    slot   : slot number where slot <= N

    M : number of broadcasts bucketed for one ciphertext
    Mct : maximum number of cts
    """
    if slot >= mpk.N:
        raise SystemExit('Setting invalid slot')
    v = mpk.v
    di = v ** (msk.z.mod_pow(slot+1,G1.order()))
    sk = SK(slot,di)
    return sk


def lazykeygen(k1,mpk,msk, slot):
    return k1

def enc(mpk, setS, m):
    N = mpk.N
    s = G2.order().random()
    Zs = mpk.Z ** s
    ct1 = Zs * m;
    ct2 = mpk.g2 ** s

    intmul = G1.neutral_element()
    for i in range(len(setS)):
        ind = setS[i]
        intmul *= mpk.Ag1[N-1-ind]
    intmul *= mpk.v

    ct3 = intmul ** (-s)

    ct = Ciphertext(ct1,ct2,ct3)
    return ct

def dec(mpk, setS, sk,ct):

    N = mpk.N

    intval = G1.neutral_element()
    for i in range(len(setS)):
        ind = setS[i]
        if (ind == sk.slot):
            continue
        intval *= mpk.Ag1[N+sk.slot-ind]
    intval *= sk.di
    val2 = intval.pair(ct.ct2)
    val3 = ct.ct3.pair(mpk.Ag2[sk.slot])
    res = ct.ct1*val2*val3
    return res

