#!/usr/bin/python
# -*- coding: utf-8 -*- #

from wfMySQL import MySQLConnector
from filter import dimension
from wfDatabase import wfdb
import codecs

mysql = MySQLConnector()


def generateGexf(list_terms, db_name):
    len_term = len(list_terms)
    outfile = codecs.open('gexf/max_' + db_name + '.gexf', 'w', 'utf-8')
    outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    outfile.write('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n')
    outfile.write('<graph mode="static" defaultedgetype="undirected">\n')
    outfile.write('<nodes>\n')
    for i in range(len_term):
        outfile.write('<node id="%s" label="%s" />\n' % (str(i), list_terms[i]))
    outfile.write('</nodes>\n')
    x = 0
    outfile.write('<edges>\n')
    results = mysql.queryrows("SELECT * FROM `" + db_name + "`")
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


# How many terms were you want to get
limit = 200

# Instance dimension Class
obj_dims = dimension()

# Instance Database List Class
obj_db = wfdb()

# Get Average CHI Score Dictionary
#dict_avg_chi = obj_dims.getAvgCHIList()

# Get Max CHI Score Dictionary
dict_max_chi = obj_dims.getMaxCHIList()

# Sort Avg CHI SCore dictionary by value
#sorted_avg_chi = sorted(dict_avg_chi.items(), key=lambda(k, v): (v, k), reverse=True)

# Sort Max CHI SCore dictionary by value
sorted_max_chi = sorted(dict_max_chi.items(), key=lambda(k, v): (v, k), reverse=True)

list_terms = []
i = 1
for key, val in sorted_max_chi:
    if i > limit:
        break
    else:
        list_terms.append(key)
    i += 1


# Get Segment database name list
segdb_namelist = obj_db.getTableList()


for db_name in segdb_namelist:
    generateGexf(list_terms, db_name)

# Close connection
mysql.disconnect()
