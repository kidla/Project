# -*- coding: utf-8 -*-
import pypyodbc 
import sys
from configparser import SafeConfigParser
from os import path

def __getConnStr():
    parser = SafeConfigParser()
    appPath = path.join(path.dirname(path.dirname(__file__)), 'app.cfg')
    parser.read(appPath)

    t = parser.get('DBSetting','driver')   #SqlType
    s = parser.get('DBSetting','server')   #ServerIP
    d = parser.get('DBSetting','database') #DataBase
    u = parser.get('DBSetting','uid')      #login ID
    p = parser.get('DBSetting','pwd')      #login Pwd

    return ('Driver={};Server={};Database={};uid={};pwd={}').format(t,s,d,u,p)


def ExecuteSP(exeCmd,params):
    '''Return result for defining the data(execute command)'''
    connection = pypyodbc.connect(__getConnStr()) 
    cursor = connection.cursor() 
    
    cursor.execute(exeCmd,params)
    results = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()
    return results

def ExecuteQuery(sqlCmd, params):
    '''Return result for defining the data(query command)'''
    connection = pypyodbc.connect(__getConnStr()) 
    cursor = connection.cursor() 
    
    cursor.execute(sqlCmd,params)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

def QueryData(sqlStr, values=''):
    connection = pypyodbc.connect(__getConnStr()) 
    cursor = connection.cursor() 
    SQLCommand = (sqlStr)

    if(len(values)):
        cursor.execute(SQLCommand,values)
    else: cursor.execute(SQLCommand)
    
    results = cursor.fetchall() #fetchall回傳多筆
    cursor.close()
    connection.close()
    return results
def get_dbcursor():
    # Refer: http://www.runoob.com/python/python-mysql.html
    db =  pypyodbc.connect(__getConnStr())
    cursor = db.cursor()
    return db, cursor
