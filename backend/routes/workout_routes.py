from fastapi import APIRouter, HTTPException
from models import User, WorkoutPlan, PlanComparison, AdherencePrediction
from controllers.workout_controller import WorkoutController
from repositories import WorkoutRepository

router = APIRouter()
controller = WorkoutController()
workout_repository = WorkoutRepository()

@router.post("/plan/rule-based", response_model=dict)
async def generate_rule_based_plan(user: User):
    return controller.get_rule_based_plan(user)

@router.post("/plan/csp", response_model=dict)
async def generate_csp_plan(user: User):
    return controller.get_csp_plan(user)

@router.post("/plan/adapt", response_model=dict)
async def adapt_workout_plan(plan: WorkoutPlan, missed_day: str, user_id: str = "temp"):
    return controller.adapt_plan(plan, missed_day, user_id)

@router.post("/plan/compare", response_model=dict)
async def compare_plans(user: User):
    return controller.compare_plans(user)

@router.post("/predict/adherence", response_model=dict)
async def predict_adherence(user: User, plan_id: str = None):
    return controller.predict_adherence(user, plan_id)

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