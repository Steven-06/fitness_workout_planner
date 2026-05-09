import os
import json
from typing import List, Optional
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib


GOAL_MAP = {
    "Lose Weight":       "weight_loss",
    "Build Muscle":      "muscle_gain",
    "Improve Endurance": "endurance",
    "General Fitness":   "general_fitness",
}
LEVEL_MAP = {"Beginner": "beginner", "Intermediate": "intermediate"}
INTENSITY_MAP = {"low": "low", "medium": "medium", "moderate": "medium", "high": "high"}

GOAL_VOCAB = ["weight_loss", "muscle_gain", "endurance", "general_fitness"]
LEVEL_VOCAB = ["beginner", "intermediate"]
INTENSITY_VOCAB = ["low", "medium", "high"]

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "adherence_model.joblib")
SCALER_PATH = os.path.join(ARTIFACTS_DIR, "adherence_scaler.joblib")
META_PATH = os.path.join(ARTIFACTS_DIR, "adherence_meta.json")


def _one_hot(value: str, vocab: list) -> list:
    return [1.0 if value == v else 0.0 for v in vocab]


def _generate_synthetic(n: int = 4000, seed: int = 42):
    rng = np.random.default_rng(seed)

    available_time = rng.integers(15, 121, n).astype(float)
    sessions = rng.integers(1, 8, n).astype(float)
    intensity_idx = rng.integers(0, 3, n)
    intensity = np.array(INTENSITY_VOCAB)[intensity_idx]
    prev_completion = np.clip(rng.beta(5, 4, n), 0, 1)
    goal = np.array(GOAL_VOCAB)[rng.integers(0, 4, n)]
    level = np.array(LEVEL_VOCAB)[rng.integers(0, 2, n)]

    intensity_val = np.where(intensity == "low", 0.3,
                     np.where(intensity == "medium", 0.6, 0.9))
    base = np.where(level == "intermediate", 0.55, 0.45)

    overload = np.maximum(0, sessions - 5) * 0.08
    intensity_pen = np.where((level == "beginner") & (intensity_val >= 0.9), 0.18,
                     np.where(intensity_val >= 0.9, 0.06, 0.0))
    time_bonus = np.where((available_time >= 30) & (available_time <= 60), 0.06,
                  np.where(available_time > 90, -0.10,
                  np.where(available_time < 20, -0.05, 0.0)))
    goal_mod = np.where(goal == "weight_loss", -0.06,
                np.where(goal == "muscle_gain", 0.02,
                np.where(goal == "endurance", -0.02, 0.04)))

    score = base + 0.30 * prev_completion - overload - intensity_pen + time_bonus + goal_mod
    score = np.clip(score + rng.normal(0, 0.07, n), 0.05, 0.98)

    rows = []
    for i in range(n):
        rows.append(_encode_row(
            available_time[i], sessions[i], prev_completion[i],
            intensity[i], goal[i], level[i],
        ))
    X = np.array(rows, dtype=np.float32)
    y = score.astype(np.float32)
    return X, y


def _encode_row(available_time, sessions, prev_completion, intensity, goal, level):
    return [
        float(available_time),
        float(sessions),
        float(prev_completion),
        *_one_hot(intensity, INTENSITY_VOCAB),
        *_one_hot(goal, GOAL_VOCAB),
        *_one_hot(level, LEVEL_VOCAB),
    ]


def _extract_features(user: dict, plan_workouts: list, prev_completion_rate: float) -> list:
    durations = [w.get("duration_minutes", 30) for w in plan_workouts] or [30]
    avg_duration = float(np.mean(durations))

    intensities = [INTENSITY_MAP.get(str(w.get("intensity", "medium")).lower(), "medium")
                   for w in plan_workouts] or ["medium"]
    intensity = max(set(intensities), key=intensities.count)

    sessions = float(len(user.get("available_days") or []))
    goal = GOAL_MAP.get(user.get("goal"), "general_fitness")
    level = LEVEL_MAP.get(user.get("level"), "beginner")

    return _encode_row(avg_duration, sessions, prev_completion_rate,
                       intensity, goal, level)


