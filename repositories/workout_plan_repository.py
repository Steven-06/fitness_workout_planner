from models.database import workout_plans_collection
from models import StoredWorkoutPlan
from typing import Optional, List
from bson import ObjectId


class WorkoutPlanRepository:
    def save(self, plan: StoredWorkoutPlan) -> dict:
        plan_dict = plan.dict()
        plan_dict["created_at"] = plan.created_at
        result = workout_plans_collection.insert_one(plan_dict)
        plan_dict["_id"] = str(result.inserted_id)
        return plan_dict

    def get(self, plan_id: str) -> Optional[dict]:
        plan = workout_plans_collection.find_one({"_id": ObjectId(plan_id)})
        if plan:
            plan["_id"] = str(plan["_id"])
        return plan

    def get_by_user(self, user_id: str) -> List[dict]:
        plans = list(workout_plans_collection.find({"user_id": user_id}))
        for plan in plans:
            plan["_id"] = str(plan["_id"])
        return plans

    def get_active_by_user(self, user_id: str) -> Optional[dict]:
        plan = workout_plans_collection.find_one({"user_id": user_id, "is_active": True})
        if plan:
            plan["_id"] = str(plan["_id"])
        return plan

    def update_active_status(self, plan_id: str, is_active: bool) -> bool:
        result = workout_plans_collection.update_one(
            {"_id": ObjectId(plan_id)},
            {"$set": {"is_active": is_active}}
        )
        return result.modified_count > 0

    def delete(self, plan_id: str) -> bool:
        result = workout_plans_collection.delete_one({"_id": ObjectId(plan_id)})
        return result.deleted_count > 0