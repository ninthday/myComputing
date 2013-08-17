#!/usr/bin/python
# -*- coding: utf-8 -*- #
from filter import dimension
from wfDatabase import wfdb
import MySQLdb

# Create a connection
conn = MySQLdb.connect(host="localhost",
                       user="wfproject",
                       passwd="1q2w3e4r",
                       db="WFProject",
                       charset="utf8")

# Instance dimension class
obj_dims = dimension()

# Instance Database list class
obj_db = wfdb()

# Get Average CHI Score Dictionary list
dict_avg_chi = obj_dims.getAvgCHIList()

list_date = ["2009-08-06", "2009-08-07", "2009-08-08", "2009-08-09",
             "2009-08-10", "2009-08-11", "2009-08-12", "2009-08-13",
             "2009-08-14", "2009-08-15", "2009-08-16", "2009-08-17",
             "2009-08-18", "2009-08-19", "2009-08-20", "2009-08-21",
             "2009-08-22", "2009-08-23", "2009-08-24", "2009-08-25",
             "2009-08-26", "2009-08-27", "2009-08-28", "2009-08-29",
             "2009-08-30", "2009-08-31", "2009-09-01", "2009-09-02",
             "2009-09-03", "2009-09-04", "2009-09-05", "2009-09-06",
             "2009-09-07", "2009-09-08"]

# Get Segment Date View list
list_segdate_view = obj_db.getSegDateViewList()

dict_result = {}

# Get connect cursor
cursor = conn.cursor()

for dbname in list_segdate_view:
    for occ_date in list_date:
        print dbname + ' --> ' + occ_date + ' proc-ing.....'
        sql_getSeg = "SELECT * FROM " + dbname + " WHERE `OccDate`='" + occ_date + "'"
        cursor.execute(sql_getSeg)

        seg_results = cursor.fetchall()

        for seg_row in seg_results:
            # print 'ID: ' + str(seg_row[0])
            seg_content = seg_row[1]
            word_list = seg_content.split("|")
            for key, val in dict_avg_chi.items():
                # if term in word list add or update result dict
                if key in word_list:
                    # if term already in result dict, to finding date key
                    if key in dict_result:
                        #if date key exist, update count +1
                        if occ_date in dict_result[key]:
                            dict_result[key][occ_date][1] += 1
                        # if not exist, add new dict
                        else:
                            dict_result[key][occ_date] = [val, 1]
                    else:
                        dict_result[key] = {occ_date: [val, 1]}
                else:
                    continue

print dict_result
print len(dict_result)

i = 1
for term, dict_row in dict_result.items():
    for occ_date, list_val in dict_row.items():
        sql_insert = unicode('INSERT INTO `procCHIScatter` VALUES (NULL, \'{0:s}\', \'{1:s}\', {2:f}, {3:d})').format(term, occ_date, list_val[0], list_val[1])
        cursor.execute(sql_insert)
    print i
    i += 1
cursor.close()
conn.close()
