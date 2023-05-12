from upstox import mongodb
import pandas as pd
from datetime import datetime, timedelta
from upstox.tes1 import triple_exponential_smoothing_minimize, triple_exponential_smoothing
from upstox.des1 import double_exponential_smoothing

class Upstox():
    def __init__(self):
        pass

    def getTickData(self, collection):
        collection=mongodb.db[collection]
        cursor = collection.find({}, {"open": 1, "high": 1, "low": 1, "close": 1, "ts": 1, "_id": False})
        data = []
        for document in cursor:
            data.append(document)
        return data
    
    def getHistoryData(self, collection, start, end):
        collection=mongodb.db[collection]
        myquery = { "date": { "$gte": start, "$lt": end } }
        cursor = collection.find(myquery, {"open": 1, "high": 1, "low": 1, "close": 1, "date": 1, "_id": False}).sort("date")
        data = []
        for document in cursor:
            data.append(document)
        return data
    
    def getEMAData(self, data):
        df_data = []
        for d in data:
            df_data.append([d['ts'], d['open'], d['high'], d['low'], d['close']])
        df = pd.DataFrame(df_data, columns=['ts', 'open', 'high', 'low', 'close'])
        df['ema_close_p3'] = df['close'].ewm(alpha=0.3).mean()
        res_data = []
        for i in range(len(df)):
            res_data.append({"ts": df['ts'][i], "open": df['open'][i], "high": df['high'][i], "low": df['low'][i], "close": df['close'][i],"ema_close_p3": df['ema_close_p3'][i]})
        return res_data
    
    def getHistoryEMAData(self, data):
        df_data = []
        for d in data:
            df_data.append([d['date'], d['open'], d['high'], d['low'], d['close']])
        df = pd.DataFrame(df_data, columns=['date', 'open', 'high', 'low', 'close'])
        df['ema_close_p3'] = df['close'].ewm(alpha=0.9).mean()
        rolling = 3
        df['ema_close_p3'] = df['ema_close_p3'].rolling(rolling).mean()
        # alpha_final, beta_final, gamma_final = triple_exponential_smoothing_minimize(df['close'])
        # t3 = triple_exponential_smoothing(df['close'], alpha_final, beta_final, gamma_final)
        # df['ema_close_p3'] = pd.Series(t3[:len(df['close'])])
        #df['ema_close_p3'] = double_exponential_smoothing(df['close'], 0.9, 0.9, 1)[:-1]
        res_data = []
        for i in range(len(df)):
            if i < (rolling-1):
                ema_close_p3 = None
            else:
                ema_close_p3 = df['ema_close_p3'][i]
            #print(df['date'][i])
            res_data.append({"date": df['date'][i], "open": df['open'][i], "high": df['high'][i], "low": df['low'][i], "close": df['close'][i],"ema_close_p3": ema_close_p3})
        return res_data
    
    def getProfitData(self, gain):
        collection=mongodb.db['profit_or_loss']
        myquery = { "gain": gain }
        cursor = collection.find(myquery, {"_id": False}).sort("date")
        data = []
        for document in cursor:
            data.append(document)
        pass
        result = []
        for d in data:
            start = d['date']
            end = start + timedelta(days=1)
            res = self.getHistoryData('nseindexniftybank2', start, end)
            res = self.getHistoryEMAData(res, start)
            result.append({"result": res, "gain": d["value"]})
        return result