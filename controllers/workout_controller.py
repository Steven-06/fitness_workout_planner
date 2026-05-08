from fastapi import HTTPException
from models import User, WorkoutPlan, PlanComparison, AdherencePrediction
from services.workout_service import WorkoutService
from typing import Optional


class WorkoutController:
    def __init__(self):
        self.service = WorkoutService()

    def get_rule_based_plan(self, user: User) -> dict:
        plan, plan_id = self.service.generate_rule_based_plan(user)
        return {"plan": plan.plan, "plan_id": plan_id}

    def get_csp_plan(self, user: User) -> dict:
        plan, plan_id = self.service.generate_csp_plan(user)
        if plan is None:
            raise HTTPException(status_code=400, detail="No CSP solution found")
        return {"plan": plan.plan, "plan_id": plan_id}

    def adapt_plan(self, plan: WorkoutPlan, missed_day: str, user_id: str = "temp") -> dict:
        adapted_plan, plan_id = self.service.adapt_plan(plan, missed_day, user_id)
        return {"plan": adapted_plan.plan, "plan_id": plan_id}

    def compare_plans(self, user: User) -> dict:
        comparison, comparison_id = self.service.compare_plans(user)
        return {"comparison": comparison.dict(), "comparison_id": comparison_id}

    def predict_adherence(self, user: User, plan_id: Optional[str] = None) -> dict:
        prediction, prediction_id = self.service.predict_adherence(user, plan_id)
        return {"prediction": prediction.dict(), "prediction_id": prediction_id}

    # Additional methods for retrieving stored data
    def get_user_plans(self, user_id: str) -> list:
        return self.service.get_user_plans(user_id)

    def get_user_comparisons(self, user_id: str) -> list:
        return self.service.get_user_comparisons(user_id)

    def get_user_predictions(self, user_id: str) -> list:
        return self.service.get_user_predictions(user_id)

    def get_user_activity(self, user_id: str, limit: int = 20) -> list:
        return self.service.get_user_activity(user_id, limit)