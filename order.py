from db import MongoDb
mongo = MongoDb()
import pandas as pd
from datetime import datetime, timedelta
from time import sleep
from connect import Upstox
from pya3 import *
from alice import AliceBlue

class Order:
    def __init__(self):
        self.strike = None
        self.strike_ce = 43800
        self.strike_pe = 41000
        self.prev_tnx = ''
        self.debug = True
        pass

    def checkLatestTick(self, collection, start, end):
        
        data = mongo.readTickData(collection, start, end)
        return data

    def getData(self, collection):
        p_l, ot = self.pAndL()
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
                    self.trade(processed_data, collection, start, end, new_data[0], p_l, ot)
                data = new_data
                print("new data received")
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
        fo = a.alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date="2023-04-27", is_fut=False,strike=strike, is_CE=is_ce)
        if not self.debug:
            o = a.alice.place_order(transaction_type = trans_type, 
                                instrument = fo,
                                quantity = 25,
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


    def trade(self, processed_data, collection, start, end, latest_data, p_l, ot):
        direction = self.getDirection(processed_data)
        if self.debug:
            data = mongo.readLatestTnx(collection, start, end)
        else:
            data = ot
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
                    
                if direction != prev_direction:
                    self.sellStock(latest_data, prev_direction, collection)
                    self.prev_tnx = 'SELL'   
                    self.buyStock(latest_data, direction, collection) 
                    self.prev_tnx = 'BUY'              
                                         
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
