import time
from db import MongoDb
from kite_helper import Helper
from order_kite import Order
mongo = MongoDb()
orderObject = Order(fin_option = None, bank_option = None)

helper = Helper(None, None, False, False)

class Order2:
    def __init__(self, bank_option, counter):
        self.bank_option = bank_option
        self.bank_trigger = 420
        self.print_once = False
        self.counter = counter
        pass

    def main(self):
        flag = False
        while True:
            pe = mongo.readLatestTick('banknifty_tick_pe')
            ce = mongo.readLatestTick('banknifty_tick_ce')
            tick_pe = pe[0]
            tick_ce = ce[0]
            #print(flag)
            if not flag:
                flag = self.counterStrategy(tick_pe,tick_ce, collection='banknifty', order=False, tl=70)
            else:
                print("counterStrategy completed")
        pass

    def counterStrategy(self, pe, ce, collection, order=False, tl=70):
        conf = helper.readOrder('order.json')
        #stoploss = helper.readOrder('stoploss.json')
        if collection == 'banknifty':
            option = self.bank_option
            SYMBOL_PE = conf['SYMBOL_PE']
            SYMBOL_CE = conf['SYMBOL_CE']
            trigger = self.bank_trigger
        if collection == 'finnifty':
            option = self.fin_option
            SYMBOL_PE = conf['FIN_SYMBOL_PE']
            SYMBOL_CE = conf['FIN_SYMBOL_CE']
            trigger = self.fin_trigger
        ub = trigger + tl
        lb = trigger - tl
        if order and not self.print_once:
            orderObject.printBounds(trigger, tl)
            self.print_once = True
        if pe['tick'] > trigger and not option:
            if collection == 'banknifty':
                self.bank_option = 'pe'
            if collection == 'finnifty':
                self.fin_option = 'pe'
            orderObject.buyOption(pe, 'buy', collection, SYMBOL_PE) 
            if order:
                helper.place_order(SYMBOL_PE, 'BUY', conf['QUANTITY'])  
        if option == 'pe' and (pe['tick'] > ub or pe['tick'] < lb):
            orderObject.buyOption(pe, 'sell', collection, SYMBOL_PE) 
            if order:
                helper.place_order(SYMBOL_PE, 'SELL', conf['QUANTITY'])            
            if pe['tick'] > ub:
                return True
                self.setTrigger(collection, ub)
                self.buyOption(pe, 'buy', collection, SYMBOL_PE)
                self.printBounds(ub, tl)
                if order:
                    helper.place_order(SYMBOL_PE, 'BUY', conf['QUANTITY'])                  
            if pe['tick'] < lb:
                if collection == 'banknifty':
                    self.bank_option = 'ce'                    
                if collection == 'finnifty':
                    self.fin_option = 'ce'
                if not self.counter:
                    self.counter = True
                else:
                    return True
                orderObject.setTrigger(collection, ce['tick'])
                orderObject.buyOption(ce, 'buy', collection, SYMBOL_CE)
                orderObject.printBounds(ce['tick'], tl)
                if order:
                    helper.place_order(SYMBOL_CE, 'BUY', conf['QUANTITY'])  
                

        if ce['tick'] > trigger and not option:
            if collection == 'banknifty':
                self.bank_option = 'ce'
            if collection == 'finnifty':
                self.fin_option = 'ce'
            orderObject.buyOption(ce, 'buy', collection, SYMBOL_CE) 
            if order:
                helper.place_order(SYMBOL_CE, 'BUY', conf['QUANTITY'])  
        if option == 'ce' and (ce['tick'] > ub or ce['tick'] < lb):
            orderObject.buyOption(ce, 'sell', collection, SYMBOL_CE) 
            if order:
                helper.place_order(SYMBOL_CE, 'SELL', conf['QUANTITY']) 
            if ce['tick'] > ub:
                return True
                self.setTrigger(collection, ub)
                self.buyOption(ce, 'buy', collection, SYMBOL_CE)
                self.printBounds(ub, tl)
                if order:
                    helper.place_order(SYMBOL_CE, 'BUY', conf['QUANTITY'])  
            if ce['tick'] < lb:
                if collection == 'banknifty':
                    self.bank_option = 'pe'
                if collection == 'finnifty':
                    self.fin_option = 'pe'
                if not self.counter:
                    self.counter = True
                else:
                    return True
                orderObject.setTrigger(collection, pe['tick'])
                orderObject.buyOption(pe, 'buy', collection, SYMBOL_PE)
                orderObject.printBounds(pe['tick'], tl)
                if order:
                    helper.place_order(SYMBOL_PE, 'BUY', conf['QUANTITY']) 
        return False

o = Order2(bank_option = None, counter=False)

o.main()