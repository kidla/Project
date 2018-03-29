import logging
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from configparser import SafeConfigParser
from os import path

class Log():

    @staticmethod
    def __createFolder():
        if os.path.isdir('logs') == False:
            os.mkdir('logs')
        
        t = time.strftime("%Y-%m-%d", time.localtime())
        return "logs/{}.log".format(t)
    
    @staticmethod
    def __setInit(logg, fn):
        logging.basicConfig(level=logg,format='[%(asctime)s] [%(name)-1s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S',filename=fn)

    @staticmethod
    def __setEmail(msg):
        dicConf={}
        parser = SafeConfigParser()
        appPath = path.join(path.dirname(path.dirname(__file__)), 'app.cfg')
        if path.exists(appPath):
            parser.read(appPath)
            dicConf['smtpServer'] = parser.get('Mail','smtpServer')
            dicConf['smtpPassword'] = parser.get('Mail','smtpPassword')
            dicConf['from'] = parser.get('Mail','from')
            dicConf['to'] = parser.get('Mail','to')
            if parser.get('Mail','isSent').lower() == 'true':
                receivers = dicConf['to']
                message = MIMEText('{}'.format(msg), 'plain', 'utf-8')
                message['From'] = Header(dicConf['from'])
                message['To'] =  Header(dicConf['to'], 'utf-8')
                
                subject = 'System Error'
                message['Subject'] = Header(subject, 'utf-8')

                server = smtplib.SMTP(dicConf['smtpServer'] )
                server.password = dicConf['smtpPassword']
                server.set_debuglevel(10)
                server.sendmail(dicConf['from'], receivers.split(','), message.as_string())
                server.quit()

    @staticmethod
    def Info(msg):
        Log.__setInit(logging.INFO,Log.__createFolder())
        logger = logging.getLogger("Info")
        logger.info(msg)


    @staticmethod
    def Debug(msg):
        Log.__setInit(logging.DEBUG,Log.__createFolder())
        logger = logging.getLogger("Debug")
        logger.debug(msg)
        Log.__setEmail(msg)

    @staticmethod
    def Warn(msg):
        Log.__setInit(logging.WARN,Log.__createFolder())
        logger = logging.getLogger("WARN")
        logger.warning(msg)
        Log.__setEmail(msg)
