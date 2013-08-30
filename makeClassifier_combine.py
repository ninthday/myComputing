#!/usr/bin/python
# -*- coding: utf-8 -*- #

from filter import dimension
from wfDatabase import wfdb
from sklearn import svm, cross_validation
from sklearn.externals import joblib
from sklearn.metrics import classification_report, f1_score
from wfMySQL import MySQLConnector
import codecs
import numpy as np
import scipy.stats as sp
from random import shuffle

# Database number in View list
"""db_num = 1"""
# Set average CHI Score filter threshold
avg_filter_num = 0.0299

# Set max CHI Score filter threshold
max_filter_num = 0.1394

# Set training combine dataset
list_combine_dataset = [2, 3]


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


# Get confidence interval
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), sp.sem(a)
    h = se * sp.t._ppf((1 + confidence) / 2., n - 1)
    return [m, h, m - h, m + h]


# Randomize feature and category dataset
def randomizeDataset(feature_dataset, category_dataset):
    random_list = range(len(category_dataset))
    shuffle(random_list)
    new_feature = []
    new_category = []
    for i in random_list:
        new_feature.append(feature_dataset[i])
        new_category.append(category_dataset[i])
    feature_dataset[:] = []
    category_dataset[:] = []
    return new_feature, new_category

# Instance dimension class
obj_dims = dimension()

# Instance Database list class
obj_db = wfdb()

# Instance mysql connector class
mysql = MySQLConnector()

# Get Average CHI Score Dictionary list
avg_chi_list = obj_dims.getAvgCHIList()

# Get Max CHI Score dictionary list
max_chi_list = obj_dims.getMaxCHIList()

# Filter list by CHI score
filted_avg_list = obj_dims.doFilteredList(avg_filter_num, avg_chi_list)
filted_max_list = obj_dims.doFilteredList(max_filter_num, max_chi_list)

# Get database View List
tfidf_viewlist = obj_db.getTFIDFViewList()

# Length of vector dimension
len_avg_vd = len(filted_avg_list)
len_max_vd = len(filted_max_list)

print 'Amount of Avg CHI is: ' + str(len_avg_vd)
print 'Amount of Max CHI is: ' + str(len_max_vd)

# Init feature and category dataset
avg_feature_dataset = []
avg_category_dataset = []
max_feature_dataset = []
max_category_dataset = []

for db_num in list_combine_dataset:
    print 'Now proc ' + tfidf_viewlist[db_num] + ' Feature and Category dataset'
    # Reset all values in dictionary
    avg_chi_zero_list = dict.fromkeys(filted_avg_list, 0.0)
    max_chi_zero_list = dict.fromkeys(filted_max_list, 0.0)

    sql_getContent = "SELECT `ClsNo1`, `ScoreContent` FROM `" + tfidf_viewlist[db_num] + "` ORDER BY RAND()"

    # Get All result
    view_results = mysql.queryrows(sql_getContent)

    for view_row in view_results:
        view_content = view_row[1]
        term_tfidf_list = view_content.split("|")
        avg_tfidf_score_vector = getTDIDFScoreVector(avg_chi_zero_list, term_tfidf_list)
        max_tfidf_score_vector = getTDIDFScoreVector(max_chi_zero_list, term_tfidf_list)

        avg_feature_dataset.append(avg_tfidf_score_vector)
        avg_category_dataset.append(int(view_row[0]))
        max_feature_dataset.append(max_tfidf_score_vector)
        max_category_dataset.append(int(view_row[0]))

    print 'AVG_feature_dataset:' + str(len(avg_feature_dataset))
    print 'AVG_category_dataset:' + str(len(avg_category_dataset))
    print 'MAX_feature_dataset:' + str(len(max_feature_dataset))
    print 'MAX_category_dataset:' + str(len(max_category_dataset))
    """print category_dataset"""

# Randomize dataset to avoid the same dataset data tied together
avg_feature_dataset, avg_category_dataset = randomizeDataset(avg_feature_dataset, avg_category_dataset)
max_feature_dataset, max_category_dataset = randomizeDataset(max_feature_dataset, max_category_dataset)


"""
Use Scikit-learn python Mechine learning libreary to learning
"""
# Use scikit-learn libreary to build classfiler
clf = svm.SVC(kernel='linear')
# clf.fit(feature_dataset, category_dataset)

"""
k_fold = cross_validation.KFold(len(category_dataset), n_folds=5)
"""
print "All Database :::::::::::::::::::::::::::::::"

avg_sk_fold = cross_validation.StratifiedKFold(avg_category_dataset, n_folds=10)
outfile = codecs.open('report/avg_sk_CDCombine_' + str(len_avg_vd) + '_train_result.txt', 'w', 'utf-8')
outfile.write("Cross-validation: Stratified 10-fold CV\n")
outfile.write('Avg CHI Static Score: ' + str(avg_filter_num) + "\n")
outfile.write('Length of vector dimension: ' + str(len_avg_vd) + "\n\n")

