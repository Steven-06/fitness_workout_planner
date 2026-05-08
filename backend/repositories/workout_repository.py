from backend.models.database import workouts_collection
from backend.models import Workout, StoredWorkout
from typing import Optional, List
from bson import ObjectId


class WorkoutRepository:
    def save(self, workout: StoredWorkout) -> dict:
        workout_dict = workout.dict()
        workout_dict["created_at"] = workout.created_at
        result = workouts_collection.insert_one(workout_dict)
        workout_dict["_id"] = str(result.inserted_id)
        return workout_dict

    def get(self, workout_id: str) -> Optional[dict]:
        workout = workouts_collection.find_one({"_id": ObjectId(workout_id)})
        if workout:
            workout["_id"] = str(workout["_id"])
        return workout

    def get_by_category_and_level(self, category: str, level: str) -> Optional[dict]:
        workout = workouts_collection.find_one({"category": category, "level": level})
        if workout:
            workout["_id"] = str(workout["_id"])
        return workout

    def get_all_by_category(self, category: str) -> List[dict]:
        workouts = list(workouts_collection.find({"category": category}))
        for workout in workouts:
            workout["_id"] = str(workout["_id"])
        return workouts

    def get_all_by_level(self, level: str) -> List[dict]:
        workouts = list(workouts_collection.find({"level": level}))
        for workout in workouts:
            workout["_id"] = str(workout["_id"])
        return workouts

    def get_all(self) -> List[dict]:
        workouts = list(workouts_collection.find())
        for workout in workouts:
            workout["_id"] = str(workout["_id"])
        return workouts

    def delete(self, workout_id: str) -> bool:
        result = workouts_collection.delete_one({"_id": ObjectId(workout_id)})
        return result.deleted_count > 0

    def clear_all(self) -> int:
        result = workouts_collection.delete_many({})
        return result.deleted_count