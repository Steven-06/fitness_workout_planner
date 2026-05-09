from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from models import WorkoutPlan, PlanComparison, AdherencePrediction
from controllers.workout_controller import WorkoutController
from repositories import WorkoutRepository

router = APIRouter()
controller = WorkoutController()
workout_repository = WorkoutRepository()

class UserIdRequest(BaseModel):
    user_id: str


@router.post("/plan/rule-based", response_model=dict)
async def generate_rule_based_plan(req: UserIdRequest):
    return controller.get_rule_based_plan(req.user_id)

@router.post("/plan/csp", response_model=dict)
async def generate_csp_plan(req: UserIdRequest):
    return controller.get_csp_plan(req.user_id)

class AdaptRequest(BaseModel):
    plan_id: str
    missed_day: str
    user_id: str


@router.post("/plan/adapt", response_model=dict)
async def adapt_workout_plan(req: AdaptRequest):
    return controller.adapt_plan(req.plan_id, req.missed_day, req.user_id)

@router.post("/plan/compare", response_model=dict)
async def compare_plans(req: UserIdRequest):
    return controller.compare_plans(req.user_id)

class PredictRequest(BaseModel):
    user_id: str
    plan_id: Optional[str] = None


@router.post("/predict/adherence", response_model=dict)
async def predict_adherence(req: PredictRequest):
    return controller.predict_adherence(req.user_id, req.plan_id)

# Additional routes for retrieving stored data
@router.get("/users/{user_id}/plans")
async def get_user_plans(user_id: str):
    return {"plans": controller.get_user_plans(user_id)}

@router.get("/users/{user_id}/comparisons")
async def get_user_comparisons(user_id: str):
    return {"comparisons": controller.get_user_comparisons(user_id)}

@router.get("/users/{user_id}/predictions")
async def get_user_predictions(user_id: str):
    return {"predictions": controller.get_user_predictions(user_id)}

@router.get("/users/{user_id}/activity")
async def get_user_activity(user_id: str, limit: int = 20):
    return {"activity": controller.get_user_activity(user_id, limit)}

# Workout management endpoints
@router.get("/workouts")
async def get_all_workouts():
    """Get all available workouts"""
    workouts = workout_repository.get_all()
    return {"workouts": workouts}

@router.get("/workouts/{category}/{level}")
async def get_workout(category: str, level: str):
    """Get a specific workout by category and level"""
    workout = workout_repository.get_by_category_and_level(category, level)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"workout": workout}

@router.get("/workouts/category/{category}")
async def get_workouts_by_category(category: str):
    """Get all workouts in a category"""
    workouts = workout_repository.get_all_by_category(category)
    return {"workouts": workouts}

@router.get("/workouts/level/{level}")
async def get_workouts_by_level(level: str):
    """Get all workouts for a level"""
    workouts = workout_repository.get_all_by_level(level)
    return {"workouts": workouts}