from backend.models.database import activity_logs_collection
from backend.models import UserActivityLog
from typing import Optional, List
from bson import ObjectId


class ActivityLogRepository:
    def save(self, log: UserActivityLog) -> dict:
        log_dict = log.dict()
        log_dict["timestamp"] = log.timestamp
        result = activity_logs_collection.insert_one(log_dict)
        log_dict["_id"] = str(result.inserted_id)
        return log_dict

    def get(self, log_id: str) -> Optional[dict]:
        log = activity_logs_collection.find_one({"_id": ObjectId(log_id)})
        if log:
            log["_id"] = str(log["_id"])
        return log

    def get_by_user(self, user_id: str, limit: int = 50) -> List[dict]:
        logs = list(activity_logs_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit))
        for log in logs:
            log["_id"] = str(log["_id"])
        return logs

    def get_by_action(self, action: str, limit: int = 100) -> List[dict]:
        logs = list(activity_logs_collection.find({"action": action}).sort("timestamp", -1).limit(limit))
        for log in logs:
            log["_id"] = str(log["_id"])
        return logs

    def get_recent_activity(self, limit: int = 100) -> List[dict]:
        logs = list(activity_logs_collection.find().sort("timestamp", -1).limit(limit))
        for log in logs:
            log["_id"] = str(log["_id"])
        return logs

    def delete(self, log_id: str) -> bool:
        result = activity_logs_collection.delete_one({"_id": ObjectId(log_id)})
        return result.deleted_count > 0