from fastapi import HTTPException
from models import WorkoutPlan, PlanComparison, AdherencePrediction
from services.workout_service import WorkoutService
from typing import Optional


class WorkoutController:
    def __init__(self):
        self.service = WorkoutService()

    def get_rule_based_plan(self, user_id: str) -> dict:
        generated_workout_plan, workout_plan_id = self.service.generate_rule_based_plan(user_id)
        return {"plan": generated_workout_plan.plan, "plan_id": workout_plan_id}

    def get_csp_plan(self, user_id: str) -> dict:
        generated_workout_plan, workout_plan_id = self.service.generate_csp_plan(user_id)
        if generated_workout_plan is None:
            raise HTTPException(status_code=400, detail="No CSP solution found")
        return {"plan": generated_workout_plan.plan, "plan_id": workout_plan_id}

    def adapt_plan(self, plan_id: str, missed_day: str, user_id: str = "temp") -> dict:
        adapted_plan, plan_id = self.service.adapt_plan(plan_id, missed_day, user_id)
        return {"plan": adapted_plan.plan, "plan_id": plan_id}

    def compare_plans(self, user_id: str) -> dict:
        comparison, comparison_id = self.service.compare_plans(user_id)
        return {"comparison": comparison.dict(), "comparison_id": comparison_id}
    def predict_adherence(self, user_id: str, plan_id: Optional[str] = None) -> dict:
        prediction, prediction_id = self.service.predict_adherence(user_id, plan_id)
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