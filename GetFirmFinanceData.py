#!/usr/bin/python
# -*- coding:utf8 -*-
from bs4 import BeautifulSoup
import requests
import time
from random import randint
import os
import re
import mysql_lib
from ConnectDB import DA
from NLog import Log
import json
from collections import namedtuple

def get_codes0(s):
    url = "http://210.242.68.58/axc/bin/assettable.php"
    r = s.get(url)
    #print(str(r.content))
    #j = json.loads(str(r.content))
    j = r.json()
    #print(j)
    return j[0]['r']

pcode='IFRSQABS_1000000','IFRSQABS_2000000','IFRSQABS_3100000','IFRSQABS_1010000','IFRSQABS_2010000','FINRQA_SRF001'+\
        'IFRSQABS_3010000','IFRSQABS_TSESPD_MKT_VALUE','IFRSQCIS_8000000','IFRSQCIS_A000000','IFRSQCIS_5000000'+\
        'IFRSQCIS_C010000','IFRSQCIS_C100000'

if __name__ == "__main__":
    strCommon = ','
    s = requests.Session()
    stringC=[]
    codes = get_codes0(s)
    for code0 in codes:
        ###code = code0[0]
        code = code0["c"]
        if len(code)!=4:
            continue
        if code in ['1339','1414','1423','1436','1438','1439','1452','1470','1516','1560','1584',
                    '1598','1713','1752','1776','1777','1808','2008','2009','2028','2032',
                    '2033','2065','2066','2235','2341','2381','2441','2455','2473','2493','2496','2524',
                    '2528','2534','2536','2537','2539','2633','2701','2706','2718','2722',
                    '2816','2820','2823','2832','2847','2850','2851','2852','2867','2897','2901',
                    '3069','3080','3087','3118','3152','3228','3599']:
            continue

        stringC.append(code)


    allPCode = strCommon.join(pcode)
    allCode = strCommon.join(stringC)
    url = "http://192.168.9.76/axc/bin/assetdata.php?c={myCode}&p={myPCode}&dm=" .format(myCode='1101',myPCode=allPCode)
    r = s.get(url).json()
    pass


