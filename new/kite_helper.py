import logging
from kiteconnect import KiteConnect
logging.basicConfig(level=logging.DEBUG)
import datetime
from datetime import timedelta
import json  


KITE_ACCESS_TOKEN = "kite_access_token.txt"



class Helper():
    def __init__(self, API_KEY):        
        self.kite = KiteConnect(api_key=API_KEY)
        self.price_pe = None
        self.price_ce = None
        self.order_id = None
        self.setAccessToken()
        pass

    def setAccessToken(self):
        f = open(KITE_ACCESS_TOKEN, "r")
        access_token = f.read().strip()
        self.kite.set_access_token(access_token)

    def processTicks(self, ticks, conf):
        option_pe,option_ce,direction,buffer,symbol_pe,symbol_ce,quantity = conf['OPTION_PE'],conf['OPTION_CE'], conf['DIRECTION'], conf['BUFFER'], conf['SYMBOL_PE'], conf['SYMBOL_CE'], conf['QUANTITY']
        tick_pe = list(filter(lambda x: x['instrument_token'] == option_pe, ticks))
        tick_ce = list(filter(lambda x: x['instrument_token'] == option_ce, ticks))
        if len(tick_pe) > 0:
            if not self.price_pe:
                self.price_pe = tick_pe['last_price']
        if len(tick_ce) > 0:
            if not self.price_ce:
                self.price_ce = tick_ce['last_price']
        if not direction:
            diff_pe = tick_pe['last_price'] - self.price_pe
            diff_ce = tick_ce['last_price'] - self.price_ce
            if diff_pe >= buffer:
                direction = 'PE'
                order_pe = tick_pe['last_price'] // 10 * 11
                self.order_id = self.place_order(symbol_pe, 'BUY', quantity, order_pe)
                conf['DIRECTION'] = direction
                self.saveToJson(conf, KITE_ACCESS_TOKEN)
            if diff_ce >= buffer:
                direction = 'CE'
                order_ce = tick_ce['last_price'] // 10 * 11
                self.order_id = self.place_order(symbol_ce, 'BUY', quantity, order_ce)
                conf['DIRECTION'] = direction
                self.saveToJson(conf, KITE_ACCESS_TOKEN)



    def place_order(self, tradingsymbol, type, quantity, price):        
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
                                order_type=self.kite.ORDER_TYPE_SL,
                                product=self.kite.PRODUCT_MIS,
                                validity=self.kite.VALIDITY_DAY,
                                price=price)
            return order_id
        except:
            print('retrying place_order')
            self.place_order(tradingsymbol, type, quantity, price)
        pass

    def modify_order(self, order_id,quantity,price):
        order_id = self.kite.modify_order(variety=self.kite.VARIETY_REGULAR,
                                          order_id=order_id,
                                          quantity=quantity,
                                          price=price,
                                          order_type=self.kite.ORDER_TYPE_SL,
                                          trigger_price=price)
        
        return order_id

    def readOrder(self, json_file):
        f = open(json_file)
        data = json.load(f)
        return data
    
    def saveToJson(self, data, json_file):               
        with open(json_file, "w") as outfile:
            json.dump(data, outfile)