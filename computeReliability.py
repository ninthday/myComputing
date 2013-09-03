#!/usr/bin/python
# -*- coding: utf-8 -*- #

from wfMySQL import MySQLConnector

# Instance Database connector class
mysql = MySQLConnector()


def pairReliablility(user1, user2, coder_clsfi):
    len_n = len(coder_clsfi)
    M = 0
    for key, value in coder_clsfi.items():
        if value[user1] == value[user2]:
            M += 1
    rebilty = (2.0 * M) / (2.0 * len_n)
    print "User: " + str(user1) + ", " + str(user2)
    print "M (Number of totally agreement): " + str(M)
    print "N1,N2 (Should agree with number): " + str(len_n)
    print "Mutual consent degree = 2M/(N1+N2): " + str(rebilty) + "\n\n"

sql_get = "SELECT `SamplingNo`, `ClsNo1`, `UserId` FROM `CoderCompare` ORDER BY `CoderCompare`.`SamplingNo` ASC"

result = mysql.queryrows(sql_get)

coder_clsfi = {}

for row in result:
    sno = int(row[0])
    cls = int(row[1])
    user = int(row[2])
    if sno in coder_clsfi:
        coder_clsfi[sno][user] = cls
    else:
        coder_clsfi[sno] = {}
        coder_clsfi[sno][user] = cls

print coder_clsfi

pairReliablility(2, 3, coder_clsfi)
pairReliablility(2, 4, coder_clsfi)
pairReliablility(3, 4, coder_clsfi)

pairReliablility(2, 3, coder_clsfi)
pairReliablility(2, 5, coder_clsfi)
pairReliablility(3, 5, coder_clsfi)
