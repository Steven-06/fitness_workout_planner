from models.database import users_collection
from models import User
from typing import Optional, List
from bson import ObjectId


class UserRepository:
    def save(self, user: User) -> dict:
        user_dict = user.dict()
        result = users_collection.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        return user_dict

    def get(self, user_id: str) -> Optional[dict]:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user

    def get_all(self) -> List[dict]:
        users = list(users_collection.find())
        for user in users:
            user["_id"] = str(user["_id"])
        return users

    def delete(self, user_id: str) -> bool:
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0