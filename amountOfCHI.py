#!/usr/bin/python
# -*- coding:utf-8 -*- #

from filter import dimension

# Set amount for get average CHI score
amtNum = 7002

# Instance dimension Class
obj_dims = dimension()

# Get Average CHI Score Dictionary
dict_avg_chi = obj_dims.getAvgCHIList()

# Get Max CHI Score Dictionary
dict_max_chi = obj_dims.getMaxCHIList()
"""
i = 1
for key, value in sorted(dict_avg_chi.items(), key=lambda(k, v): (v, k), reverse=True):
    print "%s: %s" % (key, value)
    i += 1
    if i > 100:
        break
"""
# Sort Avg CHI Score dictionary by value
sorted_avg_chi = sorted(dict_avg_chi.items(), key=lambda(k, v): (v, k), reverse=True)

i = 1
for key, value in sorted_avg_chi:
    if i == amtNum:
        print "Avg CHI Score at %d: %s, %s" % (amtNum, key, value)
        break
    i += 1

# Sort Max CHI Score dictionary by value
sorted_max_chi = sorted(dict_max_chi.items(), key=lambda(k, v): (v, k), reverse=True)

i = 1
for key, value in sorted_max_chi:
    if i == amtNum:
        print "Max CHI Score at %d: %s: %s" % (amtNum, key, value)
        break
    i += 1
