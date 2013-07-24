#!/usr/bin/python
# -*- coding: utf-8 -*- #

from filter import dimension
from wfDatabase import wfdb
from sklearn import svm, cross_validation
from sklearn.externals import joblib
from sklearn.metrics import classification_report
import MySQLdb
import codecs

# Create a connection
conn = MySQLdb.connect(host="localhost",
                       user="wfproject",
                       passwd="1q2w3e4r",
                       db="WFProject",
                       charset="utf8")

# Database number in View list
db_num = 3


# Get TFIDF Score Vector by CHI term list
def getTDIDFScoreVector(chi_zero_list, term_tfidf_list):
    base_dict = chi_zero_list.copy()
    for term_tfidf_pair in term_tfidf_list:
        term_tfidf = term_tfidf_pair.split("@")
        term = term_tfidf[0]
        tfidf = float(term_tfidf[1])
        if term in base_dict:
            base_dict[term] = tfidf
        else:
            continue
        """
        try:
            base_dict[term] = tfidf
        except:
            print "except: %s" % term
            continue
    print set(base_dict) ^ set(chi_zero_list)
    """
    return base_dict.values()


# Get cross validation Data and Target Set by index list
def getValiSetByIndexList(src_data_list, src_target_list, index_list):
    rtn_data_list = []
    rtn_target_list = []
    for idx in index_list:
        rtn_data_list.append(src_data_list[idx])
        rtn_target_list.append(src_target_list[idx])
    return rtn_data_list, rtn_target_list

# Instance dimension class
obj_dims = dimension()

# Instance dimension class
obj_db = wfdb()

# Get Average CHI Score Dictionary list
avg_chi_list = obj_dims.getAvgCHIList()
max_chi_list = obj_dims.getMaxCHIList()

# Filter list by CHI score
filted_avg_list = obj_dims.doFilteredList(0.028, avg_chi_list)

# Reset all values in dictionary
chi_zero_list = dict.fromkeys(filted_avg_list, 0.0)

# Get database View List
tfidf_viewlist = obj_db.getTFIDFViewList()

sql_getContent = "SELECT `ClsNo1`, `ScoreContent` FROM `" + tfidf_viewlist[db_num] + "` ORDER BY RAND()"

# Get connection cursor
view_cursor = conn.cursor()

# Execute the SQL statement
view_cursor.execute(sql_getContent)

# Get All result
view_results = view_cursor.fetchall()

feature_dataset = []
category_dataset = []
for view_row in view_results:
    view_content = view_row[1]
    term_tfidf_list = view_content.split("|")
    tfidf_score_vector = getTDIDFScoreVector(chi_zero_list, term_tfidf_list)

    feature_dataset.append(tfidf_score_vector)
    category_dataset.append(int(view_row[0]))

print len(feature_dataset)
print len(category_dataset)
"""print category_dataset"""

"""
Use Scikit-learn python Mechine learning libreary to learning
"""
# Use scikit-learn libreary to build classfiler
clf = svm.SVC(kernel='linear')
# clf.fit(feature_dataset, category_dataset)

k_fold = cross_validation.KFold(len(category_dataset), n_folds=10)
data_name = (tfidf_viewlist[db_num]).replace('VIEW_CateTFIDF', '')
outfile = codecs.open('report/' + data_name + '_train_result.txt', 'w', 'utf-8')

i = 1
for train_index_list, test_index_list in k_fold:
    print str(i) + '-times Training --------------------------------'
    train_set = getValiSetByIndexList(feature_dataset, category_dataset, train_index_list)
    clf.fit(train_set[0], train_set[1])

    joblib.dump(clf, 'pickle/' + data_name + '_train_' + str(i) + '.pkl', compress=9)

    test_set = getValiSetByIndexList(feature_dataset, category_dataset, test_index_list)

    pred_result = clf.predict(test_set[0])
    print (classification_report(test_set[1], pred_result))

    print str(i) + '-times Training --------------------------------' + "\n"
    outfile.write((classification_report(test_set[1], pred_result)) + "\n\n")
    """
    target_names = ['class 1', 'class 2', 'class 3', 'class 4', 'class 5', 'class 6', 'class 7', 'class 8', 'class 9']
    print (classification_report(test_set[1], pred_result, target_names=target_names))
    """
    i += 1

outfile.close()
