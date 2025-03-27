import pymongo
import os

url = SECRET_KEY = os.getenv("MONGO_URL")


client = pymongo.MongoClient(url)


db = client["flashlingo"]
