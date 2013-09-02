#!/usr/usr/python
# -*- coding: utf-8 -*- #

from filter import dimension
from wfDatabase import wfdb
from sklearn.externals import joblib
#from sklearn.metrics import classification_report, f1_score
from wfMySQL import MySQLConnector
from operator import itemgetter
#import codecs
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


# Get most common element in list
def most_common(list_term):
    dict_count = {}
    for item in list_term:
        dict_count.setdefault(item, 0)
        dict_count[item] += 1
    return max(dict_count.iteritems(), key=itemgetter(1))[0]

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

# Rest All value to 0.0 in dictionary
dict_avg_zero = dict.fromkeys(dict_flted_avgchi, 0.0)
dict_max_zero = dict.fromkeys(dict_flted_maxchi, 0.0)

sql_getContent = 'SELECT `SamplingNo`, `ScoreContent`  FROM `CoderCompare` INNER JOIN `OrigRicks` ON `OrigRicks`.`RNId` = `CoderCompare`.`SamplingNo` INNER JOIN `TFIDFRicksNSW` ON `TFIDFRicksNSW`.`TIId` = `OrigRicks`.`RCId` GROUP BY `SamplingNo`'

result = mysql.queryrows(sql_getContent)

# Init predict result dictionary
avg_all_predict = {}
max_all_predict = {}

for i in range(1, 11):
    print 'Loading....avg_sk_all_7009_train_' + str(i) + '.pkl'
    clf = joblib.load('pickle/avg_sk_all_7009_train_' + str(i) + '.pkl')
    print 'Load done.'
    for row in result:
        sid = int(row[0])
        seg_content = row[1]
        list_term_tfidf = seg_content.split("|")
        avg_tfidf_score_vactor = getTFIDFScoreVector(dict_avg_zero, list_term_tfidf)
        pred_result = clf.predict(avg_tfidf_score_vactor)
        if sid in avg_all_predict:
            avg_all_predict[sid].append(int(pred_result[0]))
        else:
            avg_all_predict[sid] = [int(pred_result[0])]

# Most common value in Vote predict result
vote_result = {}
for key, value in avg_all_predict.items():
    vote_result[key] = most_common(value)

print avg_all_predict

for key, value in vote_result.items():
    # print type(key), type(value)
    sql_insert = unicode('INSERT INTO `CoderCompare`(`DBId`, `SamplingNo`, `ClsNo1`, `UserId`, `SettingTime`) VALUES (4,{0:d},{1:d},4,NOW())').format(key, value)
    mysql.insert(sql_insert)

mysql.disconnect()
