import logging
from kiteconnect import KiteConnect
from db import MongoDb
mongo = MongoDb()
logging.basicConfig(level=logging.DEBUG)
import datetime
from datetime import timedelta
import json   

class Kite():
    def __init__(self):
        self.kite = KiteConnect(api_key="v7yjlv3s5zs83imk")
        self.request_token = 'TkR3Io1Uqn2Vq5bn0oLzpQ2mzidkbaN2'
        self.api_secret = "yuaogy62eruazre7s3ts8pbr0751tzp7"
        #https://kite.zerodha.com/connect/login?api_key=v7yjlv3s5zs83imk&v=3

    def printLoginUrl(self):
        print(self.kite.login_url())

    def setAccessToken(self):
        f = open("kite_access_token.txt", "r")
        access_token = f.read().strip()
        self.kite.set_access_token(access_token)

    def getAccessToken(self):
        data = self.kite.generate_session(self.request_token, api_secret=self.api_secret)
        f = open("kite_access_token.txt", "a")
        f.write(data['access_token'])
        f.close()
        pass

    def readInstruments(self, ins):
        f = open(ins+'.json')
  
        # returns JSON object as 
        # a dictionary
        data = json.load(f)
        return data['instruments']
        pass

    def getInstruments(self):
        #ins = self.kite.instruments()
        ins = self.readInstruments('instruments')
        self.getLtpData(ins)
        #self.saveToJson(ins)
        pass

    def saveToJson(self, ins):                 
        # Data to be written
        for i in range(len(ins)):
            ins[i]['expiry'] = str(ins[i]['expiry'])
        dictionary ={
            "instruments": ins
        }
            
        with open("instruments.json", "w") as outfile:
            json.dump(dictionary, outfile)

    def getLtpData(self, ins):
        expiry = 'BANKNIFTY23601'
        #expiry = 'BANKNIFTY23511'
        b = list(filter(lambda x: x['tradingsymbol'][:14] == expiry, ins))
        ce = list(filter(lambda x: 'CE' in x['tradingsymbol'], b))
        pe = list(filter(lambda x: 'PE' in x['tradingsymbol'], b))
        for i in b:
            h = self.kite.historical_data(i['instrument_token'], "2023-05-24", "2023-06-01", "minute")
            if len(h) > 0:
                hc = []
                for hi in h:
                    hi['date'] = datetime.datetime(year=hi['date'].year, month=hi['date'].month,day=hi['date'].day, hour=hi['date'].hour, minute=hi['date'].minute)
                    hc.append(hi)
                mongo.insertMany(i['tradingsymbol'], hc)
        pass


    def getPositions(self):
        pos = self.kite.positions()
        pass

    def insertToDB(self, data):
        hc = []
        for hi in data:
            hi['date'] = datetime.datetime(year=hi['date'].year, month=hi['date'].month,day=hi['date'].day, hour=hi['date'].hour, minute=hi['date'].minute)
            hc.append(hi)
        mongo.insertMany('banknifty', hc)

    def getTodayString(self):
        today = datetime.datetime.today()
        #today = datetime(2023,4,27)
        daystart = datetime.datetime(year=today.year, month=today.month, 
                    day=today.day, hour=0, minute=0, second=0)
        month = '0'+str(today.month) if today.month <= 9 else str(today.month)
        day = '0'+str(today.day) if today.day <= 9 else str(today.day)
        day_string = str(today.year)+'-'+str(month)+'-'+str(day)
        return day_string
    
    def check15minCrossed(self):
        #self.history()
        ins = self.readInstruments('stock_instruments')
        day_string = self.getTodayString()
        today = datetime.datetime.today()
        #today = datetime(2023,4,27)
        start = datetime.datetime(year=today.year, month=today.month, 
                    day=today.day, hour=0, minute=0, second=0)
        end = start + timedelta(days=1)
        crossed = {}
        for i in ins:
            crossed[i['name']] = False
        for i in ins:
            data = mongo.readAll(i['name']+day_string, start, end)
            low = float('inf')
            high = float('-inf')
            for d in data[:15]:
                if d['high'] > high:
                    high = d['high']
                if d['low'] < low:
                    low = d['low']
            for d in data[15:]:
                if d['high'] > high:
                    crossed[i['name']] = True
                if d['low'] < low:
                    crossed[i['name']] = True
        for k in crossed.keys():
            if not crossed[k]:
                print(k)

    def history(self):        
        ins = self.readInstruments('stock_instruments')
        day_string = self.getTodayString()
        
        for i in ins:
            h = self.kite.historical_data(i['token'], day_string, day_string, "minute")
            for hi in range(len(h)):
                d = h[hi]['date']
                h[hi]['date'] = datetime.datetime(year=d.year, month=d.month, day=d.day, hour=d.hour, minute=d.minute)
            mongo.insertMany(i['name']+day_string, h)
        #self.insertToDB(h)
        pass

    def backTestStopLoss(self):
        collection = 'banknifty'
        total = {"total": 0, "profit": 0, "loss": 0, "holiday": 0}
        first_start = datetime.datetime(2023,5,19)
        for i in range(60):
            start = first_start  + timedelta(days=i)
            end = start + timedelta(days=1)
            print(start)
            data = mongo.readAll(collection, start, end)
            if len(data) > 0:
                open = data[0]['open']
                start_open = data[14]['open']
                stoploss = 80
                trade = []
                if open > start_open:
                    direction = 'DOWN'
                else:
                    direction = 'UP'
                opt = data[14].copy()
                opt['direction'] = direction
                opt['type'] = 'BUY'
                prev_buy = opt
                trade.append(opt)
                current_stoploss = start_open - stoploss if direction == 'UP' else start_open + stoploss
                for d in data[15:]:
                    if direction == 'UP':
                        if d['open'] > start_open:
                            current_stoploss = d['open'] - stoploss
                        else:
                            if d['open'] < current_stoploss:
                                opt = d.copy()
                                opt['direction'] = direction
                                opt['type'] = 'SELL'
                                trade.append(opt)
                                opt_buy = d.copy()
                                direction = 'DOWN'
                                opt_buy['direction'] = direction
                                opt_buy['type'] = 'BUY'
                                trade.append(opt_buy)
                    elif direction == 'DOWN':
                        if d['open'] < start_open:
                            current_stoploss = d['open'] + stoploss
                        else:
                            if d['open'] > current_stoploss:
                                opt = d.copy()
                                opt['direction'] = direction
                                opt['type'] = 'SELL'
                                trade.append(opt)
                                opt_buy = d.copy()
                                direction = 'UP'
                                opt_buy['direction'] = direction
                                opt_buy['type'] = 'BUY'
                                trade.append(opt_buy)
                    start_open = d['open']
                opt = data[-1].copy()
                opt['direction'] = trade[-1]['direction']
                opt['type'] = 'SELL'
                trade.append(opt)
                tot = {"total": 0, "cnt": 0}
                for t in range(0,len(trade),2):
                    buy = trade[t]
                    sell = trade[t+1]
                    if buy['direction'] == 'UP':
                        points = sell['open'] - buy['open']
                    else:
                        points = buy['open'] - sell['open']
                    print("points: ", points)
                    tot['total'] += points
                    tot['cnt'] += 1
                print("total: ",tot)
                total['total'] += tot['total']
                if tot['total'] < 0:
                    total['loss'] += 1
                elif tot['total'] > 0:
                    total['profit'] += 1
                else:
                    total['holiday'] += 1
        print("Grand Total: ", total)
        pass



    def backTest(self):
        for day in range(9):
            start = datetime.datetime(2023,5,24)+timedelta(days=day)
            print("Date: ",start)
            end = start + timedelta(days=1)
            lt = datetime.datetime(start.year,start.month,start.day,9,25)
            ut = lt + + timedelta(minutes=5)
            lb = 350
            ub = lb+50
            trigger = ub+15
            c = mongo.db.list_collection_names()
            pe = list(filter(lambda x: 'PE' in x, c))
            ce = list(filter(lambda x: 'CE' in x, c))
            selected_pe = None
            selected_ce = None
            pe.sort()
            for p in pe:
                #print(p)
                data = mongo.readAll(p, start, end)
                for d in data:
                    if d['date'] >= lt and d['date'] <= ut:
                        # if (d['open'] >= lb and d['open'] <= ub) or (d['high'] >= lb and d['high'] <= ub) or (d['low'] >= lb and d['low'] <= ub) or (d['close'] >= lb and d['close'] <= ub):
                        if d['high'] >= lb and d['high'] <= ub:
                            selected_pe = p
                            break
                if selected_pe:
                    break
            ce.sort()
            for c in ce:
                data = mongo.readAll(c, start, end)
                for d in data:
                    if d['date'] >= lt and d['date'] <= ut:
                        # if (d['open'] >= lb and d['open'] <= ub) or (d['high'] >= lb and d['high'] <= ub) or (d['low'] >= lb and d['low'] <= ub) or (d['close'] >= lb and d['close'] <= ub):
                        if d['high'] >= lb and d['high'] <= ub:
                            selected_ce = c
                            break
                if selected_ce:
                    break
            if selected_pe:
                data_pe = mongo.readAll(selected_pe, ut, end)
            else:
                data_pe = []
            if selected_ce:
                data_ce = mongo.readAll(selected_ce, ut, end)
            else:
                data_ce = []
            selected_option = None
            triggered_time = None
            bought_candle = None
            for i in range(len(data_pe)):
                t = ut + timedelta(minutes=i)
                pe = data_pe[i]
                ce = data_ce[i]
                if ce['date'] == t:
                    #if (ce['open'] >= trigger) or (ce['high'] >= trigger) or (ce['low'] >= trigger) or (ce['close'] >= trigger):
                    if ce['high'] >= trigger:
                        selected_option = selected_ce
                        triggered_time = t
                        bought_candle = ce
                if pe['date'] == t and not selected_option:
                    #if (pe['open'] >= trigger) or (pe['high'] >= trigger) or (pe['low'] >= trigger) or (pe['close'] >= trigger):
                    if pe['high'] >= trigger:
                        selected_option = selected_pe
                        triggered_time = t
                        bought_candle = pe
                if selected_option:
                    break
            if selected_option:
                option_data = mongo.readAll(selected_option, triggered_time, end)
            else:
                option_data = []
            for d in option_data:
                #profit = d['high'] - bought_candle['high']
                #loss = d['low'] - bought_candle['high']
                profit = d['high'] - trigger
                loss = d['low'] - trigger
                if profit >= (trigger * 0.2):
                #if profit >= 75:
                    print("Profit :", profit)
                    break
                if loss < (trigger * -0.2):
                #if loss < -85:
                    print("Loss :", loss)
                    break
        pass   

    def backTestNifty(self):
        for day in range(9):
            start = datetime.datetime(2023,5,24)+timedelta(days=day)
            print("Date: ",start)
            end = start + timedelta(days=1)
            ut = datetime.datetime(start.year,start.month,start.day,9,15)
            trigger = 180
            c = mongo.db.list_collection_names()
            pe = list(filter(lambda x: 'PE' in x, c))
            ce = list(filter(lambda x: 'CE' in x, c))
            selected_pe = None
            selected_ce = None
            pe.sort()
            prev_start = start - timedelta(days=1)
            diff = float('inf')
            for p in pe:
                #print(p)
                data1 = []
                while len(data1) == 0:
                    data1 = mongo.readAll(p, prev_start, start)
                    prev_start = prev_start - timedelta(days=1)
                    if (start - prev_start).days > 8:
                        break
                if len(data1) > 0:
                    d = data1[-1]
                    if (trigger - d['high']) < diff and (trigger - d['high']) > 0:
                        selected_pe = p
                        diff = trigger - d['high']
            ce.sort()
            prev_start = start - timedelta(days=1)
            diff = float('inf')
            for c in ce:
                data1 = []
                while len(data1) == 0:
                    data1 = mongo.readAll(c, prev_start, start)
                    prev_start = prev_start - timedelta(days=1)
                    if (start - prev_start).days > 8:
                        break
                if len(data1) > 0:
                    d = data1[-1]
                    if (trigger - d['high']) < diff and (trigger - d['high']) > 0:
                        selected_ce = c
                        diff = trigger - d['high']
            if selected_pe:
                data_pe = mongo.readAll(selected_pe, start, end)
            else:
                data_pe = []
            if selected_ce:
                data_ce = mongo.readAll(selected_ce, start, end)
            else:
                data_ce = []
            selected_option = None
            triggered_time = None
            bought_candle = None
            for i in range(len(data_pe)):
                t = ut + timedelta(minutes=i)
                pe = data_pe[i]
                ce = data_ce[i]
                if ce['date'] == t:
                    #if (ce['open'] >= trigger) or (ce['high'] >= trigger) or (ce['low'] >= trigger) or (ce['close'] >= trigger):
                    if ce['high'] >= trigger:
                        selected_option = selected_ce
                        triggered_time = t
                        bought_candle = ce
                if pe['date'] == t and not selected_option:
                    #if (pe['open'] >= trigger) or (pe['high'] >= trigger) or (pe['low'] >= trigger) or (pe['close'] >= trigger):
                    if pe['high'] >= trigger:
                        selected_option = selected_pe
                        triggered_time = t
                        bought_candle = pe
                if selected_option:
                    break
            if selected_option:
                option_data = mongo.readAll(selected_option, triggered_time, end)
            else:
                option_data = []
            for d in option_data:
                profit = d['high'] - bought_candle['high']
                loss = d['low'] - bought_candle['high'] 
                if profit >= (trigger * 0.1):
                #if profit >= 75:
                    print("Profit :", profit)
                    break
                if loss < (trigger * -0.1):
                #if loss < -85:
                    print("Loss :", loss)
                    break
        pass    

    def place_order(self):
        order_id = self.kite.place_order(tradingsymbol="JUBLPHARMA",
                                exchange=self.kite.EXCHANGE_NSE,
                                transaction_type=self.kite.TRANSACTION_TYPE_SELL,
                                quantity=1,
                                variety=self.kite.VARIETY_REGULAR,
                                order_type=self.kite.ORDER_TYPE_MARKET,
                                product=self.kite.PRODUCT_MIS,
                                validity=self.kite.VALIDITY_DAY)



k = Kite()
#k.printLoginUrl()
k.getAccessToken()
#k.setAccessToken()
#k.getInstruments()
#k.getPositions()
#k.history()
#k.backTest()
#k.backTestStopLoss()
#k.check15minCrossed()
#k.backTestNifty()
#k.place_order()



# Redirect the user to the login url obtained
# from kite.login_url(), and receive the request_token
# from the registered redirect url after the login flow.
# Once you have the request_token, obtain the access_token
# as follows.

