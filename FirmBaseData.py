class FirmBaseData(object):
    seName=''
    islisted=''
    def __init__(self, *args, **dictArgs):
        self.code=dictArgs['公司代號']
        self.fullname=dictArgs['公司名稱']
        self.GUINUM=dictArgs['營利事業統一編號']
        self.address=dictArgs['住址']
        self.category=dictArgs['產業別']
