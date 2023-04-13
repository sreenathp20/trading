import websocket
import _thread
import time
import rel
from connect import Upstox

u = Upstox()

def on_message(ws, message):
    print(message, " ==================================================== ")
    pass

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api-v2.upstox.com/feed/market-data-feed", header=            {"Api-Version": "2.0","Authorization": "Bearer " + u.readAccessToken()},
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()