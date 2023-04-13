import requests, json
from db import MongoDb
mongo = MongoDb()
import pandas as pd

import datetime

class Upstox:
    def __init__(self):
        self.BASE_URL = 'https://api-v2.upstox.com'
        self.CODE = 'xiUrks'
        self.API_KEY = 'a33d9f29-4518-4b91-8a0f-2dc149061507'
        self.API_SECRET = '0rftxdw8by'
        self.REDIRECT_URI = 'http://127.0.0.1'
        self.ALPHA = 0.1

        pass

    def readAccessToken(self):
        f = open("access_token.txt", "r")
        return f.read().strip()

    def getAccessToken(self):
        url = self.BASE_URL + '/login/authorization/token'
        payload = {'code': self.CODE, 'client_id': self.API_KEY, 'client_secret': self.API_SECRET, 'redirect_uri': self.REDIRECT_URI, 'grant_type': 'authorization_code'}
        req = requests.post(url, payload, headers = {"accept": "application/json", "Api-Version": "2.0", "Content-Type": "application/x-www-form-urlencoded"})
        json_object = json.loads(req.text)
        f = open("access_token.txt", "a")
        f.write(json_object['access_token'])
        f.close()
        print(req.text)

    def getRequest(self, url, payload):
        req = requests.get(url, payload, headers = {"accept": "application/json", "Api-Version": "2.0", "Content-Type": "application/json", "Authorization": "Bearer "+ self.readAccessToken()})
        json_object = json.loads(req.text)
        return json_object
    
    def postRequest(self, url, payload):
        req = requests.post(url, payload, headers = {"accept": "application/json", "Api-Version": "2.0", "Content-Type": "application/json", "Authorization": "Bearer "+ self.readAccessToken()})
        json_object = json.loads(req.text)
        return json_object
    
    def placeOrder(self):
        url = self.BASE_URL + '/order/place'
        payload = {
            "quantity": 1,
            "product": "D",
            "validity": "DAY",
            "price": 0,
            "tag": "string",
            "instrument_token": "NSE_EQ|INE848E01016",
            "order_type": "MARKET",
            "transaction_type": "BUY",
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }
        data = self.postRequest(url, payload)
        print(data)
        pass

    def getUserProfile(self):
        url = self.BASE_URL + '/user/profile'
        payload = {}
        data = self.getRequest(url, payload)
        pass

    def getUserFundsAndMargin(self):
        url = self.BASE_URL + '/user/get-funds-and-margin'
        payload = {}
        data = self.getRequest(url, payload)
        pass

    def getPositions(self):
        url = self.BASE_URL + '/portfolio/short-term-positions'
        payload = {}
        data = self.getRequest(url, payload)
        pass

    def getHoldings(self):
        url = self.BASE_URL + '/portfolio/long-term-holdings'
        payload = {}
        data = self.getRequest(url, payload)
        pass

    def insertToDb(self, data, collection):
        candles = data['data']['candles']
        d = []
        i = -1
        for candle in candles[::-1]:
            val = {}
            dt = datetime.datetime.strptime(candle[0], "%Y-%m-%dT%H:%M:%S+05:30")
            val['date'] = dt
            val['open'] = candle[1]
            val['high'] = candle[2]
            val['low'] = candle[3]
            val['close'] = candle[4]
            
            ema_open = val['open'] if i == -1 else (self.ALPHA * val['open']) + (1 - self.ALPHA) * prev['ema_open']
            val['ema_open'] = ema_open
            ema_close = val['close'] if i == -1 else (self.ALPHA * val['close']) + (1 - self.ALPHA) * prev['ema_close']
            val['ema_close'] = ema_close
            prev = val
            d.append(val)
            i += 1
        mongo.insertMany(collection, d)
        pass

    def historicalCandleData(self, collection, instrument_key, interval, to_date, from_date):
        url = self.BASE_URL + '/historical-candle/'+instrument_key+'/'+interval+'/'+to_date+'/'+from_date
        payload = {}
        data = self.getRequest(url, payload)    

        self.insertToDb(data, collection)  
        #self.saveToExcel(data)        
        
        pass

    def getDf(self, collection, start, end):
        data = mongo.readAll(collection, start, end)
        df_data = {"date": [], "open": [], "close": [], "ema_open": [], "ema_close": []}
        for d in data:
            df_data["date"].append(str(d["date"]))
            df_data["open"].append(d["open"])
            df_data["close"].append(d["close"])
            df_data["ema_open"].append(d["ema_open"])
            df_data["ema_close"].append(d["ema_close"])
        df = pd.DataFrame(df_data)
        return df

    def getAllCandleData(self, collection):
        df = self.getDf(collection)
        self.saveToExcel(df)
        pass

    def getDfData(self, collection, start, end):
        df = self.getDf(collection, start, end)
        return df

    def saveToExcel(self, df):

        df.to_excel(r'nifty50.xlsx', sheet_name='Your sheet name', index=False)

        pass
