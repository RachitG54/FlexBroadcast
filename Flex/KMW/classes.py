#!/usr/bin/env python3

from math import ceil,sqrt,log2
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element,GTElement
from petrelic.bn import Bn
import sqlite3
from os.path import exists
import msgpack


"""
Our scheme has different choices of parameter settings, I'm going to choose one for now and we will run more tests if the other version is preferred.
CRS has elements in G1, G2 both (g^a^1, ... g^a^{2N}, but not g^{a^{N+1}}), Z, g

These should be in opposite sides, ct2 and V,A's, ct3 (which is A's and T_i) and A_{i*}

Let's optimize keygen size which means V's. T_i is in G1, V_{j,i} is in G1.
Then ct2 is in G2, ct3 is in G1.

N is max broadcast set size
"""
class Ciphertext:
    """
    Parameters
    ----------
    ct1 : element of GT, message blinded by Z^s
    ct2 : element of G2, randomization factor g^s
    ct3 : elements of G1, multiplication of broadcast pk's
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

class CRS:
    """
    Parameters
    ----------
    N : max broadcast set size
    M : number of broadcasts bucketed for one ciphertext
    g1 : generator of G1
    g2 : generator of G2
    Z : e(g1,g2)^{a^{N+1}}
    Ag1 : array of elements of G1 of size 2N
    Ag2 : array of elements of G2 of size N
    """
    def __init__(self,N=None,M=None,g1=None,g2=None,z=None):
        if N is None:
            return
        else:
            self.N = N
            self.M = M
            self.g1 = G1.generator() if g1 is None else g1
            self.g2 = G2.generator() if g2 is None else g2
            z = G1.order().random() if z is None else z
            self.Ag1 = [None] * (2*self.N)
            for i in range(2*self.N):
                if i == (self.N):
                    continue
                self.Ag1[i] = self.g1 ** (z.mod_pow(i+1,G1.order()))


            self.Ag2 = [None] * (self.N)
            for i in range(self.N):
                self.Ag2[i] = self.g2 ** (z.mod_pow(i+1,G2.order()))

            val = self.g1 ** (z.mod_pow(N+1,G1.order()))
            self.Z = val.pair(self.g2)

    def get_size(self):
        """Calculate the size (in bytes) of the crs."""
        sz = 0
        sz += 4 #for N
        sz += 4 #for M
        sz += len(self.g1.to_binary())
        sz += len(self.g2.to_binary())
        sz += len(self.Z.to_binary())
        for i in range(2*self.N):
            if (i == self.N):
                sz += 0
                continue
            sz += len(self.Ag1[i].to_binary())

        for i in range(self.N):
            sz += len(self.Ag2[i].to_binary())
        return sz

    def serialize(self):
        data = {
            'N': self.N,
            'M': self.M,
            'g1': self.g1.to_binary(),
            'g2': self.g2.to_binary(),
            'Ag1': [ag1.to_binary() if ag1 is not None else None for ag1 in self.Ag1],
            'Ag2': [ag2.to_binary() if ag2 is not None else None for ag2 in self.Ag2],
            'Z': self.Z.to_binary()
        }
        return msgpack.packb(data, use_bin_type=True)

    def deserialize(self, serialized_data):
        unpacked_data = msgpack.unpackb(serialized_data, raw=False)
        self.N = unpacked_data['N']
        self.M = unpacked_data['M']
        self.g1 = G1Element.from_binary(unpacked_data['g1'])
        self.g2 = G2Element.from_binary(unpacked_data['g2'])
        self.Ag1 = [G1Element.from_binary(ag1) if ag1 is not None else None for ag1 in unpacked_data['Ag1']]
        self.Ag2 = [G2Element.from_binary(ag2) if ag2 is not None else None for ag2 in unpacked_data['Ag2']]
        self.Z = GTElement.from_binary(unpacked_data['Z'])  # Assuming 'Z' is a GT element

class Key:
    """
    Parameters
    ----------
    N : max broadcast set size
    slot : slot i
    Ti : element of G1, g^{r_i}
    Vj : array of N many things in G1, A_j^{r_i}, 
    sk : r_i
    """
    def __init__(self,N,slot,Ti,Vj,sk=None):
        """Constructor"""
        if (N==None):
            return
        if slot >= N:
            raise SystemExit('Setting invalid slot')
        self.N = N
        self.slot = slot
        self.Ti = Ti
        self.Vj = Vj
        self.sk = sk

    def get_pksize(self):
        """Calculate the size (in bytes) of the keygen."""
        sz = 0
        sz += 4 # for N
        sz += 4 # for slot
        if (self.Ti != None):
            sz += len(self.Ti.to_binary())
        for v in self.Vj:
            if (v == None):
                sz += 0 
                continue
            sz += len(v.to_binary())
        return sz

    def get_sksize(self):
        """Calculate the size (in bytes) of the keygen."""
        sz = 0
        sz += ceil(self.sk.num_bits()/8)
        return sz

    def serialize(self):
        data = {
            'N': self.N,
            'slot': self.slot,
            'Ti': self.Ti.to_binary(),
            'Vj': [vj.to_binary() if vj is not None else None for vj in self.Vj],
            'sk': Bn.binary(self.sk)
        }
        return msgpack.packb(data, use_bin_type=True)

    def deserialize(self, serialized_data):
        unpacked_data = msgpack.unpackb(serialized_data, raw=False)
        self.N = unpacked_data['N']
        self.slot = unpacked_data['slot']
        self.Ti = G1Element.from_binary(unpacked_data['Ti'])
        self.Vj = [G1Element.from_binary(vj) if vj is not None else None for vj in unpacked_data['Vj']]
        self.sk = Bn.from_binary(unpacked_data['sk'])

class SimKey:
    """
    Parameters
    ----------
    N : max broadcast set size
    slot : slot i
    Ti : element of G1, g^{r_i}
    Vj : array of N many things in G1, A_j^{r_i}, 
    sk : r_i
    """
    def __init__(self,N,slot,Ti,Vjind,sk=None):
        """Constructor"""
        if (N==None):
            return
        if slot >= N:
            raise SystemExit('Setting invalid slot')
        self.N = N
        self.slot = slot
        self.Ti = Ti
        self.Vj = Vjind
        self.sk = sk