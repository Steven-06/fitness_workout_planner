from models import User, WorkoutPlan, PlanComparison, AdherencePrediction
from planners.rule_based import generate_rule_based_plan
from planners.csp_planner import CSPWorkoutPlanner
from utils.adapt_plan import adapt_plan, compare_plans
from services.adherence_predictor import AdherencePredictor
from typing import Optional


class WorkoutService:
    def __init__(self):
        self.predictor = AdherencePredictor()

    def generate_rule_based_plan(self, user: User) -> WorkoutPlan:
        plan = generate_rule_based_plan(user.dict())
        return WorkoutPlan(plan=plan)

    def generate_csp_plan(self, user: User) -> Optional[WorkoutPlan]:
        planner = CSPWorkoutPlanner(user.dict())
        plan = planner.generate_plan()
        if plan is None:
            return None
        return WorkoutPlan(plan=plan)

    def adapt_plan(self, plan: WorkoutPlan, missed_day: str) -> WorkoutPlan:
        adapted = adapt_plan(plan.plan, missed_day)
        return WorkoutPlan(plan=adapted)

    def compare_plans(self, csp_plan: WorkoutPlan, rule_plan: WorkoutPlan, goal: str) -> PlanComparison:
        comparison = compare_plans(csp_plan.plan, rule_plan.plan, goal)
        return PlanComparison(**comparison)

    def predict_adherence(self, user: User) -> AdherencePrediction:
        prob = self.predictor.predict_adherence(user.dict())
        # Difficulty score: inverse of adherence
        difficulty = 1 - prob
        return AdherencePrediction(adherence_probability=prob, difficulty_score=difficulty)