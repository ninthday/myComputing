#!/usr/bin/python
# -*- coding: utf-8 -*- #

"""vectorDimansion.py: This file is to compute dimansion in vector"""
__author__ = "Jeffy Shih (jeffy.sf@gmail.com)"
__email__ = "jeffy.sf@gmail.com"
__credits__ = ["Jeffy Shih"]
__copyright__ = "Copyright(c)Intelligent Media Laboratory, NCCU"
__versioni__ = "1.0.0"


class wfdb():
    def __init__(self):
        # Database Table Name list
        self.dblist = ('SegPingtungNSW', 'SegTainanNSW', 'SegRicksNSW', 'SegXditeCombineNSW', 'SegAdctNSW')

        # Database category and segment VIEW Name list
        self.viewlist = ('VIEW_CateTainan', 'VIEW_CatePingtung', 'VIEW_CateRicks', 'VIEW_CateXditeCombine', 'VIEW_CateAdct')

        # TFIDF Score and category View name list
        self.tfidf_viewlist = ('VIEW_CateTFIDFTainan', 'VIEW_CateTFIDFPingtung', 'VIEW_CateTFIDFRicks', 'VIEW_CateTFIDFXditeCombine', 'VIEW_CateTFIDFAdct')

        # Segment content and Date Time View name list
        self.segdate_viewlist = ('VIEW_SegDateTainan', 'VIEW_SegDatePingtung', 'VIEW_SegDateRicks', 'VIEW_SegDateXditeCombine', 'VIEW_SegDateAdct')

    def getTableList(self):
        return self.dblist

    def getViewList(self):
        return self.viewlist

    def getTFIDFViewList(self):
        return self.tfidf_viewlist

    def getSegDateViewList(self):
        return self.segdate_viewlist
