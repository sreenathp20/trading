import requests
import json
from pya3 import *

class AliceBlue():

    def __init__(self):
        self.alice = Aliceblue(user_id='860288',api_key='YC7ScQBtPe71YUOJ5mWbQcn9V6CHu891ZnJE13J2T7IHSW3cQMHFPKiYUsZqhdTsxMs5GNRr7WUaWVjyGPrEf7E03evOAmqAg6SiNLzNGSV20tUom1UmTDrMLqblYlKM')

    def createSession(self):
        pass
        #print(self.alice.get_session_id())

    def getContract(self):
        self.alice.get_contract_master("MCX")
        self.alice.get_contract_master("NFO")
        self.alice.get_contract_master("NSE")
        self.alice.get_contract_master("BSE")
        self.alice.get_contract_master("CDS")
        self.alice.get_contract_master("BFO")
        self.alice.get_contract_master("INDICES")


    def orderPlacement(self):
        url = 'https://ant.aliceblueonline.com/rest/AliceBlueAPIService/api'+'/placeOrder/executePlaceOrder'
        payload = json.dumps([
        {
            "complexty": "regular",
            "discqty": "0",
            "exch": "NSE",
            "pCode": "NRML",
            "prctyp": "L",
            "price": "3550.00",
            "qty": 1,
            "ret": "DAY",
            "symbol_id": "26009",
            "trading_symbol": "BANK NIFTY INDEX",
            "transtype": "BUY",
            "trigPrice": "",
            "orderTag": "order1"
        }
        ])
        headers = {
        'Authorization': 'Bearer 860288 o51d89QyIuDfhbstlQYTTvYjni6jlyW3lflmiNm5f6yeh4fyVcuVIafLg8u0oC93UQKt1XqdysuX8EkF5RHkpr4PY2HGF28pD5tZlcSCRhhaUJRbszohePmqLpUMAZxShQqAoiBKfc13vFlfyM8dEFXkVxWDcOojetx44nuIlnZTyo8fyXamEZcrdFsHKydQcLoxSoScokuYuDWETiJsgyYAmAJajV8mceiD0JYLp26M9iIaJzBJf8O87fhF3lub',
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)


a = AliceBlue()
#alice.createSession()
a.alice.get_session_id()
balance = a.alice.get_balance()
profile = a.alice.get_profile()
nb = a.alice.get_instrument_by_symbol('INDICES','NIFTY BANK')
#a.getContract()
#a.orderPlacement()
fo = a.alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date="2023-04-27", is_fut=False,strike=None, is_CE=False)

all_sensex_scrips = a.alice.search_instruments('NSE', 'NIFTY')
o = a.alice.place_order(transaction_type = TransactionType.Buy,
                     #instrument = a.alice.get_instrument_by_symbol('INDICES', 'NIFTY BANK'),
                     instrument = fo[94],
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
pass
#080 3521 5055

LTP = 0
socket_opened = False
subscribe_flag = False
subscribe_list = []
unsubscribe_list = []

def socket_open():  # Socket open callback function
    print("Connected")
    global socket_opened
    socket_opened = True
    if subscribe_flag:  # This is used to resubscribe the script when reconnect the socket.
        a.alice.subscribe(subscribe_list)

def socket_close():  # On Socket close this callback function will trigger
    global socket_opened, LTP
    socket_opened = False
    LTP = 0
    print("Closed")

def socket_error(message):  # Socket Error Message will receive in this callback function
    global LTP
    LTP = 0
    print("Error :", message)

def feed_data(message):  # Socket feed data will receive in this callback function
    global LTP, subscribe_flag
    feed_message = json.loads(message)
    if feed_message["t"] == "ck":
        print("Connection Acknowledgement status :%s (Websocket Connected)" % feed_message["s"])
        subscribe_flag = True
        print("subscribe_flag :", subscribe_flag)
        print("-------------------------------------------------------------------------------")
        pass
    elif feed_message["t"] == "tk":
        print("Token Acknowledgement status :%s " % feed_message)
        print("-------------------------------------------------------------------------------")
        pass
    else:
        print("Feed :", feed_message)
        LTP = feed_message[
            'lp'] if 'lp' in feed_message else LTP  # If LTP in the response it will store in LTP variable

# Socket Connection Request
a.alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True,market_depth=False)

while not socket_opened:
    pass

subscribe_list = [a.alice.get_instrument_by_token('INDICES', 26000)]
a.alice.subscribe(subscribe_list)
print(datetime.now())
sleep(10)
print(datetime.now())
# unsubscribe_list = [alice.get_instrument_by_symbol("NSE", "RELIANCE")]
# alice.unsubscribe(unsubscribe_list)
# sleep(8)

# Stop the websocket
a.alice.stop_websocket()
sleep(10)
print(datetime.now())

# Connect the socket after socket close
a.alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)