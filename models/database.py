from pymongo import MongoClient
from pymongo.database import Database

MONGO_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_URL)
db: Database = client.fitness_tracker

# Collections
users_collection = db.users