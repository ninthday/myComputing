#!/usr/bin/python
# -*- coding: utf-8 -*- #

from wfMySQL import MySQLConnector
from wfDatabase import wfdb
import codecs
import re
import enchant

# How many terms were you want to get
limit = 200

mysql = MySQLConnector()

# Instance Database List Class
obj_db = wfdb()

ptn1 = re.compile("^[\w\d]*$")
ptn2 = re.compile("^[\d]*$")
dic = enchant.Dict("en_US")


def verifyEngNum(term):
    if ptn1.match(term):
        if ptn2.match(term):
            return 1
        else:
            if dic.check(term):
                return 2
            else:
                return 3
    else:
        return 0


def generateGexf(list_terms, tb_name):
    len_term = len(list_terms)
    outfile = codecs.open('gexf/tfidf_' + tb_name + '.gexf', 'w', 'utf-8')
    outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    outfile.write('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n')
    outfile.write('<graph mode="static" defaultedgetype="undirected">\n')
    outfile.write('<nodes>\n')
    for i in range(len_term):
        outfile.write('<node id="%s" label="%s" />\n' % (str(i), list_terms[i]))
    outfile.write('</nodes>\n')
    x = 0
    outfile.write('<edges>\n')
    results = mysql.queryrows("SELECT * FROM `" + tb_name + "`")
    for row in results:
        list_seg_words = row[1].split("|")
        list_intersec = list(set(list_terms).intersection(set(list_seg_words)))
        list_intersec_index = []
        for term in list_intersec:
            list_intersec_index.append(list_terms.index(term))
            list_intersec_index.sort()

        len_intersec_index = len(list_intersec_index)
        print len_intersec_index
        for j in range(len_intersec_index - 1):
            for k in range(j + 1, len_intersec_index):
                outfile.write('<edge id="%s" source="%s" target="%s" />\n' % (str(x), str(list_intersec_index[j]), str(list_intersec_index[k])))
                x += 1
    outfile.write('</edges>\n')
    outfile.write('</graph></gexf>\n')
    outfile.close()

# Get TFIDF table list
tfidf_tblist = obj_db.getTFIDFTableList()

# Get Segmented table list
seg_tblist = obj_db.getTableList()
print seg_tblist
for i in range(5):
    dict_tfidf = {}
    results = mysql.queryrows("SELECT * FROM `" + tfidf_tblist[i] + "`")
    for row in results:
        list_pairs = row[1].split("|")
        for pair in list_pairs:
            term_tfidf = pair.split("@")
            term = term_tfidf[0]
            tfidf = float(term_tfidf[1])
            if term in dict_tfidf:
                continue
            else:
                dict_tfidf[term] = tfidf

    # Remove number and not english word in dictionary
    for key, val in dict_tfidf.items():
        if verifyEngNum(key) == 1 or verifyEngNum(key) == 3:
            dict_tfidf.pop(key)

    # Sort tfidf dictionary by tfidf score
    dict_sorted_tfidf = sorted(dict_tfidf.items(), key=lambda(k, v): (v, k), reverse=True)

    # Get limit term list from sorted tfidf dictionary
    list_terms = []
    j = 1
    for key, val in dict_sorted_tfidf:
        if j > limit:
            break
        else:
            list_terms.append(key)
        j += 1
    #print list_terms

    generateGexf(list_terms, seg_tblist[i])