i = 1
"""
Avearage:
for train_index_list, test_index_list in k_fold:
"""
# Set dictionary and list for computing confidence interval
dict_all_f1Soc = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
list_wegt_avg_f1Soc = []
for train_index_list, test_index_list in avg_sk_fold:
    print 'AVG ' + str(i) + '-times Training --------------------------------'
    train_set = getValiSetByIndexList(avg_feature_dataset, avg_category_dataset, train_index_list)
    clf.fit(train_set[0], train_set[1])

    joblib.dump(clf, 'pickle/avg_sk_CDCombine_' + str(len_avg_vd) + '_train_' + str(i) + '.pkl', compress=9)

    test_set = getValiSetByIndexList(avg_feature_dataset, avg_category_dataset, test_index_list)

    pred_result = clf.predict(test_set[0])
    print (classification_report(test_set[1], pred_result))

    outfile.write(str(i) + '-times Training --------------------------------' + "\n")
    outfile.write((classification_report(test_set[1], pred_result)) + "\n\n")
    """
    target_names = ['class 1', 'class 2', 'class 3', 'class 4', 'class 5', 'class 6', 'class 7', 'class 8', 'class 9']
    print (classification_report(test_set[1], pred_result, target_names=target_names))
    """
    result_f1Soc = f1_score(test_set[1], pred_result, average=None)
    result_category = sorted(list(set(test_set[1])))
    dict_f1Soc = dict(zip(result_category, result_f1Soc))

    # Weighted Average F1-measure of the all category
    list_wegt_avg_f1Soc.append(f1_score(test_set[1], pred_result, average='weighted'))
    print result_category
    print dict_f1Soc
    outfile.write(str(dict_f1Soc) + "\n\n")

    # Put value into dictionary that was all category F1-measure score
    for k in range(1, 10):
        if k in dict_f1Soc:
            dict_all_f1Soc[k].append(dict_f1Soc[k])
        else:
            dict_all_f1Soc[k].append(0.0)
    i += 1

# Show each category F1-measure score and 95% confidence interval
outfile.write("Category:\tF1-measure Score\n")
for key, value in dict_all_f1Soc.items():
    mean_ci = mean_confidence_interval(value, 0.95)
    print "C" + str(key) + ":\t\t%.2f +- %.2f" % (round(mean_ci[0], 2), round(mean_ci[1], 2))
    outfile.write("C" + str(key) + ":\t\t%.2f +- %.2f \n" % (round(mean_ci[0], 2), round(mean_ci[1], 2)))
avg_mean_ci = mean_confidence_interval(list_wegt_avg_f1Soc, 0.95)
outfile.write("avg / total\t%.2f +- %.2f" % (round(avg_mean_ci[0], 2), round(avg_mean_ci[1], 2)))
print "avg / total\t%.2f +- %.2f" % (round(avg_mean_ci[0], 2), round(avg_mean_ci[1], 2))

max_sk_fold = cross_validation.StratifiedKFold(max_category_dataset, n_folds=10)
outfile.close()

i = 1
"""
Maxinum:
for train_index_list, test_index_list in k_fold:
"""
outfile = codecs.open('report/max_sk_CDCombine_' + str(len_max_vd) + '_train_result.txt', 'w', 'utf-8')
outfile.write("Cross-validation: Stratified 10-fold CV\n")
outfile.write('Max CHI Static Score: ' + str(max_filter_num) + "\n")
outfile.write('Length of vector dimension: ' + str(len_max_vd) + "\n\n")

# Set dictionary and list for computing confidence interval
dict_all_f1Soc = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
list_wegt_avg_f1Soc = []
for train_index_list, test_index_list in avg_sk_fold:
    print str(i) + '-times Training --------------------------------'
    train_set = getValiSetByIndexList(max_feature_dataset, max_category_dataset, train_index_list)
    clf.fit(train_set[0], train_set[1])

    joblib.dump(clf, 'pickle/max_sk_CDCombine_' + str(len_max_vd) + '_train_' + str(i) + '.pkl', compress=9)

    test_set = getValiSetByIndexList(max_feature_dataset, max_category_dataset, test_index_list)

    pred_result = clf.predict(test_set[0])
    print (classification_report(test_set[1], pred_result))

    outfile.write(str(i) + '-times Training --------------------------------' + "\n")
    outfile.write((classification_report(test_set[1], pred_result)) + "\n\n")
    """
    target_names = ['class 1', 'class 2', 'class 3', 'class 4', 'class 5', 'class 6', 'class 7', 'class 8', 'class 9']
    print (classification_report(test_set[1], pred_result, target_names=target_names))
    """
    result_f1Soc = f1_score(test_set[1], pred_result, average=None)
    result_category = sorted(list(set(test_set[1])))
    dict_f1Soc = dict(zip(result_category, result_f1Soc))

    # Weighted Average F1-measure of the all category
    list_wegt_avg_f1Soc.append(f1_score(test_set[1], pred_result, average='weighted'))
    print result_category
    print dict_f1Soc
    outfile.write(str(dict_f1Soc) + "\n\n")

    # Put value into dictionary that was all category F1-measure score
    for k in range(1, 10):
        if k in dict_f1Soc:
            dict_all_f1Soc[k].append(dict_f1Soc[k])
        else:
            dict_all_f1Soc[k].append(0.0)
    i += 1

# Show each category F1-measure score and 95% confidence interval
outfile.write("Category:\tF1-measure Score\n")
for key, value in dict_all_f1Soc.items():
    mean_ci = mean_confidence_interval(value, 0.95)
    print "C" + str(key) + ":\t\t%.2f +- %.2f" % (round(mean_ci[0], 2), round(mean_ci[1], 2))
    outfile.write("C" + str(key) + ":\t\t%.2f +- %.2f \n" % (round(mean_ci[0], 2), round(mean_ci[1], 2)))
avg_mean_ci = mean_confidence_interval(list_wegt_avg_f1Soc, 0.95)
outfile.write("avg / total\t%.2f +- %.2f" % (round(avg_mean_ci[0], 2), round(avg_mean_ci[1], 2)))
print "avg / total\t%.2f +- %.2f" % (round(avg_mean_ci[0], 2), round(avg_mean_ci[1], 2))

max_sk_fold = cross_validation.StratifiedKFold(max_category_dataset, n_folds=10)
outfile.close()

# Close connection
mysql.disconnect()
