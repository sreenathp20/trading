import logging
from kiteconnect import KiteConnect
logging.basicConfig(level=logging.DEBUG)
import datetime
from datetime import timedelta
import json  
import time


KITE_ACCESS_TOKEN = "kite_access_token.txt"
ORDER_JSON = "order.json"



class Helper():
    def __init__(self, API_KEY, order_id):     
        self.kite = KiteConnect(api_key=API_KEY)
        self.price_pe = None
        self.price_ce = None
        self.order_id = order_id
        self.order = None
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
            tick_pe = tick_pe[0]
            if not self.price_pe:
                self.price_pe = tick_pe['last_price']
        else:
            tick_pe = {'last_price': 0}
        if len(tick_ce) > 0:
            tick_ce = tick_ce[0]
            if not self.price_ce:
                self.price_ce = tick_ce['last_price']
        else:
            tick_ce = {'last_price': 0}
        # first time coming with no direction
        if not direction:
            print("self.price_pe: ", self.price_pe)
            print("self.price_ce: ", self.price_ce)
            diff_pe = tick_pe['last_price'] - self.price_pe if tick_pe else 0
            diff_ce = tick_ce['last_price'] - self.price_ce if tick_ce else 0
            # print("last_price PE: ", tick_pe['last_price'])
            # print("last_price CE: ", tick_ce['last_price'])
            print("diff_pe PE: ", diff_pe)
            print("diff_ce CE: ", diff_ce)
            if diff_pe >= buffer:
                last_price = tick_pe['last_price']
                direction = 'PE'
                self.order = last_price // 10 * 10 + 10
                print("PLACE ORDER: SYMBOL: ", symbol_pe, ", BUY, QUANTITY: ", quantity, ", PRICE: ",self.order)
                self.order_id = self.place_order(symbol_pe, 'BUY', quantity, self.order)
                conf['DIRECTION'] = direction
                self.saveToJson(conf, ORDER_JSON)
            if diff_ce >= buffer:
                last_price = tick_ce['last_price']
                direction = 'CE'
                self.order = last_price // 10 * 10 + 10
                print("PLACE ORDER: SYMBOL: ", symbol_ce, ", BUY, QUANTITY: ", quantity, ", PRICE: ",self.order)
                self.order_id = self.place_order(symbol_ce, 'BUY', quantity, self.order)
                conf['DIRECTION'] = direction
                self.saveToJson(conf, ORDER_JSON)

        # if one order is placed and order id available
        if self.order_id:     
            order_history = self.kite.orders()        
            order = list(filter(lambda x: x['order_id'] == str(self.order_id), order_history))[0]
            status = order['status']
            symbol = symbol_ce if direction == 'CE' else symbol_pe
            if status == 'COMPLETE' and order['transaction_type'] == 'BUY':                
                price = self.order-buffer                
                print("PLACE ORDER: SYMBOL: ", symbol, ", SELL, QUANTITY: ", quantity, ", PRICE: ",price)
                self.order_id = self.place_order(symbol, 'SELL', quantity, price)
            
            # if sell is complete resetting to initial state
            if status == 'COMPLETE' and order['transaction_type'] == 'SELL':
                direction = 'CE' if direction == 'PE' else 'PE'
                conf['DIRECTION'] = direction
                self.price_pe = tick_pe['last_price']
                self.price_ce = tick_ce['last_price']
                symbol = symbol_ce if direction == 'CE' else symbol_pe
                last_price = tick_ce['last_price'] if direction == 'CE' else tick_pe['last_price']
                self.order = last_price // 10 * 10 + 10
                print("PLACE ORDER: SYMBOL: ", symbol, ", BUY, QUANTITY: ", quantity, ", PRICE: ",self.order)
                self.order_id = self.place_order(symbol, 'BUY', quantity, self.order)
                self.saveToJson(conf, ORDER_JSON)
                pass
            last_price = tick_ce['last_price'] if direction == 'CE' else tick_pe['last_price']
            diff = last_price - self.order
            if diff >= buffer:
                inc = ((diff//buffer) - 1 ) * buffer
                price = self.order + inc
                print("MODIFY ORDER: ORDER ID: ", self.order_id, ", QUANTITY: ", quantity, ", PRICE: ",price)
                self.order_id = self.modify_order(self.order_id, quantity, price)





    def place_order(self, tradingsymbol, type, quantity, price):        
        if type == 'BUY':
            #self.setAccessToken()
            transaction_type=self.kite.TRANSACTION_TYPE_BUY
        elif type == 'SELL':
            transaction_type=self.kite.TRANSACTION_TYPE_SELL
        try:
            print("price: ", price)
            order_id = self.kite.place_order(tradingsymbol=tradingsymbol,
                                    exchange=self.kite.EXCHANGE_NFO,
                                    transaction_type=transaction_type,
                                    quantity=quantity,
                                    variety=self.kite.VARIETY_REGULAR,
                                    order_type=self.kite.ORDER_TYPE_SL,
                                    product=self.kite.PRODUCT_MIS,
                                    validity=self.kite.VALIDITY_DAY,
                                    price=price,
                                    trigger_price=price)
            time.sleep(3)
            return order_id
        except:
            print('retrying place_order')
            self.place_order(tradingsymbol, type, quantity, price)
        pass

    def modify_order(self, order_id,quantity,price):
        try:
            self.kite.modify_order(variety=self.kite.VARIETY_REGULAR,
                                          order_id=order_id,
                                          quantity=quantity,
                                          price=price,
                                          order_type=self.kite.ORDER_TYPE_SL,
                                          trigger_price=price)
            time.sleep(3)
        except:
            print('retrying modify_order')
            self.modify_order(order_id,quantity,price)
        
        return order_id

    def readOrder(self, json_file):
        f = open(json_file)
        data = json.load(f)
        return data
    
    def saveToJson(self, data, json_file):               
        with open(json_file, "w") as outfile:
            json.dump(data, outfile)


# API_KEY = "v7yjlv3s5zs83imk"

# order_id = 2



# h = Helper(API_KEY, None)

# order_history = h.kite.orders()
# order = list(filter(lambda x: x['order_id'] == str(order_id), order_history))
# status = order[0]['status']

