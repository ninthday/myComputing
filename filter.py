#!/usr/bin/python
# -*- coding: utf-8 -*- #

"""filterDimension.py: This file is to filter dimension by CHI value"""

import codecs


class dimension():

    def __init__(self):
        self.message = "Initilization!"
        self.buildAvgCHIList()
        self.buildMaxCHIList()

    def buildAvgCHIList(self):
        rtn_list = {}
        inputfile = codecs.open("average_chi_list.txt", "r", "utf-8")
        for line in inputfile.readlines():
            inline = line.rstrip("\n").split(":")
            rtn_list[inline[0]] = float(inline[1])
        inputfile.close()
        self.avg_chi_list = rtn_list

    def buildMaxCHIList(self):
        rtn_list = {}
        inputfile = codecs.open("max_chi_list.txt", "r", "utf-8")
        for line in inputfile.readlines():
            inline = line.rstrip("\n").split(":")
            rtn_list[inline[0]] = float(inline[1])
        inputfile.close()
        self.max_chi_list = rtn_list

    def doFilteredList(self, f_vaule, in_list):
        for k, v in in_list.items():
            if v < f_vaule:
                in_list.pop(k)
        return in_list

    def getAvgCHIList(self):
        return self.avg_chi_list

    def getMaxCHIList(self):
        return self.max_chi_list

"""
avg_chi_list = getAvgCHIList()
print "Avg CHI list length is %d" % len(avg_chi_list)

w_avg_list = getFilteredList(0.028, avg_chi_list)
print "New Avg CHI list length is %d" % len(new_avg_list)

max_chi_list = getMaxCHIList()
print "Max CHI list length is %d" % len(max_chi_list)
new_max_list = getFilteredList(0.15, max_chi_list)
print "New Max CHI list length is %d" % len(new_max_list)

i = 1
for k, v in new_list.items():
    if i < 100:
        print k, v
    else:
        break
    i += 1
"""
