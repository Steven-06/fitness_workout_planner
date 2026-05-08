from pymongo import MongoClient
from pymongo.database import Database

MONGO_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_URL)
db: Database = client.fitness_tracker

# Collections
users_collection = db.users
workout_plans_collection = db.workout_plans
plan_comparisons_collection = db.plan_comparisons
adherence_predictions_collection = db.adherence_predictions
activity_logs_collection = db.activity_logs
workouts_collection = db.workouts