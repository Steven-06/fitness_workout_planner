from backend.models.models import (
    User, WorkoutPlan, PlanComparison, AdherencePrediction,
    StoredWorkoutPlan, StoredPlanComparison, StoredAdherencePrediction, UserActivityLog,
    DayWorkout, PredictionMetrics, ActivityDetails, ComparisonResult
)
from backend.repositories import (
    UserRepository, WorkoutPlanRepository, PlanComparisonRepository,
    AdherencePredictionRepository, ActivityLogRepository, WorkoutRepository
)
from backend.planners.rule_based import generate_rule_based_plan
from backend.planners.csp_planner import CSPWorkoutPlanner
from backend.utils.adapt_plan import adapt_plan as adapt_workout_plan_data, compare_plans as compare_workout_plans
from backend.services.adherence_predictor import AdherencePredictor
from typing import Optional, Tuple
from datetime import datetime


class WorkoutService:
    def __init__(self):
        self.predictor = AdherencePredictor()
        self.user_repository = UserRepository()
        self.workout_repository = WorkoutRepository()
        self.workout_plan_repository = WorkoutPlanRepository()
        self.plan_comparison_repository = PlanComparisonRepository()
        self.adherence_prediction_repository = AdherencePredictionRepository()
        self.activity_log_repository = ActivityLogRepository()

    def _convert_to_typed_plan(self, raw_plan: dict) -> dict:
        """Convert raw plan dict to Dict[str, DayWorkout] format"""
        return {
            day: DayWorkout(
                workout=workout_data.get("workout") if isinstance(workout_data, dict) else workout_data["workout"],
                exercises=workout_data.get("exercises") if isinstance(workout_data, dict) else workout_data["exercises"]
            )
            for day, workout_data in raw_plan.items()
        }

    def generate_rule_based_plan(self, user: User) -> Tuple[WorkoutPlan, str]:
        generated_plan_data = generate_rule_based_plan(user.dict())
        typed_plan = self._convert_to_typed_plan(generated_plan_data)
        workout_plan = WorkoutPlan(plan=typed_plan)

        # Store the plan
        stored_plan = StoredWorkoutPlan(
            user_id=user.id or "temp",
            plan_type="rule_based",
            plan_data=typed_plan
        )
        saved_plan = self.workout_plan_repository.save(stored_plan)

        # Log activity
        self._log_activity(user.id or "temp", "plan_generated", ActivityDetails(
            action_type="plan_generated",
            details={
                "plan_type": "rule_based",
                "plan_id": saved_plan["_id"]
            }
        ))

        return workout_plan, saved_plan["_id"]

    def generate_csp_plan(self, user: User) -> Tuple[Optional[WorkoutPlan], Optional[str]]:
        planner = CSPWorkoutPlanner(user.dict())
        generated_plan_data = planner.generate_plan()
        if generated_plan_data is None:
            return None, None

        typed_plan = self._convert_to_typed_plan(generated_plan_data)
        workout_plan = WorkoutPlan(plan=typed_plan)

        # Store the plan
        stored_plan = StoredWorkoutPlan(
            user_id=user.id or "temp",
            plan_type="csp",
            plan_data=typed_plan
        )
        saved_plan = self.workout_plan_repository.save(stored_plan)

        # Log activity
        self._log_activity(user.id or "temp", "plan_generated", ActivityDetails(
            action_type="plan_generated",
            details={
                "plan_type": "csp",
                "plan_id": saved_plan["_id"]
            }
        ))

        return workout_plan, saved_plan["_id"]

    def adapt_plan(self, plan: WorkoutPlan, missed_day: str, user_id: str = "temp") -> Tuple[WorkoutPlan, str]:
        # Convert DayWorkout objects to dicts for the adapter function
        plan_dict = {day: day_workout.dict() for day, day_workout in plan.plan.items()}
        adapted_plan_data = adapt_workout_plan_data(plan_dict, missed_day)
        typed_plan = self._convert_to_typed_plan(adapted_plan_data)
        workout_plan = WorkoutPlan(plan=typed_plan)

        # Store the adapted plan
        stored_plan = StoredWorkoutPlan(
            user_id=user_id,
            plan_type="adapted",
            plan_data=typed_plan
        )
        saved_plan = self.workout_plan_repository.save(stored_plan)

        # Log activity
        self._log_activity(user_id, "plan_adapted", ActivityDetails(
            action_type="plan_adapted",
            details={
                "missed_day": missed_day,
                "plan_id": saved_plan["_id"]
            }
        ))

        return workout_plan, saved_plan["_id"]

    def compare_plans(self, user: User) -> Tuple[PlanComparison, str]:
        rule_workout_plan, rule_plan_id = self.generate_rule_based_plan(user)
        csp_workout_plan, csp_plan_id = self.generate_csp_plan(user)

        if csp_workout_plan is None:
            raise ValueError("CSP plan generation failed")

        # Convert DayWorkout objects to dicts for the comparison function
        csp_plan_dict = {day: day_workout.dict() for day, day_workout in csp_workout_plan.plan.items()}
        rule_plan_dict = {day: day_workout.dict() for day, day_workout in rule_workout_plan.plan.items()}
        comparison_result = compare_workout_plans(csp_plan_dict, rule_plan_dict, user.goal)
        plan_comparison = PlanComparison(
            csp_score=comparison_result.csp_score,
            rule_score=comparison_result.rule_score,
            verdict=comparison_result.verdict
        )

        # Store the comparison
        stored_comparison = StoredPlanComparison(
            user_id=user.id or "temp",
            csp_plan_id=csp_plan_id,
            rule_plan_id=rule_plan_id,
            comparison_data=comparison_result
        )
        saved_comparison = self.plan_comparison_repository.save(stored_comparison)

        # Log activity
        self._log_activity(user.id or "temp", "plans_compared", ActivityDetails(
            action_type="plans_compared",
            details={
                "comparison_id": saved_comparison["_id"],
                "csp_plan_id": csp_plan_id,
                "rule_plan_id": rule_plan_id
            }
        ))

        return plan_comparison, saved_comparison["_id"]

    def _enrich_plan_for_prediction(self, plan_id: Optional[str], user_level: str) -> list:
        """Turn a stored plan's day->category mapping into [{duration_minutes, intensity}, ...]
        by looking up each day's Workout doc. Skips Rest days (they don't count
        toward perceived training load)."""
        if not plan_id:
            return []
        stored_plan = self.workout_plan_repository.get(plan_id)
        if not stored_plan:
            return []

        enriched = []
        for day, day_workout in (stored_plan.get("plan_data") or {}).items():
            category = day_workout.get("workout") if isinstance(day_workout, dict) else None
            if not category or category == "Rest":
                continue
            workout_doc = self.workout_repository.get_by_category_and_level(category, user_level)
            if workout_doc:
                enriched.append({
                    "duration_minutes": workout_doc.get("duration_minutes", 30),
                    "intensity": workout_doc.get("intensity", "medium"),
                })
        return enriched

    def predict_adherence(self, user: User, plan_id: Optional[str] = None) -> Tuple[AdherencePrediction, str]:
        plan_workouts = self._enrich_plan_for_prediction(plan_id, user.level or "Beginner")
        adherence_probability = self.predictor.predict_adherence(user.dict(), plan_workouts)
        difficulty = 1 - adherence_probability
        prediction = AdherencePrediction(adherence_probability=adherence_probability, difficulty_score=difficulty)

        # Store the prediction
        prediction_metrics = PredictionMetrics(
            adherence_probability=adherence_probability,
            difficulty_score=difficulty
        )
        stored_prediction = StoredAdherencePrediction(
            user_id=user.id or "temp",
            plan_id=plan_id,
            prediction_data=prediction_metrics
        )
        saved_prediction = self.adherence_prediction_repository.save(stored_prediction)

        # Log activity
        self._log_activity(user.id or "temp", "prediction_made", ActivityDetails(
            action_type="prediction_made",
            details={
                "prediction_id": saved_prediction["_id"],
                "plan_id": plan_id,
                "adherence_probability": adherence_probability
            }
        ))

        return prediction, saved_prediction["_id"]

    def _log_activity(self, user_id: str, action: str, activity_details: ActivityDetails):
        log = UserActivityLog(
            user_id=user_id,
            action=action,
            details=activity_details
        )
        self.activity_log_repository.save(log)

    # Additional methods for retrieving stored data
    def get_user_plans(self, user_id: str) -> list:
        return self.workout_plan_repository.get_by_user(user_id)

    def get_user_comparisons(self, user_id: str) -> list:
        return self.plan_comparison_repository.get_by_user(user_id)

    def get_user_predictions(self, user_id: str) -> list:
        return self.adherence_prediction_repository.get_by_user(user_id)

    def get_user_activity(self, user_id: str, limit: int = 20) -> list:
        return self.activity_log_repository.get_by_user(user_id, limit)