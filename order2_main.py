import time, datetime
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
        self.pe_date = None
        self.ce_date = None
        self.pe_prev_ha = None
        self.ce_prev_ha = None
        self.pe_ha_buy = False
        self.pe_ha_green_count = 0
        self.ce_ha_buy = False
        self.ce_ha_green_count = 0
        self.first = True
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
                flag = self.counterStrategy(tick_pe,tick_ce, collection='banknifty', order=True, tl=70)
            else:
                print("counterStrategy completed")
        pass

    def has_main(self):
        while True:
            pe = mongo.readLatestTick('banknifty_tick_pe')
            ce = mongo.readLatestTick('banknifty_tick_ce')
            tick_pe = pe[0]
            tick_ce = ce[0]
            #print(flag)
            #if not flag:
            flag = self.hasStrategy(tick_pe,tick_ce, collection='has', order=False, tl=70)

    def saveCandle(self, o, h, l, c, collection, d):
        date = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute)
        data = {
                "date": date,
                "open": o,
                "high": h,
                "low": l,
                "close": c
        }
        datas = [data]
        mongo.insertMany(collection+"_1m_candle", datas)

    def saveHACandle(self, o, h, l, c, collection, d, tick, order=False):
        conf = helper.readOrder('order.json')
        if collection == 'pe':
            if not self.pe_prev_ha:
                prev_ha_o = conf['PE_HA_OPEN']
                prev_ha_c = conf['PE_HA_CLOSE']
            else:
                prev_ha_o = self.pe_prev_ha['OPEN']
                prev_ha_c = self.pe_prev_ha['CLOSE']
        elif collection == 'ce':
            if not self.ce_prev_ha:
                prev_ha_o = conf['CE_HA_OPEN']
                prev_ha_c = conf['CE_HA_CLOSE']
            else:
                prev_ha_o = self.ce_prev_ha['OPEN']
                prev_ha_c = self.ce_prev_ha['CLOSE']
        ha_o = (prev_ha_o + prev_ha_c) / 2
        ha_c = (o + h + l + c) / 4
        a = (ha_o, ha_c, h)
        ha_h = max(a)
        b = (ha_o, ha_c, l)
        ha_l = min(b)
        if collection == 'pe':
            self.pe_prev_ha = {"OPEN": ha_o, "CLOSE": ha_c, "HIGH": ha_h, "LOW": ha_l }
            if not self.pe_ha_buy:
                if ha_o < ha_c and (ha_o-2) < ha_l:
                    self.pe_ha_green_count += 1
                else:
                    self.pe_ha_green_count = 0
            else:
                self.pe_ha_green_count = 0
                if ha_o > ha_c:
                    #place sell order
                    orderObject.buyOption(tick, 'sell', 'has_pe_', conf['HAS_SYMBOL_PE'])
                    if order:
                        helper.place_order(conf['HAS_SYMBOL_PE'], 'SELL', conf['HAS_QUANTITY'])
                    self.pe_ha_buy = False
        if collection == 'ce':
            self.ce_prev_ha = {"OPEN": ha_o, "CLOSE": ha_c, "HIGH": ha_h, "LOW": ha_l }
            if not self.ce_ha_buy:
                if ha_o < ha_c and (ha_o-2) < ha_l:
                    self.ce_ha_green_count += 1
                else:
                    self.ce_ha_green_count = 0
            else:
                self.ce_ha_green_count = 0
                if ha_o > ha_c:
                    #place sell order
                    orderObject.buyOption(tick, 'sell', 'has_ce_', conf['HAS_SYMBOL_CE'])
                    if order:
                        helper.place_order(conf['HAS_SYMBOL_CE'], 'SELL', conf['HAS_QUANTITY'])
                    self.ce_ha_buy = False
        date = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute)
        data = {
                "date": date,
                "open": ha_o,
                "high": ha_h,
                "low": ha_l,
                "close": ha_c
        }
        datas = [data]
        mongo.insertMany(collection+"_has_candle", datas)
            
        pass

    def hasStrategy(self, pe, ce, collection, order=False, tl=70):
        pe_h, pe_l = -float('inf'),float("inf")
        if order and self.first:
            self.first = False
            print("Ordering is enabled in this call")
        if not self.pe_ha_buy and self.pe_ha_green_count >= 2:
            # place buy order
            conf = helper.readOrder('order.json')
            orderObject.buyOption(pe, 'buy', 'has_pe_', conf['HAS_SYMBOL_PE'])
            if order:
                helper.place_order(conf['HAS_SYMBOL_PE'], 'BUY', conf['HAS_QUANTITY'])
            self.pe_ha_buy = True 
            self.pe_ha_green_count = 0
        if not self.ce_ha_buy and self.ce_ha_green_count >= 2:
            # place buy order
            conf = helper.readOrder('order.json')
            orderObject.buyOption(ce, 'buy', 'has_ce_', conf['HAS_SYMBOL_CE'])
            if order:
                helper.place_order(conf['HAS_SYMBOL_CE'], 'BUY', conf['HAS_QUANTITY'])
            self.ce_ha_buy = True 
            self.ce_ha_green_count = 0
        if not self.pe_date:
            self.pe_date = pe['date']
            pe_o = pe['tick']
        elif pe['date'].minute != self.pe_date.minute:
            self.saveCandle(pe_o,pe_h,pe_l,pe_c, 'pe', self.pe_date)
            self.saveHACandle(pe_o,pe_h,pe_l,pe_c, 'pe', self.pe_date, pe, order)
            pe_h, pe_l = -float('inf'),float("inf")
            self.pe_date = pe['date']
            pe_o = pe['tick']
        if pe['tick'] > pe_h:
            pe_h = pe['tick']
        if pe['tick'] < pe_l:
            pe_l = pe['tick']
        if pe['date'].second == 58:
            pe_c = pe['tick']
        if pe['date'].second == 59:
            pe_c = pe['tick']

        ce_h, ce_l = -float('inf'),float("inf")
        if not self.ce_date:
            self.ce_date = ce['date']
            ce_o = ce['tick']
        elif ce['date'].minute != self.ce_date.minute:
            self.saveCandle(ce_o,ce_h,ce_l,ce_c, 'ce', self.ce_date)
            self.saveHACandle(ce_o,ce_h,ce_l,ce_c, 'ce', self.ce_date, ce, order)
            ce_h, ce_l = -float('inf'),float("inf")
            self.ce_date = ce['date']
            ce_o = ce['tick']
        if ce['tick'] > ce_h:
            ce_h = ce['tick']
        if ce['tick'] < ce_l:
            ce_l = ce['tick']
        if ce['date'].second == 58:
            ce_c = ce['tick']
        if ce['date'].second == 59:
            ce_c = ce['tick']
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