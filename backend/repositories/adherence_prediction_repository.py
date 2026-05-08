from backend.models.database import adherence_predictions_collection
from backend.models import StoredAdherencePrediction
from typing import Optional, List
from bson import ObjectId


class AdherencePredictionRepository:
    def save(self, prediction: StoredAdherencePrediction) -> dict:
        prediction_dict = prediction.dict()
        prediction_dict["created_at"] = prediction.created_at
        result = adherence_predictions_collection.insert_one(prediction_dict)
        prediction_dict["_id"] = str(result.inserted_id)
        return prediction_dict

    def get(self, prediction_id: str) -> Optional[dict]:
        prediction = adherence_predictions_collection.find_one({"_id": ObjectId(prediction_id)})
        if prediction:
            prediction["_id"] = str(prediction["_id"])
        return prediction

    def get_by_user(self, user_id: str) -> List[dict]:
        predictions = list(adherence_predictions_collection.find({"user_id": user_id}))
        for prediction in predictions:
            prediction["_id"] = str(prediction["_id"])
        return predictions

    def get_by_plan(self, plan_id: str) -> List[dict]:
        predictions = list(adherence_predictions_collection.find({"plan_id": plan_id}))
        for prediction in predictions:
            prediction["_id"] = str(prediction["_id"])
        return predictions

    def get_latest_by_user(self, user_id: str) -> Optional[dict]:
        prediction = adherence_predictions_collection.find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        if prediction:
            prediction["_id"] = str(prediction["_id"])
        return prediction

    def delete(self, prediction_id: str) -> bool:
        result = adherence_predictions_collection.delete_one({"_id": ObjectId(prediction_id)})
        return result.deleted_count > 0