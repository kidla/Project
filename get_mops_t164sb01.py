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

def p(msg):
    print(msg)
    
def get_payload(code, year, season):
    payload = {'step':'1',
          'DEBUG':'',
          'CO_ID':code,
          'SYEAR':year,
          'SSEASON':season,
          'REPORT_ID':'C'}
    return payload

def get_data(s, code, year, season):
    print(code,year,season)
    if not os.path.exists("cache"):
        os.makedirs("cache")
    file = "cache/t164sb01-"+code+"-"+year+"-"+season+".txt"
    if os.path.isfile(file):
        f = open(file, "r", encoding="utf-8")
        c = f.read()
        f.close
        return c
    try:

        payload = get_payload(code, year, season)
        #print(payload)
        response = s.post(url,data=payload)
        response.encoding = 'utf-8'
        res = response.content
    except:
        Log.Warn("Except")
        print("Except!")
        time.sleep(60)
        return ""
    #print(res)
    print('.')
    time.sleep(randint(1,5))
    #time.sleep(randint(10,15))
    soup = BeautifulSoup(res, 'html5lib')            
    # 這個 table 僅作有無資料之測試
    table = soup.find("table", {'class':'result_table hasBorder'})
    if table is None:
        return ""
    #print(soup)
    tosave = str(soup.prettify())
    #print(tosave)
    f = open(file, "w", encoding="utf-8")
    f.write(tosave)
    f.close()
    print("[%d]\t" % (len(tosave)))
    return tosave

'''def get_table(s, url, payload):
    # use payload 
    response = s.post(url,data=payload)
    res = response.content
    time.sleep(randint(1,5))
    soup = BeautifulSoup(res, 'html.parser')
    table = soup.find("table", {'class':'result_table hasBorder'})
    return table'''

def get_value(soup, items, n):
    #print(soup)
    for item in items:
        print(item)
        #findtd = soup.find("td", text=re.compile(r'\s+'+item))
        findtda = soup.find_all("td", text=re.compile(r'\s+'+item))
        for findtd in findtda:
            if not findtd.text.strip()==item:
                continue
            #print(findtd.text)
            for i in range(1,n+1):
                #print(i,findtd.text)
                findtd = findtd.find_next_sibling("td")
            value = findtd.text.strip().replace(",", "")
            if value:
                return value
    return ""

def get_db_value(cursor, code, year, season, item):
    sql = "SELECT value FROM axc_assetdata WHERE code='%s' AND item='%s' AND datatime='%s%d'" % (code, item, year, season)
    cursor.execute(sql)
    results = cursor.fetchall()
    #print(results)
    if len(results)==0:
        return None
    return results[0][0]
    
def save_to_db(cursor, code, year, season, item, value):
    if get_db_value(cursor, code, year, season, item):
        return
    #財務報表上的數值都是(千元)單位，存到資料庫要先 *1000
    val1000 = float(value)*1000
    sql = "INSERT INTO axc_assetdata (code, item, datatime, value, lastupdate) VALUES ('%s','%s','%s%i', %s, NOW())" % (code, item, year, season, val1000)
    sql += " ON DUPLICATE KEY UPDATE value=%s" % (val1000)
    #print(sql)
    cursor.execute(sql)
    
#def get_comp_data(s, code):
    
def get_codes(cursor):
    sql = "SELECT code FROM axc_asset WHERE type_flag=0 AND status=1"
    cursor.execute(sql)
    results = cursor.fetchall()
    #print(results)
    return results

def get_codes0(s):
    url = "http://210.242.68.58/axc/bin/assettable.php"
    r = s.get(url)
    #print(str(r.content))
    #j = json.loads(str(r.content))
    j = r.json()
    #print(j)
    return j[0]['r']
    
'''def get_df(table):
    raws = table.find_all('table')[1].find_all('tr')
    # get the header 
    header = raws[0].find_all('th')
    header_of_table = [x.get_text() for x in header]
    # get the cell
    list_of_talbe=[]
    for raw in raws:
        r =  [x.get_text() for x in raw.find_all('td')]
        if len(r) > 0:
            list_of_talbe.append(r)
            
    df = pd.DataFrame(list_of_talbe,columns=header_of_table)
    return df'''

