#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import codecs
import sys
import math
#import tfidf

def freqence(term, doc_id, term_doc_list):
	return term_doc_list[term].count(doc_id)

def contain_doc_num(term, term_doc_set):
	return len(term_doc_set[term])

def content_tfidf(doc_id, content_words, term_doc_list, term_doc_set, total_doc_num):
	word_list = content_words.split("|")
	content_words_nums = len(word_list)
	rtn_list = []
	for word in word_list:
		tf = freqence(word, doc_id, term_doc_list)/float(content_words_nums)
		idf = math.log(total_doc_num/float(contain_doc_num(word, term_doc_set)))
		tfidf = tf * idf
		rtn_list.append(unicode('{0:s}@{1:.10f}').format(unicode(word), tfidf)) 

	return '|'.join(rtn_list)


#create mysql connection
conn = MySQLdb.connect(host="localhost",
                       user="wfproject",
                       passwd="1q2w3e4r",
                       db="WFProject",
                       charset="utf8")

# Database Name list
source_dblist = ('SegXditeNSW', 'SegPingtungNSW', 'SegTainanNSW', 'SegRicksNSW', 'SegXditeCombineNSW', 'SegAdctNSW')


score_dblist = ('TFIDFXditeNSW', 'TFIDFPingtungNSW', 'TFIDFTainanNSW', 'TFIDFRicksNSW', 'TFIDFXditeCombineNSW', 'TFIDFAdctNSW')

# Get System argument
dbnum = int(sys.argv[1])

# Set database name
dbname = source_dblist[dbnum]

# SQL statement
sql_test = 'SELECT * FROM `' + dbname + '`'

# Get Connection cursor
cursor = conn.cursor()

# Execute the SQL statement
cursor.execute(sql_test)

# Get all result
results = cursor.fetchall()

# create dictionary of word:document list
term_doc_list = {}
term_doc_set = {}
total_doc_num = 0

for rs in results:
    # get document id
    doc_id = int(rs[0])

    # String splite
    str = rs[1]
    word_list = str.split("|")
    
    total_doc_num += 1

    for word in word_list:
        try:
            term_doc_list[word].append(doc_id)
        except:
            term_doc_list[word] = [doc_id]

# Generate a term set for count term document 
for k, v in term_doc_list.items():
	term_doc_set[k] = set(v)

# Scroll the cursor in the result set to first raw
cursor.scroll(0,mode='absolute')

# Get all result again
results = cursor.fetchall()

for rs in results:
	# Get Document ID
	doc_id = int(rs[0])

	# Contant String
	strContent = rs[1]
	
	# Insert SQL statement
	sql_insert = unicode('INSERT INTO `{0:s}` VALUES({1:d}, \'{2:s}\')').format(score_dblist[dbnum], doc_id, content_tfidf(doc_id, strContent, term_doc_list, term_doc_set, total_doc_num))
	cursor.execute(sql_insert)

	#print content_tfidf(doc_id, strContent, term_doc_list, term_doc_set, total_doc_num)

cursor.close()
# close mysql database connection
conn.close()