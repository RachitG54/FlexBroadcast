#!/usr/bin/env python3

from math import ceil,sqrt,log2
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element
from petrelic.bn import Bn
import sqlite3
from os.path import exists


"""
Centralized Broadcast, not implemented bucketing because not needed for our experiments
"""
class MPK:
    """
    Parameters
    ----------
    N : max broadcast set size
    M : number of broadcasts bucketed for one ciphertext
    g1 : generator of G1
    g2 : generator of G2
    Z : e(g1,g2)^{a^{N+1}}
    Ag1 : array of elements of G1 of size 2N
    Ag2 : array of elements of G2 of size 2N
    v   : element of G1
    """
    def __init__(self,N=None,M=None,g1=None,g2=None,Ag1=None,Ag2=None,Z=None,v=None):
        if v is None:
            raise SystemExit('Invalid parameter setting')
        else:
            self.N = N
            self.M = M
            self.g1 = g1
            self.g2 = g2
            self.Ag1 = Ag1
            self.Ag2 = Ag2
            self.Z = Z
            self.v = v

    def get_size(self):
        """Calculate the size (in bytes) of the crs."""
        sz = 0
        sz += 4 #for N
        sz += 4 #for M
        sz += len(self.g1.to_binary())
        sz += len(self.g2.to_binary())
        for i in range(2*self.N):
            if (i == self.N):
                sz += 0
                continue
            sz += len(self.Ag1[i].to_binary())

        for i in range(self.N):
            sz += len(self.Ag2[i].to_binary())
        sz += len(self.Z.to_binary())
        sz += len(self.v.to_binary())
        return sz

class MSK:
    """
    Parameters
    ----------
    z : element of order of the group
    """
    def __init__(self,z=None):
        if z is None:
            raise SystemExit('Invalid parameter setting')
        else:
            self.z = z

    def get_size(self):
        """Calculate the size (in bytes) of the crs."""
        sz = 0
        sz += ceil(self.z.num_bits()/8)
        return sz

class SK:
    """
    Parameters
    ----------
    slot : slot i
    di : element of G1
    """
    def __init__(self,slot=None,di=None):
        if di is None:
            raise SystemExit('Invalid parameter setting')
        else:
            self.slot = slot
            self.di = di

    def get_size(self):
        """Calculate the size (in bytes) of the crs."""
        sz = 0
        sz += 4
        sz += len(self.di.to_binary())
        return sz

class Ciphertext:
    """
    Parameters
    ----------
    ct1 : element of GT, message blinded by Z^s
    ct2 : element of G2, randomization factor g^s
    ct3 : elements of G1, multiplication of pk's
    """
    def __init__(self,ct1,ct2,ct3):
        """Constructor"""
        self.ct1 = ct1
        self.ct2 = ct2
        self.ct3 = ct3

    def get_size(self):
        """Calculate the size (in bytes) of the ciphertext."""
        ct_size = 0
        if (self.ct1 != None):
            ct_size = ct_size + len(self.ct1.to_binary())
        if (self.ct2 != None):
            ct_size = ct_size + len(self.ct2.to_binary())
        if (self.ct3 != None):
            ct_size = ct_size + len(self.ct3.to_binary())
        return ct_size