if __name__ == "__main__":
    lawFirm = 17722683
    valuedFirm = 35004143
    comboFirms = '11880517,14053007,51911712'
    values = (lawFirm, valuedFirm, comboFirms)
    # values = dict([('@lawFirm', 1), ('@valuedFirm', 2), ('@comboFirms', 3)])

    aa =    DA.ExecuteSP("execute USP_ValuedFirmSetting_Query  ?,  ? , ?", values)
    print("Begin",end='')
    db, cursor = DA.get_dbcursor()
    s = requests.Session()

    url = "http://mops.twse.com.tw/server-java/t164sb01"
    r = s.get(url)
    #print(r)
    soup = BeautifulSoup(r.content, 'html.parser')
    # get years
    years = [[x['value'],x.string] for x in soup.select('select[name="SYEAR"] > option')]
    #print(years)
    ###codes = get_codes(cursor)
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
        p("\n"+code+"----")
        for year in years:
        #year = ['2014','1']
            for i in range(1,5):
                #暫時不要處理 2017-3 以後的資料
                if int(year[0])*10+i >= 20173:
                    continue
                #檢查是否已經有資料，如果資料庫有資料，跳過這一筆
                #print("Check %s @ %s[%d]" % (code, year[0], i))
                p("%s[%d]\t" % (year[0], i))
                #有新的項目，先關掉這個
                #if not get_db_value(cursor, code, year[0], i, "IFRSQABS_5000000") is None:
                #    continue
                #資料庫無資料，開始更新
                res = get_data(s, code, year[0], str(i))
                if len(res)==0:
                    break
                if len(res)>0:
                    #print(res)
                    #parse 用 html.parser 比較快，用 html5lib 比較不會出錯
                    #soup = BeautifulSoup(res, 'html.parser')
                    soup = BeautifulSoup(res, 'html5lib')
                    table = soup.find("table", {'class':'result_table hasBorder'})
                    #print(table)
                    #'IFRSQABS_1000000', '總資產（合併）', 'F')
                    asset = get_value(table, ["資產總額", "資產總計"], 1)
                    print(asset)
                    save_to_db(cursor, code, year[0], i, 'IFRSQABS_1000000', asset)
                    #'IFRSQABS_2000000', '總負債（合併）', 'F'),
                    asset = get_value(table, ["負債總額", "負債總計"], 1)
                    print(asset)
                    save_to_db(cursor, code, year[0], i, 'IFRSQABS_2000000', asset)
                    #'IFRSQABS_3100000', '保留盈餘', 'F'),
                    asset = get_value(table, ["保留盈餘合計", "保留盈餘（或累積虧損）合計"], 1)
                    print(asset)
                    save_to_db(cursor, code, year[0], i, 'IFRSQABS_3100000', asset)
                    #'IFRSQABS_1010000', '流動資產（合併）', 'F'),
                    asset0 = get_value(table, ["流動資產合計"], 1)
                    print(asset0)
                    if asset0:
                        save_to_db(cursor, code, year[0], i, 'IFRSQABS_1010000', asset0)
                    #'IFRSQABS_2010000', '流動負債（合併）', 'F'),
                    asset1 = get_value(table, ["流動負債合計", "流動負債總額"], 1)
                    print(asset1)
                    if asset1:
                        save_to_db(cursor, code, year[0], i, 'IFRSQABS_2010000', asset1)
                    #營運資金從會計的角度看是指流動資產與流動負債的凈額。 Refer: http://wiki.mbalib.com/zh-tw/%E8%90%A5%E8%BF%90%E8%B5%84%E9%87%91
                    #營運資金 = FINRQA_SRF001
                    if asset0 and asset1:
                        asset = int(asset0) - int(asset1)
                        print(asset)
                        save_to_db(cursor, code, year[0], i, 'FINRQA_SRF001', asset)
                    #'IFRSQABS_3010000', '股本（合併）', 'F'),
                    asset = get_value(table, ["股本合計"], 1)
                    print(asset)
                    save_to_db(cursor, code, year[0], i, 'IFRSQABS_3010000', asset)
                    #為了計算市值，先取得該季最後一筆收盤價
                    sql = "SELECT vclose FROM axc_assetprice WHERE code='%s' and YEAR(pricetime)=%s and MONTH(pricetime)<=%d ORDER BY pricetime DESC LIMIT 1" % (code, year[0], i*3)
                    print(sql)
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    if len(results)>0:
                        price = float(results[0][0])
                        #'IFRSQABS_TSESPD_MKT_VALUE', '市值', 'F'),
                        mak_value = float(asset)/10*price
                        save_to_db(cursor, code, year[0], i, 'IFRSQABS_TSESPD_MKT_VALUE', str(mak_value))
                    #綜合損益表
                    #'IFRSQCIS_8000000', '合併季營業毛利', 'F'
                    asset = get_value(soup, ["營業毛利（毛損）"], 1)
                    print(asset)
                    save_to_db(cursor, code, year[0], i, 'IFRSQCIS_8000000', asset)
                    #'IFRSQCIS_A000000', '合併季營業利益', 'F'),
                    asset = get_value(soup, ["營業利益（損失）"], 1)
                    print(asset)
                    save_to_db(cursor, code, year[0], i, 'IFRSQCIS_A000000', asset)
                    #'IFRSQABS_5000000', '營業收入（合併）', 'F')
                    asset = get_value(soup, ["營業收入合計", "收入合計", "收益合計", "淨收益", "收益"], 1)
                    print(asset)
                    if code=='6497':
                        print(asset)
                        #print("Set "+code+" asset to 0")
                        asset="0"
                    save_to_db(cursor, code, year[0], i, 'IFRSQABS_5000000', asset)
                    save_to_db(cursor, code, year[0], i, 'IFRSQCIS_5000000', asset)
                    #現金流量表
                    #table = soup.find("table", {'class':'main_table hasBorder'})
                    #本期稅前淨利 = IFRSQCIS_C010000
                    asset = get_value(soup, ["本期稅前淨利（淨損）"], 1)
                    print(asset)
                    save_to_db(cursor, code, year[0], i, 'IFRSQCIS_C010000', asset)
                    #'IFRSQCIS_C100000', '合併季稅後淨利', 'F'),
                    asset = get_value(soup, ["本期淨利（淨損）"], 1)
                    print(asset)
                    save_to_db(cursor, code, year[0], i, 'IFRSQCIS_C100000', asset)
                    #'TSESPD_MKT_VALUE1', '總市值（元）'
                    #當期權益變動表
                    # 這個表格 <td></td> 亂擺，要換一個 parser
                    # soup = BeautifulSoup(res, 'html5lib')            
                    #table = soup.find("table", {'class':'result_table1 hasBorder'})
    db.close()
    print("Done.")

'''
typeks, codes = get_type_code(r)

print(r.ok)
if r.ok:
    print(typeks)
    for typek in typeks:
        print(typek)
        for code in codes: 
            try:
                payload = get_payload(typek[0], code[0])
                print(payload)
                table = get_table(s, url, payload)
                df = get_df(table)
                print(df)
            except:
                print('%s, %s faild' % (typek[1], code[1]))
            time.sleep(10)                

'''
