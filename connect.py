import requests, json
from db import MongoDb
mongo = MongoDb()
import pandas as pd

import datetime
from des import double_exponential_smoothing
from tes import triple_exponential_smoothing
from datetime import timedelta

class Upstox:
    def __init__(self):
        self.BASE_URL = 'https://api-v2.upstox.com'
        self.CODE = '2lxzav'
        self.API_KEY = 'a33d9f29-4518-4b91-8a0f-2dc149061507'
        self.API_SECRET = '0rftxdw8by'
        self.REDIRECT_URI = 'http://127.0.0.1'
        self.ALPHA = 0.9

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

    def backTestClose(self, collection, start, end, cnt):
        data = mongo.readAll(collection, start, end)
        collection = collection+'_Close'
        if len(data) > 0:
            prev = data[0]
            prev_direction = ''
            first = True
            i = 2
            for d in data[1:]:
                if i < len(data):
                    next = data[i]
                if prev['close'] > d['close']:
                    direction = 'DOWN'
                else:
                    direction = 'UP'
                #next.pop("_id")
                d['next_date'] = next['date']
                d['next_open'] = next['open']
                d['next_high'] = next['high']
                d['next_low'] = next['low']
                d['next_close'] = next['close']
                if first:
                    prev_direction = direction
                    first = False
                    self.buyOrSellStock(d, direction, 'BUY', collection, cnt)
                if direction != prev_direction:
                    self.buyOrSellStock(d, prev_direction, 'SELL', collection, cnt)
                    cnt += 1
                    self.buyOrSellStock(d, direction, 'BUY', collection, cnt)
                cnt += 1
                i += 1
                prev_direction = direction
                prev = d
            self.buyOrSellStock(d, direction, 'SELL', collection, cnt)
            cnt += 1
        return cnt
    
    def getMovingAveragePred(self, data, alpha_final, beta_final, gamma_final):
        df_data = {"date": [], "open": [], "high": [], "low": [], "close": [], "ema_open": [], "ema_close": []}
        for d in data:
            df_data["date"].append(d["date"])
            df_data["open"].append(d["open"])
            df_data["high"].append(d["high"])
            df_data["low"].append(d["low"])
            df_data["close"].append(d["close"])
            df_data["ema_open"].append(d["ema_open"])
            df_data["ema_close"].append(d["ema_close"])
        df = pd.DataFrame(df_data)
        rolling = 3
        t3 = triple_exponential_smoothing(df['close'], alpha_final, beta_final, gamma_final)
        df['tes_close'] = pd.Series(t3[:len(df['close'])])
        df['des_close_p1'] = double_exponential_smoothing(df['close'], 0.9, 0.1, 1)[:-1]
        df['des_close_p9'] = double_exponential_smoothing(df['close'], 0.9, 0.9, 1)[:-1]
        df['des_close_p9_ma3'] = df['des_close_p9'].rolling(rolling).mean()
        
        df['ema_close_ma3'] = df['ema_close'].rolling(rolling).mean()
        df['tes_close_ma3'] = df['tes_close'].rolling(rolling).mean()
        res = []
        for i in range(len(df)):
            result = {"date": df["date"][i], "open": df["open"][i], "high": df["high"][i], "low": df["low"][i], "close": df["close"][i], "ema_open": df["ema_open"][i], "ema_close": df["ema_close"][i],
            "ema_close_ma3": df["ema_close_ma3"][i] if i >= rolling else df["ema_close"][i],
            "des_close_p9_ma3": df["des_close_p9_ma3"][i] if i >= rolling else df["des_close_p9"][i],
            "des_close_p1": df["des_close_p1"][i], "des_close_p9": df["des_close_p9"][i], "tes_close": df["tes_close"][i],
            "tes_close_ma3": df["tes_close_ma3"][i] if i >= rolling else df["tes_close"][i]}
            res.append(result)
        pass
        return res
    
    def getMovingAverage(self, data, alpha_final, beta_final, gamma_final):
        df_data = {"date": [], "open": [], "high": [], "low": [], "close": [], "ema_open": [], "ema_close": []}
        for d in data:
            df_data["date"].append(d["date"])
            df_data["open"].append(d["open"])
            df_data["high"].append(d["high"])
            df_data["low"].append(d["low"])
            df_data["close"].append(d["close"])
            df_data["ema_open"].append(d["ema_open"])
            df_data["ema_close"].append(d["ema_close"])
        df = pd.DataFrame(df_data)
        rolling = 3
        t3 = triple_exponential_smoothing(df['close'], alpha_final, beta_final, gamma_final)
        df['tes_close'] = pd.Series(t3[:len(df['close'])])
        df['des_close_p1'] = double_exponential_smoothing(df['close'], 0.9, 0.1, 1)[:-1]
        df['des_close_p9'] = double_exponential_smoothing(df['close'], 0.9, 0.9, 1)[:-1]
        df['des_close_p9_ma3'] = df['des_close_p9'].rolling(rolling).mean()
        
        df['ema_close_ma3'] = df['ema_close'].rolling(rolling).mean()
        df['tes_close_ma3'] = df['tes_close'].rolling(rolling).mean()
        res = []
        for i in range(len(df)):
            result = {"date": df["date"][i], "open": df["open"][i], "high": df["high"][i], "low": df["low"][i], "close": df["close"][i], "ema_open": df["ema_open"][i], "ema_close": df["ema_close"][i],
            "ema_close_ma3": df["ema_close_ma3"][i] if i >= rolling else df["ema_close"][i],
            "des_close_p9_ma3": df["des_close_p9_ma3"][i] if i >= rolling else df["des_close_p9"][i],
            "des_close_p1": df["des_close_p1"][i], "des_close_p9": df["des_close_p9"][i], "tes_close": df["tes_close"][i],
            "tes_close_ma3": df["tes_close_ma3"][i] if i >= rolling else df["tes_close"][i]}
            res.append(result)
        pass
        return res
    
    def getMovingAverage5min(self, data):
        df_data = {"date": [], "open": [], "close": []}
        for d in data:
            df_data["date"].append(d["date"])
            df_data["open"].append(d["open"])
            df_data["close"].append(d["close"])
        df = pd.DataFrame(df_data)
        rolling = 3
        df['ema_close'] = df['close'].ewm(alpha=0.9).mean()
        df['ema_close_ma3'] = df['ema_close'].rolling(rolling).mean()
        res = []
        for i in range(len(df)):
            result = {"date": df["date"][i], "open": df["open"][i], "close": df["close"][i], "ema_close": df["ema_close"][i], "ema_close_ma3": df["ema_close_ma3"][i] if i >= rolling else df["ema_close"][i]}
            res.append(result)
        pass
        return res
    
    def getLastBuy(self, collection, start, end):
        data = mongo.descending(collection, start, end, "date")
        return data
    
    def getDirection(self, d, prev, original=False):
        if original:
            if prev['close'] > d['close']:
            #if prev['close'] > d['close']:
                direction = 'DOWN'
            else:
                direction = 'UP'
        else:
            if prev['ema_close_ma3'] > d['ema_close_ma3']:
            #if prev['close'] > d['close']:
                direction = 'DOWN'
            else:
                direction = 'UP'
        return direction
    
    def backTestPred(self, collection, start, end, limit, alpha_final, beta_final, gamma_final):
        #start = datetime.datetime(2023, 1, 2)
        #end = datetime.datetime(2023, 1, 3)    
        data2 = []
        previous_day = start
        while len(data2) == 0:    
            previous_day_end = previous_day
            previous_day = previous_day - timedelta(days=1)            
            data2 = mongo.readAll(collection, previous_day, previous_day_end)

        data1 = mongo.readAll(collection, start, end)
        
        #collection += 'MA10'
        if len(data1) > 0:
            prev_direction = ''
            first = True
            tot_pl = 0
            for i in range(len(data1)):                
                data3 = self.getMovingAveragePred(data2+data1[:i+1], alpha_final, beta_final, gamma_final)
                prev = data3[len(data2)+i - 1]
                d = data3[len(data2)+i]
                # if i < len(data):
                #     next = data[i]
                #if prev['ema_close_ma3'] > d['ema_close_ma3']:
                #if prev['des_close_p9'] > d['des_close_p9']:                    
                if prev['tes_close'] > d['tes_close']:
                #if prev['tes_close_ma3'] > d['tes_close_ma3']:                    
                #if prev['close'] > d['close']:
                    direction = 'DOWN'
                else:
                    direction = 'UP'
                #next.pop("_id")
                # d['next_date'] = next['date']
                # d['next_open'] = next['open']
                # d['next_high'] = next['high']
                # d['next_low'] = next['low']
                # d['next_close'] = next['close']
                # d['next_ema_close_ma3'] = next['ema_close_ma3']
                if first:
                    prev_direction = direction
                    first = False
                    self.buyOrSellStock(d, direction, 'BUY', collection)
                    prev_buy = d
                if prev_buy['direction'] == 'UP':
                    future_pl = d['close'] - prev_buy['close']
                if prev_buy['direction'] == 'DOWN':
                    future_pl = prev_buy['close'] - d['close']
                if direction != prev_direction:
                    dif = d['date'] - prev_buy['date']
                    min = dif.total_seconds()/60
                    #last_buy = self.getLastBuy('transactions_'+collection, start, end)
                    
                    
                    
                    if min > 0 and (future_pl > 0 or future_pl < -99):  
                    #if min > 0 and (future_pl > 0):  
                    #if min > 0:  
                        tot_pl += future_pl                      
                        self.buyOrSellStock(d, prev_direction, 'SELL', collection)
                        prev_direction = direction
                        self.buyOrSellStock(d, direction, 'BUY', collection)
                        prev_buy = d
                    if tot_pl < -49:
                        direction = prev_direction
                        break
                else:
                    if (future_pl > 20 or future_pl < -20):  
                        tot_pl += future_pl                      
                        self.buyOrSellStock(d, prev_direction, 'SELL', collection)
                        prev_direction = direction
                        if future_pl < -20:
                            if direction == 'UP':
                                direction = 'DOWN'
                            else:
                                direction = 'UP'
                        self.buyOrSellStock(d, direction, 'BUY', collection)
                        prev_buy = d
                #cnt += 1
                i += 1
                #prev_direction = direction
                prev = d
            self.buyOrSellStock(d, direction, 'SELL', collection)
        return limit
    
    def backTest(self, collection, start, end, limit, alpha_final, beta_final, gamma_final):
        #start = datetime.datetime(2023, 1, 2)
        #end = datetime.datetime(2023, 1, 3)        
        
        data = mongo.readAll(collection, start, end)
        #collection += 'MA10'
        if len(data) > 0:
            data = self.getMovingAverage(data, alpha_final, beta_final, gamma_final)
            prev = data[0]
            prev_direction = ''
            first = True
            i = 2
            tot_pl = 0
            for d in data[1:]:
                # if i < len(data):
                #     next = data[i]
                #if prev['ema_close_ma3'] > d['ema_close_ma3']:
                #if prev['des_close_p9'] > d['des_close_p9']:                    
                if prev['tes_close'] > d['tes_close']:
                #if prev['tes_close_ma3'] > d['tes_close_ma3']:                    
                #if prev['close'] > d['close']:
                    direction = 'DOWN'
                else:
                    direction = 'UP'
                #next.pop("_id")
                # d['next_date'] = next['date']
                # d['next_open'] = next['open']
                # d['next_high'] = next['high']
                # d['next_low'] = next['low']
                # d['next_close'] = next['close']
                # d['next_ema_close_ma3'] = next['ema_close_ma3']
                if first:
                    prev_direction = direction
                    first = False
                    self.buyOrSellStock(d, direction, 'BUY', collection)
                    prev_buy = d
                if direction != prev_direction:
                    dif = d['date'] - prev_buy['date']
                    min = dif.total_seconds()/60
                    #last_buy = self.getLastBuy('transactions_'+collection, start, end)
                    if prev_buy['direction'] == 'UP':
                        future_pl = d['close'] - prev_buy['close']
                    if prev_buy['direction'] == 'DOWN':
                        future_pl = prev_buy['close'] - d['close']
                    
                    
                    if min > 0 and (future_pl > 0 or future_pl < -99):  
                    #if min > 0 and (future_pl > 0):  
                    #if min > 0:  
                        tot_pl += future_pl                      
                        self.buyOrSellStock(d, prev_direction, 'SELL', collection)
                        prev_direction = direction
                        self.buyOrSellStock(d, direction, 'BUY', collection)
                        prev_buy = d
                    if tot_pl < -49:
                        direction = prev_direction
                        break
                #cnt += 1
                i += 1
                #prev_direction = direction
                prev = d
            self.buyOrSellStock(d, direction, 'SELL', collection)
        return limit


    def backTest2(self, collection, start, end, limit):
        #start = datetime.datetime(2023, 1, 2)
        #end = datetime.datetime(2023, 1, 3)
        data = mongo.readAll(collection, start, end)
        #collection += 'MA10'
        if len(data) > 0:
            data = self.getMovingAverage(data)
            prev = data[0]
            prev_direction = ''
            first = True
            i = 2
            tot_pl = 0
            step = 5
            step_break = False
            neg_cnt = 0
            neg_accu = 0
            for idx in range(1,len(data)):
                d = data[idx]
                # if i < len(data):
                #     next = data[i]
                direction = self.getDirection(d, prev, True)
                # if prev['ema_close_ma3'] > d['ema_close_ma3']:
                # #if prev['close'] > d['close']:
                #     direction = 'DOWN'
                # else:
                #     direction = 'UP'
                #next.pop("_id")
                # d['next_date'] = next['date']
                # d['next_open'] = next['open']
                # d['next_high'] = next['high']
                # d['next_low'] = next['low']
                # d['next_close'] = next['close']
                # d['next_ema_close_ma3'] = next['ema_close_ma3']
                if first:
                    prev_direction = direction
                    first = False
                    self.buyOrSellStock(d, direction, 'BUY', collection)
                    prev_buy = d
                if direction != prev_direction:
                    dif = d['date'] - prev_buy['date']
                    min = dif.total_seconds()/60
                    #last_buy = self.getLastBuy('transactions_'+collection, start, end)
                    if prev_buy['direction'] == 'UP':
                        future_pl = d['close'] - prev_buy['close']
                    if prev_buy['direction'] == 'DOWN':
                        future_pl = prev_buy['close'] - d['close']
                    
                    neg_limit = -30
                    
                    if min > 0 and (future_pl > 100 or future_pl < neg_limit):
                        if future_pl < neg_limit:
                            neg_cnt += 1
                            neg_accu += future_pl
                        else:
                            neg_cnt = 0
                    #if min > 1 and (future_pl > 0 or future_pl < -49):  
                        tot_pl += future_pl                      
                        self.buyOrSellStock(d, prev_direction, 'SELL', collection)
                        idx += step
                        if neg_cnt >= 2:
                            idx += 2 * step
                            neg_cnt = 0
                        # if neg_cnt >= 3:
                        #     idx += 2 * step
                        #     if neg_accu < -75:
                        #         step_break = True
                        #         break
                        #     neg_cnt = 0
                        if idx >= len(data):
                            step_break = True
                            break
                        d = data[idx]
                        direction = self.getDirection(d, data[idx-1], True)
                        prev_direction = direction
                        self.buyOrSellStock(d, direction, 'BUY', collection)
                        prev_buy = d
                    # if tot_pl < -49:
                    #     direction = prev_direction
                    #     break
                #cnt += 1
                i += 1
                #prev_direction = direction
                prev = d
            if not step_break:
                self.buyOrSellStock(d, direction, 'SELL', collection)
        return limit


    def backTest5min(self, collection, start, end, limit):
        #start = datetime.datetime(2023, 1, 2)
        #end = datetime.datetime(2023, 1, 3)
        data = mongo.readAll(collection, start, end)
        #collection += 'MA10'
        if len(data) > 0:
            data = self.getMovingAverage5min(data)
            prev = data[0]
            prev_direction = ''
            first = True
            i = 2
            tot_pl = 0
            for d in data[1:]:
                # if i < len(data):
                #     next = data[i]
                if prev['ema_close_ma3'] > d['ema_close_ma3']:
                #if prev['close'] > d['close']:
                    direction = 'DOWN'
                else:
                    direction = 'UP'
                #next.pop("_id")
                # d['next_date'] = next['date']
                # d['next_open'] = next['open']
                # d['next_high'] = next['high']
                # d['next_low'] = next['low']
                # d['next_close'] = next['close']
                # d['next_ema_close_ma3'] = next['ema_close_ma3']
                if first:
                    prev_direction = direction
                    first = False
                    self.buyOrSellStock(d, direction, 'BUY', collection)
                    prev_buy = d
                if direction != prev_direction:
                    dif = d['date'] - prev_buy['date']
                    min = dif.total_seconds()/60
                    #last_buy = self.getLastBuy('transactions_'+collection, start, end)
                    if prev_buy['direction'] == 'UP':
                        future_pl = d['close'] - prev_buy['close']
                    if prev_buy['direction'] == 'DOWN':
                        future_pl = prev_buy['close'] - d['close']
                    
                    
                    if min > 0 and (future_pl > 0 or future_pl < -99):  
                        tot_pl += future_pl                      
                        self.buyOrSellStock(d, prev_direction, 'SELL', collection)
                        prev_direction = direction
                        self.buyOrSellStock(d, direction, 'BUY', collection)
                        prev_buy = d
                    if tot_pl < -49:
                        direction = prev_direction
                        break
                #cnt += 1
                i += 1
                #prev_direction = direction
                prev = d
            self.buyOrSellStock(d, direction, 'SELL', collection)
        return limit

    def buyOrSellStock(self, data, direction, type, collection):
        data['direction'] = direction
        data['type'] = type
        if "_id" in data:
            data.pop("_id")
        mongo.insertMany('tnx_'+collection, [data])
        pass

    def getProfitOrLoss(self, collection, start, end, strip):
        #start = datetime.datetime(2023, 1, 2)
        #end = datetime.datetime(2023, 1, 3)
        data = mongo.readAll(collection, start, end)
        points = 0
        no_trx = len(data)/2
        p_l = {"p": 0, "l": 0}
        diff = []
        for i in range(0, len(data), 2):
            if((i+1) < len(data)):
                buy = data[i]
                sell = data[i+1]
                direction = buy['direction']
                addition = 0
                if direction == 'UP':
                    addition = sell['close'] - buy['close']
                else:
                    addition = buy['close'] - sell['close']
                dif = sell['date'] - buy['date']
                #print(addition, " addition")
                min = dif.total_seconds()/60
                diff.append(min)

                points += addition
                print(addition, " addition", min, buy['date'], sell['date'], direction)
                if addition > 0:
                    p_l["p"] += 1
                elif addition < 0:
                    p_l["l"] += 1
                # if points < strip:
                #     break
                #print(i)
        print(points, " points ", no_trx, p_l, start)
        return points
    
    def insertProfitOrLoss(self, data):
        if len(data["profit"]) > 0:
            mongo.insertMany('profit_or_loss', data["profit"])
        if len(data["loss"]) > 0:
            mongo.insertMany('profit_or_loss', data["loss"])

    def createDataFrame(self):
        start = datetime.datetime(2011, 10, 17)
        end = datetime.datetime(2023, 4, 28)
        data = mongo.readAll("nseindexniftybankDay", start, end)
        df_data = {"date": [], "open": [], "high": [], "low": [], "close": []}
        for d in data:
            df_data["date"].append(d["date"])
            df_data["open"].append(d["open"])
            df_data["high"].append(d["high"])
            df_data["low"].append(d["low"])
            df_data["close"].append(d["close"])
        df = pd.DataFrame(df_data)
        df.to_csv("out_day.csv")
        pass

    def get5minticks(self, collection, start, end):
        data = mongo.readAll(collection, start, end)
        d = []
        for i in range(0, len(data), 5):
            close = data[i+4]['close'] if i + 4 < len(data) else data[len(data) - 1]['close']
            di = {"open": data[i]['open'], 'date': data[i]['date'], 'close': close}
            d.append(di)
        if len(d) > 0:
            mongo.insertMany(collection+'_5min', d)
        pass


