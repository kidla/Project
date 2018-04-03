'''
照這順序
IFRSQABS_1000000':'總資產, 'IFRSQABS_2000000':'總負債,    'IFRSQABS_3100000':'保留盈餘',
'IFRSQABS_1010000':'流動資產 ,IFRSQABS_2010000':'流動負債, FINRQA_SRF001: 營運資金 ,
 IFRSQCIS_8000000':'合併季營業毛利',IFRSQABS_5000000':'營業收入',IFRSQABS_3010000':'股本',
'IFRSQABS_TSESPD_MKT_VALUE':'市值',IFRSQABS_2010100:短期負債 ,IFRSQABS_2010510:商業本票
IFRSQABS_2010520:附買回債, IFRSQABS_2012552 :融劵存入保證金,IFRSQABS_2012558:應付融劵擔保價款
IFRSQABS_2150500 :長期負債,  IFRSQABS_3000000:股權淨值equity ,IFRSQCIS_A000000:營業利益
IFRSQCIS_C050000:所得稅費用 ,IFRSQCIS_7051000:利息費用,IFRSQCIS_C100000':合併季稅後淨利(NETPATAX)
IFRSQCIS_C010000:本期稅前淨利(NETPBTAX),IFRSQCIS_G050104:折舊,IFRSQCIS_G050105,攤銷
'''
import calendar


class FirmFinData(object):
    #TODO   date處理
    def __init__(self,*args,**dictArgs):
        for key,value in dictArgs.items():
            if value == None:
                dictArgs[key]=0

        self.code=dictArgs['code']
        self.ymq=dictArgs['ymq']
        self.totAsset = dictArgs[args[0]]
        self.totLib=  dictArgs[args[1]]
        self.retainEarning = dictArgs[args[2]]
        self.currentAsset = dictArgs[args[3]]
        self.currentLib= dictArgs[args[4]]
        self.workCapital=dictArgs[args[5]]
        self.grossProfit = dictArgs[args[6]]
        self.income = dictArgs[args[7]]
        self.commStock =dictArgs[args[8]]
        self.mktValue =dictArgs[args[9]]
        self.closeValue = 0
        if self.commStock!=0:
            self.closeValue= (float(self.mktValue)/float(self.commStock))/10
        self.shortDebit=dictArgs[args[10]]
        self.commerical=dictArgs[args[11]]
        self.rBond=dictArgs[args[12]]
        self.deposit=dictArgs[args[13]]
        self.dpsf=dictArgs[args[14]]
        self.longloan=dictArgs[args[15]]
        self.equity=dictArgs[args[16]]
        self.profit=dictArgs[args[17]]
        self.taxfee=dictArgs[args[18]]
        self.interest=dictArgs[args[19]]
        self.NETPATax=dictArgs[args[20]]
        self.NETPBTax=dictArgs[args[21]]
        self.depreciation=dictArgs[args[22]]
        self.amor=dictArgs[args[23]]
        self.year = int(self.ymq[:4])
        self.month = int(self.ymq[4:])*3
        self.quater = 'Q'+self.ymq[4:] #將來要修正 看月報季報
        _monthRange = calendar.monthrange(self.year, self.month)
        self.issueDate=str(self.year) +'-'+str(self.month)+'-'+str(_monthRange[1])
        pass





