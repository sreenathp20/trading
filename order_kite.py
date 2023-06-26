import time
from db import MongoDb
from kite_helper import Helper
mongo = MongoDb()

helper = Helper(None, None, False, False)

class Order:
    def __init__(self, fin_option, bank_option):
        self.fin_option = fin_option
        self.bank_option = bank_option
        self.fin_trigger = 180
        self.bank_trigger = 400
        pass

    def main(self):
        while True:
            pe = mongo.readLatestTick('banknifty_tick_pe')
            ce = mongo.readLatestTick('banknifty_tick_ce')
            # pe = mongo.readLatestTick('nifty_tick_pe')
            # ce = mongo.readLatestTick('nifty_tick_ce')
            fin_pe = mongo.readLatestTick('finnifty_tick_pe')
            fin_ce = mongo.readLatestTick('finnifty_tick_ce')
            fin_tick_pe = fin_pe[0]
            fin_tick_ce = fin_ce[0]
            tick_pe = pe[0]
            tick_ce = ce[0]
            print(tick_pe)
            print(tick_ce)
            print(fin_tick_pe)
            print(fin_tick_ce)
            self.fullStrategy(tick_pe,tick_ce, collection='banknifty', order=False, tl=40)
            self.fullStrategy(fin_tick_pe,fin_tick_ce, collection='finnifty', order=False, tl=18)
            print("============")
            #time.sleep(1)
        pass

    def buyOption(self, tick, type, collection):
        data = {
                "date": tick['date'],
                "tick": tick['tick'],
                "option": self.option,
                "type": type
        }
        datas = [data]
        print(type, " :", datas)
        mongo.insertMany(collection+"_fs_option", datas)

    def setTrigger(self, collection, trigger):
        if collection == 'banknifty':
            self.bank_option = trigger
        if collection == 'finnifty':
            self.fin_option = trigger


    def fullStrategy(self, pe, ce, collection, order=False, tl=40):
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
        if pe['tick'] > trigger and not option:
            if collection == 'banknifty':
                self.bank_option = 'pe'
            if collection == 'finnifty':
                self.fin_option = 'pe'
            self.buyOption(pe, 'buy', collection) 
            if order:
                helper.place_order(SYMBOL_PE, 'BUY', conf['QUANTITY'])  
        if option == 'pe' and (pe['tick'] > ub or pe['tick'] < lb):
            self.buyOption(pe, 'sell', collection) 
            if order:
                helper.place_order(SYMBOL_PE, 'SELL', conf['QUANTITY'])            
            if pe['tick'] > ub:
                self.setTrigger(collection, ub)
                self.buyOption(pe, 'sell', collection)
            if pe['tick'] < lb:
                if collection == 'banknifty':
                    self.bank_option = 'ce'                    
                if collection == 'finnifty':
                    self.fin_option = 'ce'
                self.setTrigger(collection, ce['tick'])
                self.buyOption(ce, 'buy', collection)
                if order:
                    helper.place_order(SYMBOL_CE, 'BUY', conf['QUANTITY'])  

        if ce['tick'] > trigger and not option:
            if collection == 'banknifty':
                self.bank_option = 'ce'
            if collection == 'finnifty':
                self.fin_option = 'ce'
            self.buyOption(ce, 'buy', collection) 
            if order:
                helper.place_order(SYMBOL_CE, 'BUY', conf['QUANTITY'])  
        if option == 'ce' and (ce['tick'] > ub or ce['tick'] < lb):
            self.buyOption(ce, 'sell', collection) 
            if order:
                helper.place_order(SYMBOL_CE, 'SELL', conf['QUANTITY']) 
            if ce['tick'] > ub:
                self.setTrigger(collection, ub)
                self.buyOption(ce, 'sell', collection)
            if ce['tick'] < lb:
                if collection == 'banknifty':
                    self.bank_option = 'pe'
                if collection == 'finnifty':
                    self.fin_option = 'pe'
                self.setTrigger(collection, pe['tick'])
                self.buyOption(pe, 'buy', collection)
                if order:
                    helper.place_order(SYMBOL_PE, 'BUY', conf['QUANTITY']) 
        pass

o = Order(fin_option = None, bank_option = None)

o.main()