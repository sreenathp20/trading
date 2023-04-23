from connect import Upstox

from db import MongoDb
from datetime import datetime, timedelta
#mongo = MongoDb()

u = Upstox()

start = datetime(2023, 4, 1)
limit = 31
# start = datetime(2022, 10, 16)
# limit = 191





#u.getAccessToken()
#u.getUserProfile()
#u.getUserFundsAndMargin()
#u.getPositions()
#u.getHoldings()
#u.historicalCandleData('nseindexniftybankPoint9', 'NSE_INDEX|Nifty Bank', '1minute', '2023-04-27', '2022-10-16' )
#u.getAllCandleData('nifty50')
#df1 = u.getDfData('nifty50', start, end)
#u.placeOrder()
#u.createDataFrame()
cnt = {"loss": 0, "profit": 0, "holiday": 0, "total": 0}
for i in range(limit):
    end = start + timedelta(days=1)
    print(start, end)
    limit = u.backTest('nseindexniftybankPoint9', start, end, -49)
    points = u.getProfitOrLoss('transactions_nseindexniftybankPoint9', start, end,-49)
    data = {"profit": [], "loss": []}
    if points > 0:
        cnt["profit"] += 1
        data["profit"].append({"date": start, "value": points, "gain": "profit"})
    if points < 0:
        cnt["loss"] += 1
        data["loss"].append({"date": start, "value": points, "gain": "loss"})
    if points == 0:
        cnt["holiday"] += 1
    cnt["total"] += points   
    #u.insertProfitOrLoss(data)
    print(cnt) 
    print("=============================================================")
    start = end
    

