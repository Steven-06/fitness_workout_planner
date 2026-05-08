from fastapi import APIRouter, HTTPException
from models.models import User, WorkoutPlan, PlanComparison, AdherencePrediction
from controllers.workout_controller import WorkoutController

router = APIRouter()
controller = WorkoutController()

@router.post("/plan/rule-based", response_model=WorkoutPlan)
async def generate_rule_based_plan(user: User):
    return controller.get_rule_based_plan(user)

@router.post("/plan/csp", response_model=WorkoutPlan)
async def generate_csp_plan(user: User):
    return controller.get_csp_plan(user)

@router.post("/plan/adapt", response_model=WorkoutPlan)
async def adapt_workout_plan(plan: WorkoutPlan, missed_day: str):
    return controller.adapt_plan(plan, missed_day)

@router.post("/plan/compare", response_model=PlanComparison)
async def compare_plans(user: User):
    return controller.compare_plans(user)

@router.post("/predict/adherence", response_model=AdherencePrediction)
async def predict_adherence(user: User):
    return controller.predict_adherence(user)