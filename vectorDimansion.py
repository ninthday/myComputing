#!/usr/bin/python
# -*- coding: utf-8 -*- #

"""vectorDimansion.py: This file is to compute dimansion CHI Score and save to text file"""
__author__ = "Jeffy Shih (jeffy.sf@gmail.com)"
__email__ = "jeffy.sf@gmail.com"
__credits__ = ["Jeffy Shih"]
__copyright__ = "Copyright(c)Intelligent Media Laboratory, NCCU"
__version__ = "1.0.0"

import MySQLdb
import codecs
import re
import enchant


# Create a connection
conn = MySQLdb.connect(host="localhost",
                       user="wfproject",
                       passwd="1q2w3e4r",
                       db="WFProject",
                       charset="utf8")

# Regular expression - ptn1: find english letter and numbehiuh feng

ptn1 = re.compile("^[\w\d]*$")
ptn2 = re.compile("^[\d]*$")
dic = enchant.Dict("en_US")


# Verify English Words or Number
# return 0: not-eng letter and not-number
#       1: All was numbers
#       2: English words
#       3: not-english words
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


# Return each term CHI static score dictionary
def getCHIScore(term, cate_list, cate_doc_amount_list):
    # Total Document
    total_doc_amount = getTotalDocNumber(cate_doc_amount_list)

    # A + B + C + D
    total_alltimes = getAllTimes(cate_list)

    # A + B
    total_term_times = getTermAllTimes(term, cate_list)
    if total_term_times == 0:
        return [0.0, 0.0]
    # A + C
    cate_allterm_count_list = getCateTermCountList(cate_list)

    # Initialize
    sum_cate_chi = 0.0
    cate_chi_list = [0.0] * 9
    for i in xrange(9):
        # A Times, number of times, term and category co-occurs
        try:
            A_times = cate_list[i][term]
        except:
            A_times = 0

        # B Times, number of times, the term occurs without category
        B_times = total_term_times - A_times

        # C Times, number of times, the category occurs witout term
        C_times = cate_allterm_count_list[i] - A_times

        # D Times, number of times neither category nor term occurs
        D_times = total_alltimes - cate_allterm_count_list[i] - B_times

        """
        print "Category %d --------------" % (i + 1)
        print "A times is %d" % A_times
        print "B times is %d" % B_times
        print "C times is %d" % C_times
        print "D times is %d" % D_times
        """

        # Compute each category CHI score x(t,c)
        cate_chi = float(total_doc_amount * (((A_times * D_times) - (C_times * B_times)) ** 2)) / float((A_times + C_times) * (B_times + D_times) * (A_times + B_times) * (C_times + D_times))
        '''
        print "Category CHI Score is %f" % cate_chi
        '''

        # For compute average CHI score
        sum_cate_chi += cate_chi * cate_doc_amount_list[i]

        #Set CHI score in each category
        cate_chi_list[i] = cate_chi

    # Average CHI Score
    avg_chi = (sum_cate_chi / float(total_doc_amount))
    '''
    print "Avg.CHI Score is %f" % avg_chi
    '''

    max_chi = max(cate_chi_list)
    '''
    print "Max.CHI Scoreis %f" % max_chi
    '''
    return [avg_chi, max_chi]


# Get All times
def getAllTimes(cate_list):
    cate_allterm_count_list = getCateTermCountList(cate_list)
    sum = 0
    for i in xrange(9):
        sum += cate_allterm_count_list[i]
    '''
    print "All times is %d" % sum
    '''
    return sum


# Get term times in all category
def getTermAllTimes(term, cate_list):
    sum = 0
    for i in xrange(9):
        try:
            sum += cate_list[i][term]
        except:
            sum += 0

    return sum


# Get the list of term count in each category
def getCateTermCountList(cate_list):
    rtn_list = [0] * 9
    for i in xrange(9):
        sum = 0
        for k, v in cate_list[i].items():
            sum += v
        rtn_list[i] = sum
    return rtn_list


# Get the list of document amount in each category
def getCateDocAmountList():
    rtn_list = [0] * 9
    sql_cp = "SELECT `ClsNo1`, count(*) FROM `Sampling2Turn` GROUP BY `ClsNo1`"
    #  Get Connection cursor
    cursor = conn.cursor()

    # Execute the SQL statement
    cursor.execute(sql_cp)

    # get All result
    results = cursor.fetchall()

    for row in results:
        rtn_list[row[0] - 1] = int(row[1])
    # Close connection cursor
    cursor.close()
    return rtn_list


