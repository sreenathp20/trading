from db import MongoDb
mongo = MongoDb()
import pandas as pd
from datetime import datetime, timedelta
from time import sleep
from connect import Upstox
from pya3 import *
from alice import AliceBlue
from tes import triple_exponential_smoothing_minimize, triple_exponential_smoothing

class Order:
    def __init__(self):
        self.strike = None
        self.strike_ce = 43800
        self.strike_pe = 41000
        self.prev_tnx = ''
        self.debug = True
        self.QUANTITY = 25
        pass

    def checkLatestTick(self, collection, start, end):
        
        data = mongo.readTickData(collection, start, end)
        return data

    def getData(self, collection):
        p_l, ot = self.pAndL()
        #today = datetime.today()
        today = datetime(2023,4,27)
        daystart = datetime(year=today.year, month=today.month, 
                    day=today.day, hour=0, minute=0, second=0) 

        start = daystart
        end = start + timedelta(days=1)
        alpha = 0.9
        rolling = 3
        data = self.checkLatestTick(collection, start, end)
        #data = data[:-1]
        processed_data = self.processData(data, alpha, rolling)
        
        while True:
            new_data = self.checkLatestTick(collection, start, end) 
                       
            print("new check")            
            if len(new_data) > len(data):
                processed_data = self.processNewData(processed_data, new_data, alpha, rolling)
                if len(new_data) > 3:
                    flag = self.trade(processed_data, collection, start, end, new_data[0], p_l, ot)
                data = new_data
                print("new data received")
                if not flag:
                    print("Closed for the day")
                    break
                p_l, ot = self.pAndL()
                sleep(30)
            sleep(1)

    def pAndL(self):
        a = AliceBlue()
        a.alice.get_session_id()
        ot = a.alice.get_trade_book()
        order = {'buy': 0, 'sell': 0}
        if type(ot) == list:
            for o in ot:
                if o['Trantype'] == 'S':
                    order['sell'] += (float(o['Price']) * o['Qty'])
                elif o['Trantype'] == 'B':
                    order['buy'] += (float(o['Price']) * o['Qty'])
        else:
            ot = []
        p_l = order['sell'] - order['buy']
        return p_l, ot


    def transact(self, type, direction):
        if type == 'BUY':
            trans_type = TransactionType.Buy
        else:
            trans_type = TransactionType.Sell
        if direction == 'DOWN':
            is_ce = False
            strike = self.strike_pe
        else:
            is_ce = True
            strike = self.strike_ce
        a = AliceBlue()
        a.alice.get_session_id()
        fo = a.alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date="2023-05-11", is_fut=False,strike=strike, is_CE=is_ce)
        if not self.debug:
            o = a.alice.place_order(transaction_type = trans_type, 
                                instrument = fo,
                                quantity = self.QUANTITY,
                                order_type = OrderType.Market,
                                product_type = ProductType.Intraday,
                                #price = 1.0,
                                trigger_price = None,
                                stop_loss = None,
                                square_off = None,
                                trailing_sl = None,
                                is_amo = False,
                                order_tag='order1')
        else:
            o = {"msg": "order placed"}
        print("order placed =======", trans_type, " ======= is_CE => ", is_ce)
        return o

    def buyStock(self, latest_data, direction, collection):
        u = Upstox()        
        u.buyOrSellStock(latest_data, direction, 'BUY', collection)
        o = self.transact('BUY', direction)        
        pass  
        return o
    
    def sellStock(self, latest_data, direction, collection):
        u = Upstox()
        u.buyOrSellStock(latest_data, direction, 'SELL', collection)
        o = self.transact('SELL', direction)
        pass  
        return o
    
    def getTotalPoints(self, data):
        points = 0
        for i in range(0, len(data), 2):
            if i+1 < len(data):
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
                points += addition
        return points


    def trade(self, processed_data, collection, start, end, latest_data, p_l, ot):
        direction = self.getDirection(processed_data)
        if self.debug:
            data = mongo.readLatestTnx(collection, start, end)
        else:
            data = ot
        point_data = data = mongo.readLatestTnx(collection, start, end)
        tot_points = self.getTotalPoints(point_data)
        today = datetime.today()
        dayend = datetime(year=today.year, month=today.month, 
                    day=today.day, hour=15, minute=25, second=0)
        if len(data) > 0:
            prev_tnx = data[0]
            if self.debug:
                trans_type = prev_tnx['type']
                trans_code = 'SELL'
            else:
                trans_type = prev_tnx['Trantype']
                trans_code = 'S'
            if prev_tnx and trans_type == trans_code:
                self.buyStock(latest_data, direction, collection) 
                self.prev_tnx = 'BUY'
            else:
                if self.debug:
                    prev_direction = prev_tnx['direction']
                else:
                    prev_direction = 'DOWN' if prev_tnx['optiontype'] == 'PE' else 'UP'
                if latest_data["ts"]  > dayend:     
                    self.sellStock(latest_data, prev_direction, collection)  
                    self.prev_tnx = 'SELL'
                    direction = prev_direction
                
                if point_data[0]['direction'] == 'UP':
                    future_pl = latest_data['close'] - point_data[0]['close']
                elif point_data[0]['direction'] == 'DOWN':
                    future_pl = point_data[0]['close'] - latest_data['close'] 
                if direction != prev_direction:
                    tot_points += future_pl
                    if future_pl > 0 or future_pl < -99:
                        self.sellStock(latest_data, prev_direction, collection)
                        self.prev_tnx = 'SELL'   
                        self.buyStock(latest_data, direction, collection) 
                        self.prev_tnx = 'BUY'    
                    if tot_points < -49:
                        self.sellStock(latest_data, prev_direction, collection)
                        self.prev_tnx = 'SELL'
                        return False          
                                         
        else:
            if latest_data["ts"] < dayend:
                self.buyStock(latest_data, direction, collection)  
                self.prev_tnx = 'BUY'        
        
        pass
        return True

    def getDirection(self, processed_data):
        #field = 'ema_close_ma'
        field = 'tes_close'
        cur = processed_data[field][len(processed_data) - 1]
        prev = processed_data[field][len(processed_data) - 2]
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
        processed_data['tes_close'] = self.getTripeExponential(processed_data['close'])
        pass
        return processed_data
    
    def getTripeExponential(self, series):
        alpha_final, beta_final, gamma_final = triple_exponential_smoothing_minimize(series)
        t3 = triple_exponential_smoothing(series, alpha_final, beta_final, gamma_final)
        tes_close = pd.Series(t3[:len(series)])
        return tes_close

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
        df['tes_close'] = self.getTripeExponential(df['close'])
        
        return df

collection = "niftybankticks"
o = Order()
o.getData(collection)
