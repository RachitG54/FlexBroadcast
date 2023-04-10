#!/usr/bin/env python3

from math import ceil,floor, log2,sqrt
from operator import mod

from classes import *
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element
from petrelic.bn import Bn
import sqlite3
from os.path import exists

def setup(N,filename=None,rorw=None):
    """
    N : maximum number of users in a broadcast slot
    """
    crs = CRS(N)
    # crs.save_to_file(filename,rorw)
    return crs


def keygen(crs, slot):
    """
    crs : pp's for the scheme
    i   : slot number where i <= N
    """
    if slot >= crs.N:
        raise SystemExit('Setting invalid slot')
    N = crs.N

    sk = G1.order().random()
    Ti = crs.g1 ** sk
    Vj = [None] * (N)
    for i in range(N):
        if (i == slot):
            continue
        Vj[i] = crs.Ag1[i] ** sk

    ki = Key(N,slot,Ti,Vj,sk)
    return ki

def enc(crs, karray, m):
    """
    Parameters
    ----------
    crs : common reference string
    karray : array of pks
    m : element of GT

    Returns
    -------
    ct : Ciphertext
    """


    s = G2.order().random()

    Zs = crs.Z ** s
    ct1 = Zs * m;
    ct2 = crs.g2 ** s
    intmul = G1.neutral_element()
    for i in range(len(karray)):
        if(karray[i]==None):
            continue;
        currslot = karray[i].slot
        intmul *= (crs.Ag1[crs.N-1-currslot] * karray[i].Ti)


    ct3 = intmul ** (-s)
    ct = Ciphertext(ct1,ct2,ct3)
    return ct

def dec(crs, karray, ksk,ct):
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

    val1 = ct.ct1
    val2 = ct.ct3.pair(crs.Ag2[ksk.slot])
    intval = G1.neutral_element()
    for i in range(len(karray)):
        if(karray[i]==None):
            continue;
        currslot = karray[i].slot
        if (currslot == ksk.slot):
            continue
        intval *= (crs.Ag1[crs.N-currslot+ksk.slot]*karray[i].Vj[ksk.slot])

    val3 = crs.Ag1[ksk.slot] ** ksk.sk
    intval *= val3

    res = val1*val2*(intval.pair(ct.ct2))
    return res

