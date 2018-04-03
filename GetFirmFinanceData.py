#!/usr/bin/python
# -*- coding:utf8 -*-
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time
import os
import re
from random import randint
from ConnectDB import DA
from NLog import Log
import json
from FirmFinData import  FirmFinData
from FirmBaseData import  FirmBaseData

from collections import namedtuple

def get_codes0(s):
    url = "http://210.242.68.58/axc/bin/assettable.php"
    r = s.get(url)
    #print(str(r.content))
    #j = json.loads(str(r.content))
    j = r.json()
    #print(j)
    return j[0]['r']

def getJsonFromFile(fileName):
    if os.path.isfile(fileName):
        f = open(fileName, "r", encoding="utf-8")
        result = f.read()
        f.close
        return result

'''
IFRSQABS_1000000':'總資產, 'IFRSQABS_2000000':'總負債,    'IFRSQABS_3100000':'保留盈餘',
'IFRSQABS_1010000':'流動資產 ,IFRSQABS_2010000':'流動負債, FINRQA_SRF001: 營運資金 ,
 IFRSQCIS_8000000':'合併季營業毛利',IFRSQABS_5000000':'營業收入',IFRSQABS_3010000':'股本',
'IFRSQABS_TSESPD_MKT_VALUE':'市值',IFRSQABS_2010100:短期負債 ,IFRSQABS_2010510:商業本票
IFRSQABS_2010520:附買回債, IFRSQABS_2012552 :融劵存入保證金,IFRSQABS_2012558:應付融劵擔保價款
IFRSQABS_2150500 :長期負債,  IFRSQABS_3000000:股權淨值equity ,IFRSQCIS_A000000:營業利益
IFRSQCIS_C050000:所得稅費用 ,IFRSQCIS_7051000:利息費用,IFRSQCIS_C100000':合併季稅後淨利(NETPATAX)
IFRSQCIS_C010000:本期稅前淨利(NETPBTAX),IFRSQCIS_G050104:折舊,IFRSQCIS_G050105,攤銷
'''
pcode='IFRSQABS_1000000','IFRSQABS_2000000','IFRSQABS_3100000','IFRSQABS_1010000','IFRSQABS_2010000','FINRQA_SRF001',\
        'IFRSQCIS_8000000','IFRSQABS_5000000','IFRSQABS_3010000','IFRSQABS_TSESPD_MKT_VALUE','IFRSQABS_2010100',\
        'IFRSQABS_2010510','IFRSQABS_2010520','IFRSQABS_2012552','IFRSQABS_2012558','IFRSQABS_2150500',\
        'IFRSQABS_3000000','IFRSQCIS_A000000','IFRSQCIS_C050000','IFRSQCIS_7051000','IFRSQCIS_C100000',\
        'IFRSQCIS_C010000','IFRSQCIS_G050104','IFRSQCIS_G050105'

