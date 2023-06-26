from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['upstox']
kite = client['kite']