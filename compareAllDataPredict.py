#!/usr/usr/python
# -*- coding: utf-8 -*- #

from filter import dimension
from wfDatabase import wfdb
from sklearn.externals import joblib
from sklearn.metrics import classification_report, f1_score
from wfMySQL import MySQLConnector
import codecs
import numpy as np
import scipy.stats as sp

# Set average CHI score filter threshold
avg_filter_threshold = 0.0299

# Set maxinum CHI score filter threshold
max_filter_threshold = 0.1394


# Get TFIDF Score Vector by CHI term list
def getTFIDFScoreVector(chi_zero_list, term_tfidf_list):
    base_dict = chi_zero_list.copy()
    for term_tfidf_pair in term_tfidf_list:
        list_pair = term_tfidf_pair.split("@")
        term = list_pair[0]
        tfidf = float(list_pair[1])
        if term in base_dict:
            base_dict[term] = tfidf
        else:
            continue
    return base_dict.values()


# Get confidence interval
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), sp.sem(a)
    h = se * sp.t._ppf((1 + confidence) / 2., n - 1)
    return [m, h, m - h, m + h]

# Instance dimension class
obj_dims = dimension()

# Instance Database list class
obj_db = wfdb()

# Instance mysql connector class
mysql = MySQLConnector()

# Get Average CHI Score Dictionary
dict_avg_chi = obj_dims.getAvgCHIList()

# Get Maxiunm CHI Score Dictionary
dict_max_chi = obj_dims.getMaxCHIList()

# Filter CHI Score dictionary by threshold
dict_flted_avgchi = obj_dims.doFilteredList(avg_filter_threshold, dict_avg_chi)
dict_flted_maxchi = obj_dims.doFilteredList(max_filter_threshold, dict_max_chi)

# Get Database View List
tfidf_viewlist = obj_db.getTFIDFViewList()

