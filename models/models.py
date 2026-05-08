from pydantic import BaseModel
from typing import List, Dict, Optional, Any


class User(BaseModel):
    available_days: List[str]
    goal: str
    level: Optional[str] = "Beginner"
    history: Optional[List[Dict]] = []  # For NN prediction


class WorkoutPlan(BaseModel):
    plan: Dict[str, Dict[str, Any]]  # day: {"workout": str, "exercises": List[str]}


class PlanComparison(BaseModel):
    csp_score: Dict[str, int]
    rule_score: Dict[str, int]
    verdict: str


class AdherencePrediction(BaseModel):
    adherence_probability: float
    difficulty_score: float