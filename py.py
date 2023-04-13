import websocket
import json
import buffer
import time
def on_message(wsapp, message):
    print(message)

def on_ping(wsapp, message):
    print("Got a ping! A pong reply has already been automatically sent.")
def on_pong(wsapp, message):
    print("Got a pong! No need to respond")

headers = {
    "Api-Version": "2.0",
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI1NkE0UEYiLCJqdGkiOiI2NDM0MWYzYTJhZTU4YzdiNzFhZjgyNjAiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNBY3RpdmUiOnRydWUsInNjb3BlIjpbImludGVyYWN0aXZlIiwiaGlzdG9yaWNhbCJdLCJpYXQiOjE2ODExMzc0NjYsImlzcyI6InVkYXBpLWdhdGV3YXktc2VydmljZSIsImV4cCI6MTY4MTIyNTY2Nn0.9ivIfeLQhkMiOopULNZ9767dpi9m3GfkJY9fIC5lhJo"
  }

def on_open(wsapp):
    time.sleep(1)
    print("on_open")
    data = {
      "guid": "someguid",
      "method": "sub",
      "data": {
        "mode": "full",
        "instrumentKeys": ["NSE_INDEX|Nifty Bank"]
      }
    }
    time.sleep(1)
    wsapp.send(buffer(json.dumps(data)))

wsapp = websocket.WebSocketApp("wss://api-v2.upstox.com/feed/market-data-feed", header=headers, on_open=on_open, on_message=on_message)





wsapp.run_forever() 