for view_num in range(5):
    # Init ang reset feature and category dataset
    avg_feature = []
    avg_category = []
    max_feature = []
    max_category = []

    # Rest All value to 0.0 in dictionary
    dict_avg_zero = dict.fromkeys(dict_flted_avgchi, 0.0)
    dict_max_zero = dict.fromkeys(dict_flted_maxchi, 0.0)

    sql_getContent = "SELECT `ClsNo1`, `ScoreContent` FROM `" + tfidf_viewlist[view_num] + "`"

    # Get All result
    view_result = mysql.queryrows(sql_getContent)

    for view_row in view_result:
        view_content = view_row[1]
        term_tfidf_list = view_content.split("|")
        avg_tfidf_score_vactor = getTFIDFScoreVector(dict_avg_zero, term_tfidf_list)
        max_tfidf_score_vextor = getTFIDFScoreVector(dict_max_zero, term_tfidf_list)

        avg_feature.append(avg_tfidf_score_vactor)
        avg_category.append(int(view_row[0]))
        max_feature.append(max_tfidf_score_vextor)
        max_category.append(int(view_row[0]))

    print 'AVG Feature dataset: ' + str(len(avg_feature))
    print 'AVG Category dataset: ' + str(len(avg_category))
    print 'MAX Feature dataset: ' + str(len(max_feature))
    print 'MAX Category dataset: ' + str(len(max_category))

    data_name = (tfidf_viewlist[view_num]).replace('VIEW_CateTFIDF', '')

    # Compare Predict in average CHI
    outfile = codecs.open('compare/avg_cpr_all_' + data_name + '.txt', 'w', 'utf-8')
    outfile.write('Avg CHI Static Score: ' + str(avg_filter_threshold) + '\n')
    outfile.write('Length of vector dimension: ' + str(len(dict_flted_avgchi)) + '\n')

    dict_all_f1Soc = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
    list_wtg_avg_f1Soc = []

    for i in range(1, 11):
        print 'Loading....avg_sk_all_7009_train_' + str(i) + '.pkl'
        clf = joblib.load('pickle/avg_sk_all_7009_train_' + str(i) + '.pkl')
        print 'Load done.'

        pred_result = clf.predict(avg_feature)
        print data_name + ': ' + str(i) + '-times AVG Compare Testing-----------------------------------'
        print classification_report(avg_category, pred_result)

        outfile.write(str(i) + '-times AVG Compare Testing-----------------------------------\n')
        outfile.write(classification_report(avg_category, pred_result) + '\n\n')

        result_f1Soc = f1_score(avg_category, pred_result, average=None)
        result_category = sorted(list(set(avg_category)))
        dict_f1Soc = dict(zip(result_category, result_f1Soc))

        # Weighted Average F1-measure of all category
        list_wtg_avg_f1Soc.append(f1_score(avg_category, pred_result, average='weighted'))

        print dict_f1Soc
        outfile.write(str(dict_f1Soc) + '\n\n')

        # Put value or zero into dictionary, that was all category's F1-Score
        for k in range(1, 10):
            if k in dict_f1Soc:
                dict_all_f1Soc[k].append(dict_f1Soc[k])
            else:
                dict_all_f1Soc[k].append(0.0)
    # Show each category F1-Score and 95% confidence interval
    outfile.write('Category:\tF1-measure Score\n')
    for key, value in dict_all_f1Soc.items():
        mean_ci = mean_confidence_interval(value, 0.95)

        print 'C' + str(key) + ':\t\t%.2f +- %.2f' % (round(mean_ci[0], 2), round(mean_ci[1], 2))
        outfile.write('C' + str(key) + ':\t\t%.2f +- %.2f\n' % (round(mean_ci[0], 2), round(mean_ci[1], 2)))

    avg_mean_ci = mean_confidence_interval(list_wtg_avg_f1Soc, 0.95)
    print 'avg / total\t\t%.2f +- %.2f' % (round(avg_mean_ci[0], 2), round(avg_mean_ci[1], 2))
    outfile.write('avg / total\t\t%.2f +- %.2f\n' % (round(avg_mean_ci[0], 2), round(avg_mean_ci[1], 2)))

    outfile.close()

    # Compare Predict in max CHI
    outfile = codecs.open('compare/max_cpr_all_' + data_name + '.txt', 'w', 'utf-8')
    outfile.write('Max CHI Static Score: ' + str(max_filter_threshold) + '\n')
    outfile.write('Length of vector dimension: ' + str(len(dict_flted_maxchi)) + '\n')

    dict_all_f1Soc = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
    list_wtg_avg_f1Soc = []

    for i in range(1, 11):
        print 'Loading....max_sk_all_7002_train_' + str(i) + '.pkl'
        clf = joblib.load('pickle/max_sk_all_7002_train_' + str(i) + '.pkl')
        print 'Load done.'

        pred_result = clf.predict(max_feature)
        print data_name + ': ' + str(i) + '-times Max Compare Testing-----------------------------------'
        print classification_report(max_category, pred_result)

        outfile.write(str(i) + '-times Max Compare Testing-----------------------------------\n')
        outfile.write(classification_report(max_category, pred_result) + '\n\n')

        result_f1Soc = f1_score(max_category, pred_result, average=None)
        result_category = sorted(list(set(max_category)))
        dict_f1Soc = dict(zip(result_category, result_f1Soc))

        # Weighted Average F1-measure of all category
        list_wtg_avg_f1Soc.append(f1_score(max_category, pred_result, average='weighted'))

        print dict_f1Soc
        outfile.write(str(dict_f1Soc) + '\n\n')

        # Put value or zero into dictionary, that was all category's F1-Score
        for k in range(1, 10):
            if k in dict_f1Soc:
                dict_all_f1Soc[k].append(dict_f1Soc[k])
            else:
                dict_all_f1Soc[k].append(0.0)
    # Show each category F1-Score and 95% confidence interval
    outfile.write('Category:\tF1-measure Score\n')
    for key, value in dict_all_f1Soc.items():
        mean_ci = mean_confidence_interval(value, 0.95)

        print 'C' + str(key) + ':\t\t%.2f +- %.2f' % (round(mean_ci[0], 2), round(mean_ci[1], 2))
        outfile.write('C' + str(key) + ':\t\t%.2f +- %.2f\n' % (round(mean_ci[0], 2), round(mean_ci[1], 2)))

    avg_mean_ci = mean_confidence_interval(list_wtg_avg_f1Soc, 0.95)
    print 'avg / total\t\t%.2f +- %.2f' % (round(avg_mean_ci[0], 2), round(avg_mean_ci[1], 2))
    outfile.write('avg / total\t\t%.2f +- %.2f\n' % (round(avg_mean_ci[0], 2), round(avg_mean_ci[1], 2)))

    outfile.close()
