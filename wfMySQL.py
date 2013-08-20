#!/usr/bin/python
# -*- coding: utf-8 -*- #
# Copyright (c) 2012 Philip Matuskiewicz www.famousphil.com

#to include / use, insert the following lines in the code
#import imp;
#mysql = imp.load_source("MySQLConnector", "PATH_TO_PYTHON_FILE/mysql.py").MySQLConnector();
#result = mysql.tryquery("Mysql Query Here");

import sys
#import os
#import string
#import base64
import MySQLdb


#MySQL Singleton Class
class MySQLConnector(object):
    _connection = None
    _instance = None

    def __init__(self):
        try:
            if MySQLConnector._instance is None:
                MySQLConnector._instance = self
                MySQLConnector._instance.connect()
        except Exception, e:
            print "MySQL Error " + str(e)

    def instance(self):
        return MySQLConnector._instance

    def get_connection(self):
        return MySQLConnector._connection

    def connect(self, debug=False):
        try:
            for line in open('includes/db_config.py'):
                #this can be dangerous, but sources / executes lines in config.py, which contains the db info
                #alternatively, you can just set the variables here manually
                exec('%s = %s' % tuple(line.split('=', 1)))
            MySQLConnector._connection = MySQLdb.connect(dbhost, dblogin, dbpassword, dbname, dbcharset)
            if debug:
                print "INFO: Database connection successfully established"
        except Exception, e:
            print "ERROR: MySQL Connection Couldn't be created... Fatal Error! " + str(e)
            sys.exit()

    def disconnect(self):
        try:
            MySQLConnector._connection.close()
        except:
            #connection not open
            pass

    #returns escaped data for insertion into mysql
    def esc(self, esc):
        return MySQLdb.escape_string(str(esc))

    #query with no result returned
    def query(self, sql):
        cur = MySQLConnector._connection.cursor()
        return cur.execute(sql)

    def tryquery(self, sql):
        try:
            cur = MySQLConnector._connection.cursor()
            return cur.execute(sql)
        except:
            return False

    #inserts and returns the inserted row id (last row id in PHP version)
    def insert(self, sql):
        cur = MySQLConnector._connection.cursor()
        cur.execute(sql)
        return self._connection.insert_id()

    def tryinsert(self, sql):
        try:
            cur = MySQLConnector._connection.cursor()
            cur.execute(sql)
            return self._connection.insert_id()
        except:
            return -1

    #returns the first item of data
    def queryrow(self, sql):
        cur = MySQLConnector._connection.cursor()
        cur.execute(sql)
        return cur.fetchone()

    #returns a list of data (array)
    def queryrows(self, sql):
        cur = MySQLConnector._connection.cursor()
        cur.execute(sql)
        return cur.fetchmany()

#end class MySQLConnector
