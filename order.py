from db import MongoDb
mongo = MongoDb()
import pandas as pd
from datetime import datetime, timedelta
from time import sleep
from connect import Upstox

class Order:
    def __init__(self):
        pass

    def checkLatestTick(self, collection, start, end):
        
        data = mongo.readTickData(collection, start, end)
        return data

    def getData(self, collection):
        today = datetime.today()
        daystart = datetime(year=today.year, month=today.month, 
                    day=today.day, hour=0, minute=0, second=0) 

        start = daystart
        end = start + timedelta(days=1)
        alpha = 0.9
        rolling = 3
        data = self.checkLatestTick(collection, start, end)
        data = data[:-1]
        processed_data = self.processData(data, alpha, rolling)
        
        while True:
            new_data = self.checkLatestTick(collection, start, end) 
                       
            print("new check")            
            if len(new_data) > len(data):
                processed_data = self.processNewData(processed_data, new_data, alpha, rolling)
                if len(new_data) > 3:
                    self.trade(processed_data, collection, start, end, new_data[0])
                data = new_data
                print("new data received")
                sleep(30)
            sleep(1)

    def buyStock(self, latest_data, direction, collection):
        u = Upstox()
        u.buyOrSellStock(latest_data, direction, 'BUY', collection)
        pass  

    def sellStock(self, latest_data, direction, collection):
        u = Upstox()
        u.buyOrSellStock(latest_data, direction, 'SELL', collection)
        pass  


    def trade(self, processed_data, collection, start, end, latest_data):
        direction = self.getDirection(processed_data)
        data = mongo.readLatestTnx(collection, start, end)
        today = datetime.today()
        dayend = datetime(year=today.year, month=today.month, 
                    day=today.day, hour=15, minute=25, second=0)
        if len(data) > 0:
            prev_tnx = data[0]
            if self.prev_tnx and self.prev_tnx == 'SELL':
                self.buyStock(latest_data, direction, collection) 
                self.prev_tnx = 'BUY'
            else:
                if direction != prev_tnx['direction']:
                    self.sellStock(latest_data, prev_tnx['direction'], collection)
                    self.prev_tnx = 'SELL'                 
                if latest_data["ts"]  > dayend:     
                    self.sellStock(latest_data, prev_tnx['direction'], collection)  
                    self.prev_tnx = 'SELL'                          
        else:
            if latest_data["ts"] < dayend:
                self.buyStock(latest_data, direction, collection)  
                self.prev_tnx = 'BUY'        
        
        pass

    def getDirection(self, processed_data):
        cur = processed_data['ema_close_ma'][len(processed_data) - 1]
        prev = processed_data['ema_close_ma'][len(processed_data) - 2]
        if prev > cur:
            direction = 'DOWN'
        else:
            direction = 'UP'
        pass
        return direction

    def processNewData(self, processed_data, data, alpha, rolling):
        new_data = data[0]
        ema_close = (alpha * new_data['close']) + ((1-alpha) * processed_data['ema_close'][len(processed_data)-1])
        sum = ema_close
        for i in range(1, rolling):
            sum += processed_data['ema_close'][len(processed_data)-i]
        ema_close_ma = sum / rolling
        data_df2 = {'date': [new_data["ts"]], 'open': [new_data['open']], 'high': [new_data['high']], 'low': [new_data['low']], 'close': [new_data['close']],'ema_close': [ema_close],'ema_close_ma': [ema_close_ma]}
        df2 = pd.DataFrame(data_df2)
        #processed_data = processed_data.append(df2, ignore_index = True)
        processed_data = pd.concat([processed_data, df2], ignore_index = True)
        processed_data.reset_index()        
        pass
        return processed_data

    def processData(self, data, alpha, rolling):
        df_data = {"date": [], "open": [], "high": [], "low": [], "close": []}
        for d in data[::-1][:-1]:
            df_data["date"].append(d["ts"])
            df_data["open"].append(d["open"])
            df_data["high"].append(d["high"])
            df_data["low"].append(d["low"])
            df_data["close"].append(d["close"])
        df = pd.DataFrame(df_data)
        df['ema_close'] = df['close'].ewm(alpha=alpha).mean()
        df['ema_close_ma'] = df['close'].rolling(rolling).mean()
        return df

collection = "niftybankticks"
o = Order()
o.getData(collection)
