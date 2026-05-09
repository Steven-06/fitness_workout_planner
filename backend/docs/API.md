API: Canonical User and Plan Input

This document defines the canonical shapes and how data flows through the system so planners and predictors always receive the same format.

1) Creating a user (client -> server)

POST /users
Request body (JSON):
{
  "name": "Alice",
  "available_days": ["Monday", "Wednesday", "Friday"],
  "goal": "Lose Weight",          # one of: "Lose Weight", "Build Muscle", "Improve Endurance", "General Fitness"
  "level": "Beginner",           # optional, default "Beginner"
  "workout_history": []            # optional; list of {adherence_probability, difficulty_score}
}

Response:
{
  "user_id": "<mongo_object_id_string>",
  "message": "User created"
}

Note: The service stores the user as a document and returns a `user_id` (string representation of Mongo `_id`). All plan/predict endpoints expect this `user_id`.

2) Plan / prediction endpoints (client -> server)

- Generate rule-based plan
POST /plan/rule-based
Request body (JSON):
{
  "user_id": "<mongo_id_string>"
}

- Generate CSP plan
POST /plan/csp
Request body (JSON):
{
  "user_id": "<mongo_id_string>"
}

- Compare plans
POST /plan/compare
Request body (JSON):
{
  "user_id": "<mongo_id_string>"
}

- Predict adherence
POST /predict/adherence
Request body (JSON):
{
  "user_id": "<mongo_id_string>",
  "plan_id": "<stored_plan_id_or_null>"  # optional: specify a stored plan to evaluate
}

- Adapt a plan
POST /plan/adapt
Request body (JSON):
{
  "plan_id": "<stored_plan_id>",
  "missed_day": "Wednesday",
  "user_id": "<mongo_id_string>"
}

3) Internal format (what planners and predictors receive)

- `user` (dict):
  - `name`: str
  - `available_days`: list[str]
  - `goal`: str (one of the recognized goals)
  - `level`: str ("Beginner"|"Intermediate")
  - `workout_history`: list[ {"adherence_probability": float, "difficulty_score": float} ]

- `plan_workouts` (list[dict]) passed into the predictor:
  - Each entry: { "duration_minutes": int, "intensity": "low"|"medium"|"high" }

The system converts stored plans into the `plan_workouts` list internally by looking up workouts and extracting `duration_minutes` and `intensity`.

4) Summary / Rules
- Clients create or fetch a user document and then always pass `user_id` (string) to plan/prediction endpoints.
- The server resolves `user_id` to a `user` dict and passes that dict to planners and predictors.
- All stored records keep a `user_id` string field (no `id` on the `User` Pydantic model).

Examples (curl)

Create user:
```
curl -X POST http://localhost:8000/users -H "Content-Type: application/json" -d '{"name":"Alice","available_days":["Mon","Wed","Fri"],"goal":"Lose Weight"}'
```

Generate plan:
```
curl -X POST http://localhost:8000/plan/rule-based -H "Content-Type: application/json" -d '{"user_id":"<mongo_id>"}'
```
