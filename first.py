import requests

r = requests.get('https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyStockWatch.json').json()

print(r)