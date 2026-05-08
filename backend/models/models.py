from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


# Day-level workout structure
class DayWorkout(BaseModel):
    """Single day's workout assignment"""
    workout: str  # e.g., "Cardio", "Upper Body", "Rest"
    exercises: List[str]  # List of exercise names


# Plan scoring/comparison structures
class PlanScore(BaseModel):
    """Metrics for evaluating a workout plan"""
    consecutive_conflicts: int  # Number of consecutive same workouts
    rest_days: int  # Number of rest days
    goal_match_score: int  # How well plan aligns with user goal


# Prediction/adherence structures
class PredictionMetrics(BaseModel):
    """Adherence prediction metrics"""
    adherence_probability: float  # 0-1 probability user will stick to plan
    difficulty_score: float  # 0-1 difficulty assessment


# Activity tracking structures
class ActivityDetails(BaseModel):
    """Generic activity log details"""
    action_type: str  # Type of action that occurred
    details: Dict = Field(default_factory=dict)  # Action-specific details


class ComparisonResult(BaseModel):
    """Complete comparison between two plans"""
    csp_score: PlanScore
    rule_score: PlanScore
    verdict: str


class User(BaseModel):
    
    name: str
    available_days: List[str]
    goal: str
    level: Optional[str] = "Beginner"
    id: Optional[str] = None
    workout_history: List[PredictionMetrics] = Field(default_factory=list)  # Historical adherence for NN prediction


class WorkoutPlan(BaseModel):
    plan: Dict[str, DayWorkout]  # day: {workout, exercises}


class PlanComparison(BaseModel):
    csp_score: PlanScore
    rule_score: PlanScore
    verdict: str


class AdherencePrediction(BaseModel):
    adherence_probability: float
    difficulty_score: float


# Database Models (for storage)
class StoredWorkoutPlan(BaseModel):
    user_id: str
    plan_type: str  # "csp" or "rule_based"
    plan_data: Dict[str, DayWorkout]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class StoredPlanComparison(BaseModel):
    user_id: str
    csp_plan_id: Optional[str] = None
    rule_plan_id: Optional[str] = None
    comparison_data: ComparisonResult
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StoredAdherencePrediction(BaseModel):
    user_id: str
    plan_id: Optional[str] = None
    prediction_data: PredictionMetrics
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserActivityLog(BaseModel):
    user_id: str
    action: str  # "plan_generated", "plan_adapted", "prediction_made", etc.
    details: ActivityDetails
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Workout Models
class Workout(BaseModel):
    category: str  # "Cardio", "Upper Body", "Lower Body", "Full Body", "Rest"
    level: str  # "Beginner", "Intermediate"
    exercises: List[str]  # List of exercise names
    duration_minutes: int  # How long the workout takes
    intensity: str  # "low", "medium", "high"
    calories_burned: Optional[int] = None  # Estimated calories
    equipment_needed: List[str] = Field(default_factory=list)  # Equipment required
    muscle_groups: List[str] = Field(default_factory=list)  # Targeted muscle groups
    benefits: List[str] = Field(default_factory=list)  # Workout benefits
    description: Optional[str] = None  # Additional details


class StoredWorkout(BaseModel):
    category: str
    level: str
    exercises: List[str]
    duration_minutes: int
    intensity: str
    calories_burned: Optional[int] = None
    equipment_needed: List[str] = Field(default_factory=list)
    muscle_groups: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)