if __name__ == "__main__":
    tYear= datetime.today().year
    allDate=[str(year)+str(quater)  for year in range(2013,tYear) for quater in range(1,5)]
    strCommon = ','
    s = requests.Session()
    stringC=[]
    allPCode = strCommon.join(pcode)
    listedfile="baseListedData.json"
    unlistedflie="baseUnListedData.json"
    jsonListedText=getJsonFromFile(listedfile)
    jsonUnListedText=getJsonFromFile(unlistedflie)

    baseDataDict={}
    #baseURL = "https://quality.data.gov.tw/dq_download_json.php?nid=18419&md5_url=4932a781923479c4c782e8a07078d9e9"
    #baseJson= s.get(baseURL).json()
    baseListedJson=json.loads(jsonListedText)
    for baseDict in baseListedJson:
        firmBaseData=FirmBaseData(**baseDict)
        firmBaseData.islisted ="1"
        baseDataDict[firmBaseData.code]=firmBaseData
        pass
    baseUnListedJson = json.loads(jsonUnListedText)
    for baseDict in baseUnListedJson:
        firmBaseData = FirmBaseData(**baseDict)
        firmBaseData.islisted ="0"
        baseDataDict[firmBaseData.code] = firmBaseData
        pass
    codes = get_codes0(s)
    dbcon,cursor=DA.get_dbcursor()
    for code0 in codes:
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

        nameUrl = "http://210.242.68.58/axc/bin/signalextradata.php?c={myCode}&p=500".format(myCode=code)
        codeName = s.get(nameUrl).text.split(',')
        if (codeName[0] not in baseDataDict):
            continue
        print(code)
        firmBase = baseDataDict[codeName[0]]
        firmBase.seName = codeName[1]

        sqlCommand = "exec USP_FirmBaseData_Insert @CODE={fCode},@GUINUM={fNum},@COMPNAME='{firmName}',@SENAME='{seName}',@CATEGORY='{category}'," \
                     " @ADDRESS='{firmAddrs}',@ISLISTED='{listed}'" \
            .format (fCode=firmBase.code,fNum=firmBase.GUINUM,firmName=firmBase.fullname,seName=firmBase.seName,category=firmBase.category, firmAddrs=firmBase.address,listed=firmBaseData.islisted)

        cursor.execute(sqlCommand)
        dbcon.commit()
        print(sqlCommand)
        for ymq in allDate:
            url = "http://192.168.9.76/axc/bin/assetdata.php?c={myCode}&p={myPCode}&dm={myDate}".format(myCode=code,
                                                                                            myPCode=allPCode,myDate=ymq)

            r = s.get(url).text.replace(code + ',', '')
            jsonReturn = json.loads(r)
            jsonReturn['code'] = code
            jsonReturn['ymq']=ymq
            fData = FirmFinData(*jsonReturn, **jsonReturn)
            #guiNum =DA.ExecuteQuery('select GUINUM from Apex_UlspFirm where code={fcode}'.format(fcode=code),'')
            #if len(guiNum)==0:
             #   continue

            sqlCommand = "exec USP_FirmFinance_Insert @GUINUM={fNum},@CODE={fCode},@PBYEAR={year},@PBMONTH={month}," \
                         "@ISSUEDATE='{fDate}',@DATATYPE={type},@TOTASSET={TAsset},@TOTLIB={TLib}," \
                         "@RETAINEARNING={earning},@CURRENTASSET={CAsset},@CURRENTLIB={CLib},@WORKINGCAPITAL={Capital}," \
                         "@GROSSPROFIT={GProfit},@INCOME={income},@COMMONSTOCK={CStock},@CLOSEVALUE={CValue}," \
                         "@MKTVALUE={MValue},@SHORTLOAN={SLoan},@COMMERICAL={COMICAL},@REP_BOND={RBond}," \
                         "@M_DEPOSIT={MDespoit},@DPSF={DPSF},@LONGLOAN={LLoan},@EQUITY={equity},@PROFIT={profit}," \
                         "@TAXFEE={Tax},@INTERESTFEE={INT},@NETPATAX={NPATax},@NETPBTAX={NPBTax},@DEPRECIATION={Dep},"\
            "@AMORTIZATION={Amor}".format(fNum=firmBase.GUINUM,fCode=code,year=fData.year,month=fData.month,
                                          fDate=fData.issueDate,type=fData.quater,TAsset=fData.totAsset,TLib=fData.totLib,
                                          earning=fData.retainEarning,CAsset=fData.currentAsset,CLib=fData.currentLib,
                                          Capital=fData.workCapital,GProfit=fData.grossProfit,income=fData.income,
                                          CStock=fData.commStock,CValue=fData.closeValue,MValue=fData.mktValue,
                                          SLoan=fData.shortDebit,COMICAL=fData.commerical,RBond=fData.rBond,MDespoit=fData.deposit,
                                          DPSF=fData.dpsf,LLoan=fData.longloan,equity=fData.equity,profit=fData.profit,
                                          Tax=fData.taxfee,INT=fData.interest,NPATax=fData.NETPATax,NPBTax=fData.NETPBTax,
                                          Dep=fData.depreciation,Amor=fData.amor)
            #print(sqlCommand)
            cursor.execute(sqlCommand)
            dbcon.commit()
            pass


    dbcon.close()
    print ('end')










    pass