# Get Total number of document
def getTotalDocNumber(cate_doc_amount_list):
    sum = 0
    for num in cate_doc_amount_list:
        sum += num
    return sum

# Database Table Name list
dblist = ('SegPingtungNSW', 'SegTainanNSW', 'SegRicksNSW', 'SegXditeCombineNSW', 'SegAdctNSW')

# Database Category and Segment VIEW Name list
viewlist = ('VIEW_CateTainan', 'VIEW_CatePingtung', 'VIEW_CateRicks', 'VIEW_CateXditeCombine', 'VIEW_CateAdct')

cate_list = [{}, {}, {}, {}, {}, {}, {}, {}, {}]

# Build every category term count, for computing CHI Score
for viewname in viewlist:
    # Get View Table content in Database
    sql_getview = "SELECT * FROM `" + viewname + "`"

    # Get connection cursor
    view_cursor = conn.cursor()

    # Execute the SQL statement
    view_cursor.execute(sql_getview)

    # Get All view result
    view_results = view_cursor.fetchall()

    for view_row in view_results:
        view_content = view_row[4]
        view_word_list = view_content.split("|")
        for view_word in view_word_list:
            try:
                cate_list[view_row[2] - 1][view_word] += 1
            except:
                cate_list[view_row[2] - 1][view_word] = 1
view_cursor.close()
print "Category term count list has builded.........."
'''
print "Cate1: %d" % len(cate_list[0])
print "Cate2: %d" % len(cate_list[1])
print "Cate3: %d" % len(cate_list[2])
print "Cate4: %d" % len(cate_list[3])
print "Cate5: %d" % len(cate_list[4])
print "Cate6: %d" % len(cate_list[5])
print "Cate7: %d" % len(cate_list[6])
print "Cate8: %d" % len(cate_list[7])
print "Cate9: %d" % len(cate_list[8])
'''

# Create dictionary of word:document list
dimension_list = {}

for dbname in dblist:
    # Get content in database SQL Statement
    sql = "SELECT * FROM`" + dbname + "`"

    # Get Connection cursor
    cursor = conn.cursor()

    # Execute the SQL statement
    cursor.execute(sql)

    # Get result
    results = cursor.fetchall()

    # Create dictionary of word:document list
    #dimension_list = {}

    for rs in results:
        content = rs[1]
        word_list = content.split("|")
        for word in word_list:
            try:
                dimension_list[word] += 1
            except:
                dimension_list[word] = 1
    """
    print "Add %s term amount %d" % (dbname, len(dimension_list))
    """
cursor.close()
print "Dimension term list has created. Length is %d." % len(dimension_list)

# Remove some term when count < 1
for k, v in dimension_list.items():
    if v < 2:
        dimension_list.pop(k)

# Remove number and not english word in dictionary
for k, v in dimension_list.items():
    if verifyEngNum(k) == 1 or verifyEngNum(k) == 3:
        dimension_list.pop(k)

print "Dimension list has removed Count < 1 and not eng word. Lenght is %d" % len(dimension_list)

cate_doc_amount_list = getCateDocAmountList()
# Initialize average CHI Score List and max_chi_dimension_list
avg_chi_dimension_list, max_chi_dimension_list = {}, {}

# Build CHI Score list
i = 1
for k, v in dimension_list.items():
    term_chi = getCHIScore(k, cate_list, cate_doc_amount_list)
    if term_chi[0] != 0.0:
        avg_chi_dimension_list[k] = term_chi[0]
        max_chi_dimension_list[k] = term_chi[1]
    print "computing %d" % i
    i += 1

print "Average CHI Score list is %d" % len(avg_chi_dimension_list)
print "Max CHI Score list is %d" % len(max_chi_dimension_list)

'''
i = 1
for k, v in dimension_list.items():
    if i < 100:
        print k, v
        if verifyEngNum(k) == 0:
            print 'not-English and not-Number'
        elif verifyEngNum(k) == 1:
            print 'only number'
        elif verifyEngNum(k) == 2:
            print 'english Words'
        elif verifyEngNum(k) == 3:
            print 'not English words'
    else:
        break
    i += 1
'''

outfile = codecs.open('average_chi_list.txt', 'w', 'utf-8')
for k, v in avg_chi_dimension_list.items():
    outfile.write(k + ':' + str(v) + "\n")

outfile2 = codecs.open('max_chi_list.txt', 'w', 'utf-8')
for k, v in max_chi_dimension_list.items():
    outfile2.write(k + ':' + str(v) + "\n")

# close mysql database connection
conn.close()
