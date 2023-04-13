from upstox import mongodb
import pandas as pd


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