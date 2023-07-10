import logging
from kiteconnect import KiteTicker
from kite_helper import Helper, BANKNIFTY, OPTION_PE, OPTION_CE, NIFTY_OPTION_PE, NIFTY_OPTION_CE

logging.basicConfig(level=logging.DEBUG)
h = Helper(None, None, False, False)
h1 = Helper(None, None, False, False)

#h2 = Helper(None, None, False)
# Initialise

def getAccessToken():
    f = open("kite_access_token.txt", "r")
    access_token = f.read().strip()
    return access_token

acc = getAccessToken()

kws = KiteTicker("v7yjlv3s5zs83imk", acc)
conf = h.readOrder('order.json')
def on_ticks(ws, ticks):
    # Callback to receive ticks.
    #logging.debug("Ticks: {}".format(ticks))    
    h.insertTicks(ticks, 400, conf['OPTION_PE'], conf['OPTION_CE'], 'banknifty', 0.2, False)
    #h.fullStrategy(ticks, 400, False)
    #h2.insertTicks(ticks, 400, 11448322, 11436034, 'banknifty23806', 0.2)
    h1.insertTicks(ticks, 180, conf['HAS_OPTION_PE'], conf['HAS_OPTION_CE'], 'has', 0.1)
    h1.insertTicks(ticks, 180, conf['FIN_OPTION_PE'], conf['FIN_OPTION_CE'], 'finnifty', 0.1)
    

def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    ws.subscribe([conf['OPTION_PE'], conf['OPTION_CE'], conf['HAS_OPTION_PE'], conf['HAS_OPTION_CE'], conf['FIN_OPTION_PE'], conf['FIN_OPTION_CE']])

    # Set RELIANCE to tick in `full` mode.
    ws.set_mode(ws.MODE_FULL, [conf['OPTION_PE'], conf['OPTION_CE'], conf['HAS_OPTION_PE'], conf['HAS_OPTION_CE'], conf['FIN_OPTION_PE'], conf['FIN_OPTION_CE']])

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