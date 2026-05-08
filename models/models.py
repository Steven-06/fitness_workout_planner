from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class User(BaseModel):
    available_days: List[str]
    goal: str
    level: Optional[str] = "Beginner"
    history: List[Dict] = Field(default_factory=list)  # For NN prediction


class WorkoutPlan(BaseModel):
    plan: Dict[str, Dict[str, Any]]  # day: {"workout": str, "exercises": List[str]}


class PlanComparison(BaseModel):
    csp_score: Dict[str, int]
    rule_score: Dict[str, int]
    verdict: str


class AdherencePrediction(BaseModel):
    adherence_probability: float
    difficulty_score: float


# Database Models (for storage)
class StoredWorkoutPlan(BaseModel):
    user_id: str
    plan_type: str  # "csp" or "rule_based"
    plan_data: Dict[str, Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class StoredPlanComparison(BaseModel):
    user_id: str
    csp_plan_id: Optional[str] = None
    rule_plan_id: Optional[str] = None
    comparison_data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StoredAdherencePrediction(BaseModel):
    user_id: str
    plan_id: Optional[str] = None
    prediction_data: Dict[str, float]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserActivityLog(BaseModel):
    user_id: str
    action: str  # "plan_generated", "plan_adapted", "prediction_made", etc.
    details: Dict[str, Any]
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