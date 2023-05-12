from connect import Upstox

from db import MongoDb
from datetime import datetime, timedelta
mongo = MongoDb()

u = Upstox()

start = datetime(2023, 5, 11)
limit = 1
# start = datetime(2022, 10, 26)
# limit = 220
from tes import triple_exponential_smoothing_minimize

# 6341.549999999901 previous result total
#u.getAccessToken()
#u.getUserProfile()
#u.getUserFundsAndMargin()
#u.getPositions()
#u.getHoldings()
#u.historicalCandleData('nseindexniftybankPoint9', 'NSE_INDEX|Nifty Bank', '1minute', '2023-05-12', '2023-05-11' )
#u.getAllCandleData('nifty50')
#df1 = u.getDfData('nifty50', start, end)
#u.placeOrder()
#u.createDataFrame()
cnt = {"loss": 0, "profit": 0, "holiday": 0, "total": 0}
collection = 'nseindexniftybankPoint9'
df = u.getDf(collection, datetime(2022, 10, 25), datetime(2023, 5, 25))
alpha_final, beta_final, gamma_final = triple_exponential_smoothing_minimize(df['close'])
for i in range(limit):
    end = start + timedelta(days=1)
    print(start, end)
    #limit = u.backTest(collection, start, end, -49, alpha_final, beta_final, gamma_final)
    limit = u.backTestPred(collection, start, end, -49, alpha_final, beta_final, gamma_final)
    #limit = u.backTest5min('nseindexniftybankPoint9_5min', start, end, -49)
    #limit = u.backTest2('nseindexniftybankPoint9', start, end, -79)
    points = u.getProfitOrLoss('tnx_'+collection, start, end,-49)
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
    #u.get5minticks('nseindexniftybankPoint9', start, end)
    start = end


    

