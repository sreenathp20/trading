from db import MongoDb
mongo = MongoDb()
import pandas as pd
from datetime import datetime, timedelta
from time import sleep
from connect import Upstox
from pya3 import *
from alice import AliceBlue
from tes import triple_exponential_smoothing_minimize, triple_exponential_smoothing

import order
o = order.Order()
collection = "niftybankticks"
today = datetime.today()
#today = datetime(2023,4,27)
daystart = datetime(year=today.year, month=today.month, 
                    day=today.day, hour=0, minute=0, second=0) 

start = daystart
end = start + timedelta(days=1)
new_data = o.checkLatestTick(collection, start, end)
latest_data = new_data[0]
o.sellStock(latest_data, 'DOWN', collection)