from pymongo import MongoClient
from datetime import datetime
# start = datetime(2023, 3, 1)
# end = datetime(2023, 3, 1)

class MongoDb:
    def __init__(self):
        self.HOST = 'localhost:27017'
        self.DATABASE = 'upstox'
        self.db_client = MongoClient(self.HOST)
        self.db = self.db_client[self.DATABASE]
        pass

    def insertMany(self, collection, data):
        col = self.db[collection]
        col.insert_many(data)

    def readAll(self, collection, start, end):
        print("hello 123")
        col = self.db[collection]
        data = col.find({"date": {"$gte": start, "$lt": end}})
        res = []
        for d in data:
            res.append(d)
        return res
    