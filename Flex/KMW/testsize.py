#!/usr/bin/env python3
from classes import *
from schemeKMW import *
# import inspect module
import inspect
from petrelic.multiplicative.pairing import G1,G2,GT,G1Element,G2Element


a = G1.order().random()
b= G2.order().random()

ga = G1.generator() ** a
gb = G2.generator() ** b

gt = ga.pair(gb)

# using pairing BLS381 curve
print("Size of group G1 is " + str(len(ga.to_binary())) + " bytes")
print("Size of group G2 is " + str(len(gb.to_binary())) + " bytes")
print("Size of group GT is " + str(len(gt.to_binary())) + " bytes")
