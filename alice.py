import requests
import json
from pya3 import *
import pandas as pd

class AliceBlue():

    def __init__(self):
        self.alice = Aliceblue(user_id='860288',api_key='YC7ScQBtPe71YUOJ5mWbQcn9V6CHu891ZnJE13J2T7IHSW3cQMHFPKiYUsZqhdTsxMs5GNRr7WUaWVjyGPrEf7E03evOAmqAg6SiNLzNGSV20tUom1UmTDrMLqblYlKM')

    def strike_price(self):
        import requests
        import io
        from pprint import pprint
        import pandas as pd
        instruments=requests.get('https://api.kite.trade/instruments').content
        instruments=pd.read_csv(io.StringIO(instruments.decode('utf-8')))
        instruments_str_match=instruments[instruments['segment'].str.match('NFO-OPT')]
        strike=instruments_str_match[instruments_str_match['tradingsymbol'].str.match('BANKNIFTY')]
        strike_price=strike['strike']
        print(strike_price)

    def web_socket(self):

        def event_handler_quote_update(ticks):
            print(ticks)

        def open_callback():
            global socket_opened
            socket_opened=True
        self.alice.start_websocket(event_handler_quote_update,open_callback,run_in_background=True)
        sleep(5)
        while True:  
            print("started") 
            sleep(5)         
            self.alice.subscribe([self.alice.get_instrument_by_symbol('NSE','TATAMOTORS'),self.alice.get_instrument_by_symbol('NSE','M&M')])
            print("subscribed") 

    def atm(self):
        instruments = pd.DataFrame(self.alice.search_instruments('NFO', 'BANKNIFTY'))
        options = instruments[:-3]
        expiry_index = 0
        expiry_date = sorted(options.expiry.drop_duplicates())[expiry_index]
        symbols=options[options['expiry']==expiry_date]
        symbols['symbol'].to_csv('tradingsymbol.csv',index=False,header=None)
        Strike=[float(symbols['symbol'][x].split(" ")[2]) for x in range(3,len(symbols['symbol']))]
        Price=34682.65 
        ATM=round(Price/100)*100.0
        CALL_ITM=[Strike[x] for x in range(len(Strike)) if Strike[x]<=ATM]
        CALL_OTM=[Strike[x] for x in range(len(Strike)) if Strike[x]>ATM]
        CALL=pd.DataFrame(CALL_ITM+CALL_OTM,columns=['CALL']).drop_duplicates().reset_index(drop=True)
        PUT_ITM=[Strike[x] for x in range(len(Strike)) if Strike[x]>ATM]
        PUT_OTM=[Strike[x] for x in range(len(Strike)) if Strike[x]<=ATM]
        PUT=pd.DataFrame(PUT_OTM+PUT_ITM,columns=['PUT']).drop_duplicates().reset_index(drop=True)
        print(CALL)
        print(PUT)
        pass

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
        'Authorization': 'Bearer 860288 tKUJ3O6AfakSQOcELkQ2eeygj9a17yGrp3gY15BLtDq1YiBa0egotYrpoX2qqHV7GWhjZf727DsKPPb3xReAgZp2pcDha5FsDYWJEmQr0pvAUPHO1BpxW341VFPKC3NhegCGA4hdWQk04YZCTPS3jv5tXDbokFWlWzUddPrevK0FdxbcKtxre1Y6q139ASeUYuL6Zim1cnRZhcS5jXSkhGcxUtcmNPbCT2IiH2PPEovUs0M0DiWIUcCbuTxhyuRq',
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)




#080 3521 5055

def socket():
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
    # a.alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
    #                       socket_error_callback=socket_error, subscription_callback=feed_data)

    while not socket_opened:
        pass

    #subscribe_list = [a.alice.get_instrument_by_token('INDICES', 26000)]
    #subscribe_list = [fo[0]]
    subscribe_list = [a.alice.get_instrument_by_symbol('INDICES', 'NIFTY BANK')]
    a.alice.subscribe(subscribe_list)
    print(datetime.now())
    #sleep(10)
    print(datetime.now())
    # unsubscribe_list = [alice.get_instrument_by_symbol("NSE", "RELIANCE")]
    # alice.unsubscribe(unsubscribe_list)
    # sleep(8)

    # Stop the websocket
    #a.alice.stop_websocket()
    #sleep(10)
    print(datetime.now())

    # Connect the socket after socket close
    a.alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                        socket_error_callback=socket_error, subscription_callback=feed_data)

def main():
    
    #alice.createSession()
    
    balance = a.alice.get_balance()
    profile = a.alice.get_profile()
    nb = a.alice.get_instrument_by_symbol('INDICES','NIFTY BANK')
    nb2 = a.alice.get_instrument_by_symbol('NFO', 'NIFTY BANK')
    #a.getContract()
    #a.orderPlacement()
    

    all_sensex_scrips = a.alice.search_instruments('NSE', 'NIFTY BANK')
    # o = a.alice.place_order(transaction_type = TransactionType.Buy, 
    #                     #instrument = a.alice.get_instrument_by_symbol('INDICES', 'NIFTY BANK'),
    #                     instrument = fo,
    #                     quantity = 25,
    #                     order_type = OrderType.Market,
    #                     product_type = ProductType.Intraday,
    #                     #price = 1.0,
    #                     trigger_price = None,
    #                     stop_loss = None,
    #                     square_off = None,
    #                     trailing_sl = None,
    #                     is_amo = False,
    #                     order_tag='order1')
    pass

a = AliceBlue()
# a.alice.get_session_id()
#oh = a.alice.get_order_history(1700000097915771)
#ot = a.alice.get_trade_book()
#hp = a.alice.get_holding_positions()
#h = a.alice.get_historical('BANKNIFTY', '2023-04-25', '2023-04-27', 'minute')
#a.getContract()
#a.atm()
#a.strike_price()
#a.web_socket()
fo = a.alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date="2023-05-11", is_fut=False,strike=41100, is_CE=False)
#main()
#socket()
pass