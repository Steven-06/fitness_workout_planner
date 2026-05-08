from models import (
    User, WorkoutPlan, PlanComparison, AdherencePrediction,
    StoredWorkoutPlan, StoredPlanComparison, StoredAdherencePrediction, UserActivityLog
)
from repositories import (
    UserRepository, WorkoutPlanRepository, PlanComparisonRepository,
    AdherencePredictionRepository, ActivityLogRepository
)
from planners.rule_based import generate_rule_based_plan
from planners.csp_planner import CSPWorkoutPlanner
from utils.adapt_plan import adapt_plan, compare_plans
from services.adherence_predictor import AdherencePredictor
from typing import Optional, Tuple
from datetime import datetime


class WorkoutService:
    def __init__(self):
        self.predictor = AdherencePredictor()
        self.user_repo = UserRepository()
        self.plan_repo = WorkoutPlanRepository()
        self.comparison_repo = PlanComparisonRepository()
        self.prediction_repo = AdherencePredictionRepository()
        self.activity_repo = ActivityLogRepository()

    def generate_rule_based_plan(self, user: User) -> Tuple[WorkoutPlan, str]:
        plan = generate_rule_based_plan(user.dict())
        workout_plan = WorkoutPlan(plan=plan)

        # Store the plan
        stored_plan = StoredWorkoutPlan(
            user_id=user.id if hasattr(user, 'id') else "temp",
            plan_type="rule_based",
            plan_data=plan
        )
        saved_plan = self.plan_repo.save(stored_plan)

        # Log activity
        self._log_activity(user.id if hasattr(user, 'id') else "temp", "plan_generated", {
            "plan_type": "rule_based",
            "plan_id": saved_plan["_id"]
        })

        return workout_plan, saved_plan["_id"]

    def generate_csp_plan(self, user: User) -> Tuple[Optional[WorkoutPlan], Optional[str]]:
        planner = CSPWorkoutPlanner(user.dict())
        plan = planner.generate_plan()
        if plan is None:
            return None, None

        workout_plan = WorkoutPlan(plan=plan)

        # Store the plan
        stored_plan = StoredWorkoutPlan(
            user_id=user.id if hasattr(user, 'id') else "temp",
            plan_type="csp",
            plan_data=plan
        )
        saved_plan = self.plan_repo.save(stored_plan)

        # Log activity
        self._log_activity(user.id if hasattr(user, 'id') else "temp", "plan_generated", {
            "plan_type": "csp",
            "plan_id": saved_plan["_id"]
        })

        return workout_plan, saved_plan["_id"]

    def adapt_plan(self, plan: WorkoutPlan, missed_day: str, user_id: str = "temp") -> Tuple[WorkoutPlan, str]:
        adapted = adapt_plan(plan.plan, missed_day)
        workout_plan = WorkoutPlan(plan=adapted)

        # Store the adapted plan
        stored_plan = StoredWorkoutPlan(
            user_id=user_id,
            plan_type="adapted",
            plan_data=adapted
        )
        saved_plan = self.plan_repo.save(stored_plan)

        # Log activity
        self._log_activity(user_id, "plan_adapted", {
            "missed_day": missed_day,
            "plan_id": saved_plan["_id"]
        })

        return workout_plan, saved_plan["_id"]

    def compare_plans(self, user: User) -> Tuple[PlanComparison, str]:
        rule_plan, rule_plan_id = self.generate_rule_based_plan(user)
        csp_plan, csp_plan_id = self.generate_csp_plan(user)

        if csp_plan is None:
            raise ValueError("CSP plan generation failed")

        comparison = compare_plans(csp_plan.plan, rule_plan.plan, user.goal)
        plan_comparison = PlanComparison(**comparison)

        # Store the comparison
        stored_comparison = StoredPlanComparison(
            user_id=user.id if hasattr(user, 'id') else "temp",
            csp_plan_id=csp_plan_id,
            rule_plan_id=rule_plan_id,
            comparison_data=comparison
        )
        saved_comparison = self.comparison_repo.save(stored_comparison)

        # Log activity
        self._log_activity(user.id if hasattr(user, 'id') else "temp", "plans_compared", {
            "comparison_id": saved_comparison["_id"],
            "csp_plan_id": csp_plan_id,
            "rule_plan_id": rule_plan_id
        })

        return plan_comparison, saved_comparison["_id"]

    def predict_adherence(self, user: User, plan_id: Optional[str] = None) -> Tuple[AdherencePrediction, str]:
        prob = self.predictor.predict_adherence(user.dict())
        difficulty = 1 - prob
        prediction = AdherencePrediction(adherence_probability=prob, difficulty_score=difficulty)

        # Store the prediction
        stored_prediction = StoredAdherencePrediction(
            user_id=user.id if hasattr(user, 'id') else "temp",
            plan_id=plan_id,
            prediction_data={"adherence_probability": prob, "difficulty_score": difficulty}
        )
        saved_prediction = self.prediction_repo.save(stored_prediction)

        # Log activity
        self._log_activity(user.id if hasattr(user, 'id') else "temp", "prediction_made", {
            "prediction_id": saved_prediction["_id"],
            "plan_id": plan_id,
            "adherence_probability": prob
        })

        return prediction, saved_prediction["_id"]

    def _log_activity(self, user_id: str, action: str, details: dict):
        log = UserActivityLog(
            user_id=user_id,
            action=action,
            details=details
        )
        self.activity_repo.save(log)

    # Additional methods for retrieving stored data
    def get_user_plans(self, user_id: str) -> list:
        return self.plan_repo.get_by_user(user_id)

    def get_user_comparisons(self, user_id: str) -> list:
        return self.comparison_repo.get_by_user(user_id)

    def get_user_predictions(self, user_id: str) -> list:
        return self.prediction_repo.get_by_user(user_id)

    def get_user_activity(self, user_id: str, limit: int = 20) -> list:
        return self.activity_repo.get_by_user(user_id, limit)