from backend.models.database import plan_comparisons_collection
from backend.models import StoredPlanComparison
from typing import Optional, List
from bson import ObjectId


class PlanComparisonRepository:
    def save(self, comparison: StoredPlanComparison) -> dict:
        comparison_dict = comparison.dict()
        comparison_dict["created_at"] = comparison.created_at
        result = plan_comparisons_collection.insert_one(comparison_dict)
        comparison_dict["_id"] = str(result.inserted_id)
        return comparison_dict

    def get(self, comparison_id: str) -> Optional[dict]:
        comparison = plan_comparisons_collection.find_one({"_id": ObjectId(comparison_id)})
        if comparison:
            comparison["_id"] = str(comparison["_id"])
        return comparison

    def get_by_user(self, user_id: str) -> List[dict]:
        comparisons = list(plan_comparisons_collection.find({"user_id": user_id}))
        for comparison in comparisons:
            comparison["_id"] = str(comparison["_id"])
        return comparisons

    def get_latest_by_user(self, user_id: str) -> Optional[dict]:
        comparison = plan_comparisons_collection.find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        if comparison:
            comparison["_id"] = str(comparison["_id"])
        return comparison

    def delete(self, comparison_id: str) -> bool:
        result = plan_comparisons_collection.delete_one({"_id": ObjectId(comparison_id)})
        return result.deleted_count > 0