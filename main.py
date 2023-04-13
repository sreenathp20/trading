from connect import Upstox

from db import MongoDb
from datetime import datetime
#mongo = MongoDb()

u = Upstox()

start = datetime(2023, 3, 1)
end = datetime(2023, 3, 1)

u.getAccessToken()
#u.getUserProfile()
#u.getUserFundsAndMargin()
#u.getPositions()
#u.getHoldings()
#u.historicalCandleData('nseindexniftybank', 'NSE_INDEX|Nifty Bank', '1minute', '2023-04-12', '2023-03-31')
#u.getAllCandleData('nifty50')
#df1 = u.getDfData('nifty50', start, end)
#u.placeOrder()

