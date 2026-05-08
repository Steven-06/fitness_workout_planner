from fastapi import HTTPException
from models.models import User, WorkoutPlan, PlanComparison, AdherencePrediction
from services.workout_service import WorkoutService


class WorkoutController:
    def __init__(self):
        self.service = WorkoutService()

    def get_rule_based_plan(self, user: User) -> WorkoutPlan:
        return self.service.generate_rule_based_plan(user)

    def get_csp_plan(self, user: User) -> WorkoutPlan:
        plan = self.service.generate_csp_plan(user)
        if plan is None:
            raise HTTPException(status_code=400, detail="No CSP solution found")
        return plan

    def adapt_plan(self, plan: WorkoutPlan, missed_day: str) -> WorkoutPlan:
        return self.service.adapt_plan(plan, missed_day)

    def compare_plans(self, user: User) -> PlanComparison:
        rule_plan = self.service.generate_rule_based_plan(user)
        csp_plan = self.service.generate_csp_plan(user)
        if csp_plan is None:
            raise HTTPException(status_code=400, detail="No CSP solution found")
        return self.service.compare_plans(csp_plan, rule_plan, user.goal)

    def predict_adherence(self, user: User) -> AdherencePrediction:
        return self.service.predict_adherence(user)