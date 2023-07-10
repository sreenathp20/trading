import logging
from kiteconnect import KiteConnect
from db import MongoDb
mongo = MongoDb()
logging.basicConfig(level=logging.DEBUG)
import datetime
from datetime import timedelta
import json  

BANKNIFTY = 260105
OPTION_PE = 9591810
OPTION_CE = 9586690
NIFTY_OPTION_PE = 14179330
NIFTY_OPTION_CE = 14164738




class Helper():
    def __init__(self, option, buy_option, sold, order_sold=False):
        self.option = option #None
        self.buy_option = buy_option
        self.sold = sold #False
        self.order_sold = order_sold #False
        self.kite = KiteConnect(api_key="v7yjlv3s5zs83imk")
        self.cnt = 0
        self.STOPLOSS = 360
        self.setAccessToken()
        pass

    def setAccessToken(self):
        f = open("kite_access_token.txt", "r")
        access_token = f.read().strip()
        self.kite.set_access_token(access_token)

    def buyOption(self, tick, type, collection):
        data = {
                "date": tick['exchange_timestamp'],
                "tick": tick['last_price'],
                "option": self.option,
                "type": type
        }
        datas = [data]
        print(type, " :", datas)
        mongo.insertMany(collection+"_option", datas)

    def buyOptionStrategy(self, tick, type, collection, option_name):
        data = {
                "date": tick['exchange_timestamp'],
                "tick": tick['last_price'],
                "option": option_name,
                "type": type
        }
        datas = [data]
        print(type, " :", datas)
        mongo.insertMany(collection+"_option", datas)

    def insertTicks(self, ticks, trigger, option_pe, option_ce, collection, margin, order=False):
        if order:
            print("Ordering is enabled in this call")
        conf = self.readOrder('order.json')
        stoploss = self.readOrder('stoploss.json')
        trigger = trigger
        ub = trigger + (trigger * margin)
        lb = trigger - (trigger * margin)
        tick_pe = list(filter(lambda x: x['instrument_token'] == option_pe, ticks))
        tick_ce = list(filter(lambda x: x['instrument_token'] == option_ce, ticks))
        if len(tick_pe) > 0: 
            tick_pe = tick_pe[0]
            if tick_pe['last_price'] >= trigger and not self.option:
                self.option = 'option_pe'
                self.buyOption(tick_pe, 'buy', collection) 
                if order:
                    self.place_order(conf['SYMBOL_PE'], 'BUY', conf['QUANTITY'])            
            if (tick_pe['last_price'] >= ub or tick_pe['last_price'] < lb)  and self.option == 'option_pe' and not self.sold:
                self.buyOption(tick_pe, 'sell', collection)
                self.sold = True
            data = {
                "date": tick_pe['exchange_timestamp'],
                "tick": tick_pe['last_price']
            }
            if order:
                if self.option == 'option_pe' and not self.order_sold:
                    if stoploss['stoploss'] < trigger and tick_pe['last_price'] > (trigger + (trigger * 0.1)):
                        stoploss['stoploss'] = trigger + (trigger * 0.1)
                        self.saveToJson(stoploss, "stoploss.json")
                    if stoploss['stoploss'] > trigger and tick_pe['last_price'] >= stoploss['stoploss'] + 30:
                        stoploss['stoploss'] += 10
                        self.saveToJson(stoploss, "stoploss.json")

                    if tick_pe['last_price'] < stoploss['stoploss']:
                        self.cnt += 1
                    else:
                        self.cnt = 0
                    if self.cnt >= conf['SELLCOUNT']:
                        self.place_order(conf['SYMBOL_PE'], 'SELL', conf['QUANTITY'])  
                        self.order_sold = True

            datas = [data]
            print(datas)
            mongo.insertMany(collection+"_tick_pe", datas)
        if len(tick_ce) > 0:   
            tick_ce = tick_ce[0]
            if tick_ce['last_price'] >= trigger and not self.option:
                self.option = 'option_ce' 
                self.buyOption(tick_ce, 'buy', collection)     
                if order:
                    self.place_order(conf['SYMBOL_CE'], 'BUY', conf['QUANTITY'])            
            if (tick_ce['last_price'] >= ub or tick_ce['last_price'] < lb)  and self.option == 'option_ce' and not self.sold:
                self.buyOption(tick_ce, 'sell', collection)
                self.sold = True    
            data = {
                "date": tick_ce['exchange_timestamp'],
                "tick": tick_ce['last_price']
            }
            if order:
                if self.option == 'option_ce' and not self.order_sold:
                    if stoploss['stoploss'] < trigger and tick_ce['last_price'] > (trigger + (trigger * 0.1)):
                        stoploss['stoploss'] = trigger + (trigger * 0.1)
                        self.saveToJson(stoploss, "stoploss.json")
                    if stoploss['stoploss'] > trigger and tick_ce['last_price'] >= stoploss['stoploss'] + 30:
                        stoploss['stoploss'] += 10
                        self.saveToJson(stoploss, "stoploss.json")
                        
                    if tick_ce['last_price'] < stoploss['stoploss']:
                        self.cnt += 1
                    else:
                        self.cnt = 0
                    if self.cnt >= conf['SELLCOUNT']:
                        self.place_order(conf['SYMBOL_CE'], 'SELL', conf['QUANTITY'])  
                        self.order_sold = True
            datas = [data]
            print(datas)
            mongo.insertMany(collection+"_tick_ce", datas)
        pass

    def fullStrategy(self, ticks, trigger, order=False):
        if order:
            print("Ordering is enabled in this call")
        conf = self.readOrder('order.json')
        option_pe = conf['OPTION_PE']
        option_ce = conf['OPTION_CE']
        d = datetime.date()
        collection = 'banknifty_400strategy_'
        margin = 40
        stoploss = self.readOrder('stoploss.json')
        trigger = trigger
        ub = trigger + margin
        lb = trigger - margin
        tick_pe = list(filter(lambda x: x['instrument_token'] == option_pe, ticks))
        tick_ce = list(filter(lambda x: x['instrument_token'] == option_ce, ticks))
        if len(tick_pe) > 0: 
            tick_pe = tick_pe[0]
            if tick_pe['last_price'] >= trigger and not self.buy_option:
                self.buy_option = 'PE'
                self.buyOptionStrategy(tick_pe, 'buy', collection, conf['SYMBOL_PE']) 
                if order:
                    self.place_order(conf['SYMBOL_PE'], 'BUY', conf['QUANTITY'])            
            if (tick_pe['last_price'] >= ub or tick_pe['last_price'] < lb)  and self.buy_option == 'option_pe' and not self.sold:
                self.buyOption(tick_pe, 'sell', collection)
                self.sold = True
            data = {
                "date": tick_pe['exchange_timestamp'],
                "tick": tick_pe['last_price']
            }
            if order:
                if self.buy_option == 'option_pe' and not self.order_sold:
                    if stoploss['stoploss'] < trigger and tick_pe['last_price'] > (trigger + (trigger * 0.1)):
                        stoploss['stoploss'] = trigger + (trigger * 0.1)
                        self.saveToJson(stoploss, "stoploss.json")
                    if stoploss['stoploss'] > trigger and tick_pe['last_price'] >= stoploss['stoploss'] + 30:
                        stoploss['stoploss'] += 10
                        self.saveToJson(stoploss, "stoploss.json")

                    if tick_pe['last_price'] < stoploss['stoploss']:
                        self.cnt += 1
                    else:
                        self.cnt = 0
                    if self.cnt >= conf['SELLCOUNT']:
                        self.place_order(conf['SYMBOL_PE'], 'SELL', conf['QUANTITY'])  
                        self.order_sold = True

            datas = [data]
            print(datas)
            mongo.insertMany(collection+"_tick_pe", datas)
        if len(tick_ce) > 0:   
            tick_ce = tick_ce[0]
            if tick_ce['last_price'] >= trigger and not self.buy_option:
                self.buy_option = 'option_ce' 
                self.buyOption(tick_ce, 'buy', collection)     
                if order:
                    self.place_order(conf['SYMBOL_CE'], 'BUY', conf['QUANTITY'])            
            if (tick_ce['last_price'] >= ub or tick_ce['last_price'] < lb)  and self.buy_option == 'option_ce' and not self.sold:
                self.buyOption(tick_ce, 'sell', collection)
                self.sold = True    
            data = {
                "date": tick_ce['exchange_timestamp'],
                "tick": tick_ce['last_price']
            }
            if order:
                if self.buy_option == 'option_ce' and not self.order_sold:
                    if stoploss['stoploss'] < trigger and tick_ce['last_price'] > (trigger + (trigger * 0.1)):
                        stoploss['stoploss'] = trigger + (trigger * 0.1)
                        self.saveToJson(stoploss, "stoploss.json")
                    if stoploss['stoploss'] > trigger and tick_ce['last_price'] >= stoploss['stoploss'] + 30:
                        stoploss['stoploss'] += 10
                        self.saveToJson(stoploss, "stoploss.json")
                        
                    if tick_ce['last_price'] < stoploss['stoploss']:
                        self.cnt += 1
                    else:
                        self.cnt = 0
                    if self.cnt >= conf['SELLCOUNT']:
                        self.place_order(conf['SYMBOL_CE'], 'SELL', conf['QUANTITY'])  
                        self.order_sold = True
            datas = [data]
            print(datas)
            mongo.insertMany(collection+"_tick_ce", datas)
        pass

    def place_order(self, tradingsymbol, type, quantity):        
        if type == 'BUY':
            #self.setAccessToken()
            transaction_type=self.kite.TRANSACTION_TYPE_BUY
        elif type == 'SELL':
            transaction_type=self.kite.TRANSACTION_TYPE_SELL
        try:
            order_id = self.kite.place_order(tradingsymbol=tradingsymbol,
                                exchange=self.kite.EXCHANGE_NFO,
                                transaction_type=transaction_type,
                                quantity=quantity,
                                variety=self.kite.VARIETY_REGULAR,
                                order_type=self.kite.ORDER_TYPE_MARKET,
                                product=self.kite.PRODUCT_MIS,
                                validity=self.kite.VALIDITY_DAY)
        except:
            print('retrying place_order')
            self.place_order(tradingsymbol, type, quantity)
        pass

    def readOrder(self, json_file):
        f = open(json_file)
        data = json.load(f)
        return data
    
    def saveToJson(self, data, json_file):               
        with open(json_file, "w") as outfile:
            json.dump(data, outfile)