def _history_to_completion_rate(workout_history) -> float:
    """Average past adherence_probability values; default to 0.5 if no history."""
    if not workout_history:
        return 0.5
    rates = []
    for h in workout_history:
        if isinstance(h, dict):
            rate = h.get("adherence_probability")
        else:
            rate = getattr(h, "adherence_probability", None)
        if rate is not None:
            rates.append(float(rate))
    return float(np.mean(rates)) if rates else 0.5


class AdherencePredictor:
    """Multi-layer perceptron (32, 16) regressor over 12 engineered features."""

    def __init__(self):
        self.model: Optional[MLPRegressor] = None
        self.scaler: Optional[StandardScaler] = None

    def train(self, n_samples: int = 4000, random_state: int = 42) -> dict:
        X, y = _generate_synthetic(n_samples, seed=random_state)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state
        )

        self.scaler = StandardScaler().fit(X_train)
        X_train_s = self.scaler.transform(X_train)
        X_test_s = self.scaler.transform(X_test)

        self.model = MLPRegressor(
            hidden_layer_sizes=(32, 16),
            activation="relu",
            solver="adam",
            learning_rate_init=0.001,
            max_iter=300,
            early_stopping=True,
            validation_fraction=0.15,
            n_iter_no_change=15,
            random_state=random_state,
        )
        self.model.fit(X_train_s, y_train)

        preds = np.clip(self.model.predict(X_test_s), 0.0, 1.0)
        mae = float(np.mean(np.abs(preds - y_test)))
        mse = float(np.mean((preds - y_test) ** 2))
        return {"test_mae": mae, "test_mse": mse, "n_train": len(X_train)}

    def save(self, model_path: str = MODEL_PATH,
             scaler_path: str = SCALER_PATH, meta_path: str = META_PATH) -> None:
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        with open(meta_path, "w") as f:
            json.dump({
                "feature_order": [
                    "available_time_min", "sessions_per_week", "prev_completion_rate",
                    *[f"intensity_{v}" for v in INTENSITY_VOCAB],
                    *[f"goal_{v}" for v in GOAL_VOCAB],
                    *[f"level_{v}" for v in LEVEL_VOCAB],
                ],
            }, f, indent=2)

    def load(self, model_path: str = MODEL_PATH,
             scaler_path: str = SCALER_PATH) -> None:
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

    def load_or_train(self) -> Optional[dict]:
        """Load saved artifacts; if missing, train + save and return metrics."""
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            self.load()
            return None
        metrics = self.train()
        self.save()
        return metrics

    def predict_adherence(self, user: dict, plan_workouts: Optional[List[dict]] = None,
                          prev_completion_rate: Optional[float] = None) -> float:
        if self.model is None or self.scaler is None:
            self.load_or_train()

        if prev_completion_rate is None:
            prev_completion_rate = _history_to_completion_rate(user.get("workout_history"))

        features = _extract_features(user, plan_workouts or [], prev_completion_rate)
        X = self.scaler.transform(np.array([features], dtype=np.float32))
        p = float(self.model.predict(X)[0])
        return float(np.clip(p, 0.0, 1.0))


if __name__ == "__main__":
    ap = AdherencePredictor()
    metrics = ap.train()
    ap.save()
    print(f"Training done -- {metrics}")

    user = {"available_days": ["Monday", "Wednesday", "Friday"],
            "goal": "Lose Weight", "level": "Beginner",
            "workout_history": []}
    plan = [
        {"duration_minutes": 30, "intensity": "low"},
        {"duration_minutes": 30, "intensity": "medium"},
        {"duration_minutes": 25, "intensity": "medium"},
    ]
    print(f"Sample adherence: {ap.predict_adherence(user, plan):.2%}")
