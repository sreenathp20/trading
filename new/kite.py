import logging
from kiteconnect import KiteTicker
from kite_helper import Helper

API_KEY = "v7yjlv3s5zs83imk"


h = Helper(API_KEY=API_KEY, order_id=None)

def getAccessToken():
    f = open("kite_access_token.txt", "r")
    access_token = f.read().strip()
    return access_token

acc = getAccessToken()

kws = KiteTicker(API_KEY, acc)
conf = h.readOrder('order.json')
def on_ticks(ws, ticks):
    print(ticks[0]['last_price'])
    print(ticks[0]['instrument_token'])
    print(ticks[1]['last_price'])
    print(ticks[1]['instrument_token'])
    h.processTicks(ticks, conf)
    
    

def on_connect(ws, response):
    ws.subscribe([conf['OPTION_PE'],conf['OPTION_CE']])
    ws.set_mode(ws.MODE_FULL, [conf['OPTION_PE'],conf['OPTION_CE']])

def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect()