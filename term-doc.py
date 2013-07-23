#!/usr/bin/python
# -*- coding: utf-8 -*- #

import MySQLdb
import codecs
import sys
# Create a connection
conn = MySQLdb.connect(host="localhost",
                       user="wfproject",
                       passwd="1q2w3e4r",
                       db="WFProject",
                       charset="utf8")
# Database Name list
dblist = ('SegXditeNSW', 'SegPingtungNSW', 'SegTainanNSW', 'SegRicksNSW', 'SegXditeCombineNSW', 'SegAdctNSW')

# Get System argument
dbnum = int(sys.argv[1])

# Set database name
dbname = dblist[dbnum]

# create output file
outfile = codecs.open('term_doclist_nsw' + dbname + '.txt', 'w', 'utf-8')

# SQL statement
sql_test = 'SELECT * FROM `' + dbname + '`'

# Get Connection cursor
cursor = conn.cursor()

# Execute the SQL statement
cursor.execute(sql_test)

# Get one result
results = cursor.fetchall()

# create dictionary of word:document list
output_doclist = {}

for rs in results:
    # get document id
    doc_id = int(rs[0])

    # String splite
    str = rs[1]
    word_list = str.split("|")
    #print str

    for word in word_list:
        try:
            output_doclist[word].append(doc_id)
        except:
            output_doclist[word] = [doc_id]

print len(output_doclist)

for k, v in output_doclist.items():
    docs = ''
    term = k
    for docid in v:
        docs += " d%i" % docid
    #print k, docs
    outfile.write(term + ':' + unicode(docs) + '\n')
    #print type(unicode(docs))

outfile.close()

#conn.query(sql_test)
#rs_test = conn.use_result()
#print rs_test.fetch_row()
cursor.close()
conn.close()
