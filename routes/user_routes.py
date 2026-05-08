from fastapi import APIRouter, HTTPException
from models import User
from repositories.user_repository import UserRepository

router = APIRouter()

@router.post("/users", response_model=dict)
async def create_user(user: User):
    repo = UserRepository()
    db_user = repo.save(user)
    return {"id": db_user["_id"], "message": "User created"}

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    repo = UserRepository()
    user = repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users")
async def get_users():
    repo = UserRepository()
    users = repo.get_all()
    return users